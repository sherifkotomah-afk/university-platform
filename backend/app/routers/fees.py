"""
Fees / invoices / payments.

Flow:
1. Admin/finance configures FeeItems for an academic year (itemized levies).
2. Admin/finance (or an automated job) generates a StudentFeeInvoice for a
   student for a given semester, pulling in all active, applicable fee
   items as InvoiceLineItems (respecting opt-outs where eligible).
3. Student initiates payment on an invoice (full or partial amount) ->
   we call Paystack to initialize a transaction -> return the
   authorization_url for the frontend to redirect the student to.
4. After payment, the frontend calls /payments/verify with the reference.
   We verify server-side with Paystack (never trust the client alone),
   then update the Payment + Invoice records accordingly.
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.students import Student
from app.models.fees import FeeItem, StudentFeeInvoice, InvoiceLineItem, Payment
from app.schemas.fees import (
    FeeItemOut, CreateFeeItemRequest, InvoiceOut, GenerateInvoiceRequest, InitiatePaymentRequest,
    InitiatePaymentResponse, VerifyPaymentRequest, PaymentOut
)
from app.core.deps import get_current_user, require_role
from app.core.paystack import initialize_transaction, verify_transaction, verify_webhook_signature, PaystackError

router = APIRouter(prefix="/fees", tags=["fees"])


# ---------------- Fee item configuration (admin/finance) ----------------

@router.get("/items", response_model=List[FeeItemOut])
def list_fee_items(academic_year: str = None, db: Session = Depends(get_db)):
    """Public-readable: applicants/students should be able to see what fees exist."""
    query = db.query(FeeItem).filter(FeeItem.active == True)  # noqa: E712
    if academic_year:
        query = query.filter(FeeItem.academic_year == academic_year)
    return query.all()


@router.post("/items", response_model=FeeItemOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "finance"))])
def create_fee_item(payload: CreateFeeItemRequest, db: Session = Depends(get_db)):
    fee_item = FeeItem(
        academic_year=payload.academic_year,
        programme_level=payload.programme_level,
        name=payload.name,
        amount=payload.amount,
        is_mandatory=payload.is_mandatory,
        opt_out_eligible=payload.opt_out_eligible,
        one_time_only=payload.one_time_only,
        gtec_approved=payload.gtec_approved,
    )
    db.add(fee_item)
    db.commit()
    db.refresh(fee_item)
    return fee_item


# ---------------- Invoice generation (admin/finance) ----------------

@router.post("/invoices", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "finance"))])
def generate_invoice(payload: GenerateInvoiceRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    applicable_items = (
        db.query(FeeItem)
        .filter(FeeItem.academic_year == payload.academic_year, FeeItem.active == True)  # noqa: E712
        .all()
    )
    if not applicable_items:
        raise HTTPException(status_code=400, detail="No fee items configured for this academic year yet.")

    opted_out_ids = set(payload.opted_out_fee_item_ids or [])
    total = 0.0
    line_items = []
    for item in applicable_items:
        opted_out = item.id in opted_out_ids and item.opt_out_eligible
        amount = 0.0 if opted_out else float(item.amount)
        total += amount
        line_items.append(InvoiceLineItem(fee_item_id=item.id, amount=amount, opted_out=opted_out))

    invoice = StudentFeeInvoice(
        student_id=student.id,
        academic_year=payload.academic_year,
        semester=payload.semester,
        total_amount=total,
        amount_paid=0,
        status="Unpaid",
        due_date=payload.due_date,
        created_at=datetime.now(timezone.utc),
    )
    db.add(invoice)
    db.flush()  # get invoice.id before attaching line items

    for li in line_items:
        li.invoice_id = invoice.id
        db.add(li)

    db.commit()
    db.refresh(invoice)
    return invoice


# ---------------- Student-facing: view + pay invoices ----------------

def _get_student_or_403(db: Session, current_user: User) -> Student:
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=403, detail="No student record associated with this account.")
    return student


@router.get("/invoices/mine", response_model=List[InvoiceOut])
def my_invoices(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    return (
        db.query(StudentFeeInvoice)
        .options(joinedload(StudentFeeInvoice.line_items).joinedload(InvoiceLineItem.fee_item))
        .filter(StudentFeeInvoice.student_id == student.id)
        .order_by(StudentFeeInvoice.academic_year.desc(), StudentFeeInvoice.semester.desc())
        .all()
    )


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = (
        db.query(StudentFeeInvoice)
        .options(joinedload(StudentFeeInvoice.line_items).joinedload(InvoiceLineItem.fee_item))
        .filter(StudentFeeInvoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    student = db.query(Student).filter(Student.id == invoice.student_id).first()
    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this invoice.")
    return invoice


@router.post("/payments/initiate", response_model=InitiatePaymentResponse)
def initiate_payment(
    payload: InitiatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)
    invoice = db.query(StudentFeeInvoice).filter(StudentFeeInvoice.id == payload.invoice_id).first()
    if not invoice or invoice.student_id != student.id:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    remaining = float(invoice.total_amount) - float(invoice.amount_paid)
    if payload.amount <= 0 or payload.amount > remaining + 0.01:
        raise HTTPException(status_code=400, detail=f"Amount must be between 0 and the remaining balance (GHS {remaining:.2f}).")

    reference = f"INV{invoice.id}-{uuid.uuid4().hex[:10]}"

    payment = Payment(
        invoice_id=invoice.id,
        amount=payload.amount,
        payment_method="Card/Mobile Money",  # Paystack itself determines the exact channel used
        provider_reference=reference,
        status="Pending",
    )
    db.add(payment)
    db.commit()

    try:
        result = initialize_transaction(email=current_user.email, amount_ghs=payload.amount, reference=reference)
    except PaystackError as e:
        payment.status = "Failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Payment initialization failed: {e}")

    return InitiatePaymentResponse(
        authorization_url=result["authorization_url"],
        access_code=result["access_code"],
        reference=result["reference"],
    )


@router.post("/payments/verify", response_model=PaymentOut)
def verify_payment(payload: VerifyPaymentRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.provider_reference == payload.reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found.")

    try:
        result = verify_transaction(payload.reference)
    except PaystackError as e:
        raise HTTPException(status_code=502, detail=f"Could not verify payment with Paystack: {e}")

    paystack_amount_ghs = result.get("amount", 0) / 100  # convert pesewas back to cedis

    if result.get("status") == "success" and abs(paystack_amount_ghs - float(payment.amount)) < 0.01:
        payment.status = "Successful"
        payment.paid_at = datetime.now(timezone.utc)

        invoice = db.query(StudentFeeInvoice).filter(StudentFeeInvoice.id == payment.invoice_id).first()
        invoice.amount_paid = float(invoice.amount_paid) + float(payment.amount)
        if invoice.amount_paid >= float(invoice.total_amount) - 0.01:
            invoice.status = "Paid"
        else:
            invoice.status = "Partially Paid"
    else:
        payment.status = "Failed"

    db.commit()
    db.refresh(payment)
    return payment


@router.post("/payments/webhook", include_in_schema=False)
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Backup confirmation path. If a student closes their browser tab right
    after paying — before the redirect-and-verify flow in the frontend
    completes — this webhook is what still marks the payment successful.
    Paystack calls this URL directly from their servers whenever a
    transaction's status changes, regardless of what the student's browser
    does. Configure this URL in Paystack Dashboard -> Settings -> API Keys
    & Webhooks -> Webhook URL, as: https://your-render-url/fees/payments/webhook
    """
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    if not verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        data = payload.get("data", {})
        reference = data.get("reference")
        amount_ghs = data.get("amount", 0) / 100

        payment = db.query(Payment).filter(Payment.provider_reference == reference).first()
        if payment and payment.status != "Successful":
            payment.status = "Successful"
            payment.paid_at = datetime.now(timezone.utc)

            invoice = db.query(StudentFeeInvoice).filter(StudentFeeInvoice.id == payment.invoice_id).first()
            if invoice:
                invoice.amount_paid = float(invoice.amount_paid) + float(amount_ghs)
                if invoice.amount_paid >= float(invoice.total_amount) - 0.01:
                    invoice.status = "Paid"
                else:
                    invoice.status = "Partially Paid"
            db.commit()

    return {"received": True}
