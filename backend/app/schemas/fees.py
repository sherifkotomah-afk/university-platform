from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class FeeItemOut(BaseModel):
    id: int
    name: str
    amount: float
    is_mandatory: bool
    opt_out_eligible: bool
    one_time_only: bool
    gtec_approved: bool

    class Config:
        from_attributes = True


class CreateFeeItemRequest(BaseModel):
    academic_year: str
    programme_level: Optional[str] = None
    name: str
    amount: float
    is_mandatory: bool = True
    opt_out_eligible: bool = False
    one_time_only: bool = False
    gtec_approved: bool = False


class InvoiceLineItemOut(BaseModel):
    id: int
    fee_item_id: int
    amount: float
    opted_out: bool
    fee_item: Optional[FeeItemOut] = None

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    academic_year: str
    semester: int
    total_amount: float
    amount_paid: float
    status: str
    due_date: Optional[date] = None
    line_items: List[InvoiceLineItemOut] = []

    class Config:
        from_attributes = True


class GenerateInvoiceRequest(BaseModel):
    student_id: int
    academic_year: str
    semester: int
    due_date: Optional[date] = None
    opted_out_fee_item_ids: Optional[List[int]] = None  # levies the student is opting out of, where eligible


class InitiatePaymentRequest(BaseModel):
    invoice_id: int
    amount: float  # allows partial/installment payments


class InitiatePaymentResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class VerifyPaymentRequest(BaseModel):
    reference: str


class PaymentOut(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_method: Optional[str]
    provider_reference: Optional[str]
    status: str
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True
