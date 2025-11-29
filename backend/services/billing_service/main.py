from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import BillingDB

app = FastAPI(title="Billing Service", version="2.0")

db = BillingDB()


# ==========================================================
# --------------------- MODELS -----------------------------
# ==========================================================

class PaymentRequest(BaseModel):
    booking_id: str
    payment_method: str  # "credit_card" or "paypal"
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    paypal_email: Optional[str] = None


class BillingResponse(BaseModel):
    billing_id: str
    booking_id: str
    amount: float
    payment_method: str
    payment_status: str
    transaction_date: datetime


class BillingListResponse(BaseModel):
    total_count: int
    total_amount: float
    billings: List[BillingResponse]


class RefundRequest(BaseModel):
    reason: str


# ==========================================================
# --------------------- ROUTES ------------------------------
# ==========================================================


# --------------------- 1. Create Payment -------------------
@app.post("/payments", response_model=BillingResponse)
def create_payment(req: PaymentRequest):
    """
    Creates a billing entry when a user pays for a booking.
    Frontend: PaymentForm.jsx → createPayment()
    """
    if req.payment_method not in ["credit_card", "paypal"]:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    billing = db.create_billing_entry(
        booking_id=req.booking_id,
        payment_method=req.payment_method,
        amount=db.get_booking_amount(req.booking_id),
        card_number=req.card_number,
        card_expiry=req.card_expiry,
        card_cvv=req.card_cvv,
        paypal_email=req.paypal_email,
    )

    return BillingResponse(**billing)


# --------------------- 2. Get Billing by ID ----------------
@app.get("/billings/{billing_id}", response_model=BillingResponse)
def get_billing_by_id(billing_id: str):
    """
    Retrieve a single billing record.
    Used by: PaymentConfirmation, InvoiceViewer
    """
    billing = db.get_billing(billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    return BillingResponse(**billing)


# --------------------- 3. List/Search Billings -------------
@app.get("/billings", response_model=BillingListResponse)
def search_billings(
    user_id: Optional[str] = Query(None),
    booking_id: Optional[str] = Query(None),
    limit: int = 100,
):
    """
    Returns all billing records or filters by user/booking.
    Used by: BillingHistory component
    """
    result = db.search_billings(user_id=user_id, booking_id=booking_id, limit=limit)
    return BillingListResponse(**result)


# --------------------- 4. Refund Billing -------------------
@app.post("/billings/{billing_id}/refund")
def refund_billing(billing_id: str, req: RefundRequest):
    """
    Marks a billing entry as refunded.
    """
    success = db.refund_billing(billing_id, req.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Refund failed")

    return {"status": "REFUNDED", "billing_id": billing_id}


# --------------------- 5. Generate Invoice -----------------
@app.get("/billings/{billing_id}/invoice")
def generate_invoice(billing_id: str):
    """
    Returns invoice data (not a PDF).
    Used by: InvoiceViewer.jsx
    """
    invoice = db.generate_invoice(billing_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


# --------------------- 6. Health Check ---------------------
@app.get("/health")
def health():
    return {"status": "billing service OK"}
