from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Date, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base


class FeeItem(Base):
    """
    A single configurable levy/fee line (e.g. 'SRC Dues', 'Academic Facility
    User Fee', 'GRASAG Development Levy'). Editable per academic year by
    admin/finance — nothing here is hardcoded, since GTEC-approved amounts
    change yearly.
    """
    __tablename__ = "fee_items"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(9), nullable=False)
    programme_level = Column(String(20))
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    opt_out_eligible = Column(Boolean, default=False)
    one_time_only = Column(Boolean, default=False)
    gtec_approved = Column(Boolean, default=False)
    active = Column(Boolean, default=True)


class StudentFeeInvoice(Base):
    __tablename__ = "student_fee_invoices"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    academic_year = Column(String(9), nullable=False)
    semester = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    amount_paid = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="Unpaid")  # Unpaid, Partially Paid, Paid, Overdue
    due_date = Column(Date)
    created_at = Column(TIMESTAMP)

    line_items = relationship("InvoiceLineItem", back_populates="invoice")


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("student_fee_invoices.id", ondelete="CASCADE"))
    fee_item_id = Column(Integer, ForeignKey("fee_items.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    opted_out = Column(Boolean, default=False)

    invoice = relationship("StudentFeeInvoice", back_populates="line_items")
    fee_item = relationship("FeeItem")


class Payment(Base):
    """
    Records a payment attempt/result. provider_reference stores Paystack's
    transaction reference so it can be verified server-side via Paystack's
    /transaction/verify/:reference endpoint before marking Successful.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("student_fee_invoices.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(30))  # Mobile Money, Card, Bank Transfer
    provider_reference = Column(String(100))
    status = Column(String(20), default="Pending")  # Pending, Successful, Failed, Refunded
    paid_at = Column(TIMESTAMP)


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("student_fee_invoices.id"))
    installment_number = Column(Integer, nullable=False)
    amount_due = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    paid = Column(Boolean, default=False)


class ScholarshipFinancialAid(Base):
    __tablename__ = "scholarships_financial_aid"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    aid_type = Column(String(50))  # Scholarship, Bursary, Loan, Fee Waiver
    amount = Column(Numeric(10, 2))
    coverage_percent = Column(Numeric(5, 2))
    academic_year = Column(String(9))
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected, Disbursed
