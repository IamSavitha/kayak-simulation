"""
Billing Service - FastAPI application for payment and billing management.
"""
import logging
import calendar
from datetime import datetime, date as date_type, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, Query, status, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.billing_schemas import (
    PaymentRequest,
    BillingResponse,
    BillingSearchParams,
    BillingListResponse,
    RefundRequest,
)
from ...models.mysql_models import Billing, PaymentStatus
from .service import BillingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kayak Billing Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Legacy request models to match the original Billing API PDF
# -------------------------------------------------------------------


class LegacyPaymentDetails(BaseModel):
    cardNumber: Optional[str] = None
    cvv: Optional[str] = None
    expiryMonth: Optional[str] = None
    expiryYear: Optional[str] = None
    paypalEmail: Optional[str] = None


class LegacyPaymentInfo(BaseModel):
    method: str  # "CREDIT_CARD" | "PAYPAL"
    details: LegacyPaymentDetails


class LegacyBillingCreateRequest(BaseModel):
    userId: str
    bookingType: str  # "HOTEL" | "FLIGHT" | "CAR"
    bookingId: str
    totalAmount: float
    currency: str
    payment: LegacyPaymentInfo


class AdminStatusUpdateRequest(BaseModel):
    status: str  # pending | completed | failed | refunded


def require_admin(x_admin: Optional[str] = Header(default=None)):
    """
    Simple admin check to match PDF requirement of x-admin: true header
    for /admin/billing/* endpoints.
    """
    if x_admin is None or str(x_admin).lower() != "true":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


# -------------------------------------------------------------------
# Startup & health
# -------------------------------------------------------------------


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Billing Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "billing-service"}


# -------------------------------------------------------------------
# Core (new) billing endpoints used by kayak-simulation
# -------------------------------------------------------------------


@app.post("/payments", response_model=BillingResponse)
async def process_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_mysql_session),
):
    """Process a payment for a booking."""
    service = BillingService(db)
    try:
        billing = service.process_payment(payment)
        return billing
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/billings/{billing_id}", response_model=BillingResponse)
async def get_billing(billing_id: str, db: Session = Depends(get_mysql_session)):
    """Get billing record by ID."""
    billing = BillingService(db).get_billing(billing_id)
    if not billing:
        handle_not_found("Billing", billing_id)
    return billing


@app.get("/billings", response_model=BillingListResponse)
async def search_billings(
    user_id: Optional[str] = None,
    booking_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session),
):
    """Search billing records."""
    params = BillingSearchParams(
        user_id=user_id,
        booking_type=booking_type,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return BillingService(db).search_billings(params)


@app.post("/billings/{billing_id}/refund")
async def process_refund(
    billing_id: str,
    refund: RefundRequest,
    db: Session = Depends(get_mysql_session),
):
    """Process a refund."""
    return BillingService(db).process_refund(billing_id, refund)


@app.get("/billings/{billing_id}/invoice")
async def get_invoice(billing_id: str, db: Session = Depends(get_mysql_session)):
    """Get invoice details."""
    return BillingService(db).generate_invoice(billing_id)


# -------------------------------------------------------------------
# Legacy public endpoints to match Billing API PDF
# -------------------------------------------------------------------


@app.post("/billing", response_model=BillingResponse, tags=["legacy-billing"])
async def create_billing_legacy(
    body: LegacyBillingCreateRequest,
    db: Session = Depends(get_mysql_session),
):
    """
    Legacy endpoint matching the original PDF:

    POST /billing
    {
      "userId": "123-45-6789",
      "bookingType": "HOTEL",
      "bookingId": 123,
      "totalAmount": 350.0,
      "currency": "USD",
      "payment": {
        "method": "CREDIT_CARD" | "PAYPAL",
        "details": { ... }
      }
    }
    """
    method = body.payment.method.upper()
    if method not in ("CREDIT_CARD", "PAYPAL"):
        raise HTTPException(status_code=400, detail="Invalid payment method")

    payment_method = "credit_card" if method == "CREDIT_CARD" else "paypal"

    details = body.payment.details
    card_expiry = None
    if details.expiryMonth and details.expiryYear:
        year_two = details.expiryYear[-2:]
        card_expiry = f"{details.expiryMonth}/{year_two}"

    payment_req = PaymentRequest(
        booking_id=str(body.bookingId),
        payment_method=payment_method,
        card_number=details.cardNumber,
        card_expiry=card_expiry,
        card_cvv=details.cvv,
        cardholder_name=None,
        paypal_email=details.paypalEmail,
    )

    service = BillingService(db)
    billing = service.process_payment(payment_req)

    if isinstance(billing, dict):
        return BillingResponse(**billing)
    return billing


@app.get("/billing/{billing_id}", response_model=BillingResponse, tags=["legacy-billing"])
async def get_billing_legacy(
    billing_id: str,
    db: Session = Depends(get_mysql_session),
):
    """
    Legacy GET /billing/:billingId from the PDF.
    """
    service = BillingService(db)
    billing = service.get_billing(billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")
    if isinstance(billing, dict):
        return BillingResponse(**billing)
    return billing


@app.get(
    "/billing/user/{user_id}",
    response_model=BillingListResponse,
    tags=["legacy-billing"],
)
async def get_billing_for_user_legacy(
    user_id: str,
    db: Session = Depends(get_mysql_session),
):
    """
    Legacy GET /billing/user/:userId from the PDF.
    """
    service = BillingService(db)
    params = BillingSearchParams(user_id=user_id)
    result = service.search_billings(params)
    if isinstance(result, dict):
        return BillingListResponse(**result)
    return result


@app.get("/billing/{billing_id}/invoice", tags=["legacy-billing"])
async def get_invoice_legacy(
    billing_id: str,
    db: Session = Depends(get_mysql_session),
):
    """
    Legacy GET /billing/:billingId/invoice from the PDF.
    """
    service = BillingService(db)
    invoice = service.generate_invoice(billing_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


# -------------------------------------------------------------------
# Admin endpoints to match Billing API PDF (/admin/billing/*)
# -------------------------------------------------------------------


@app.get(
    "/admin/billing/by-date",
    response_model=BillingListResponse,
    tags=["admin-billing"],
)
async def admin_billing_by_date(
    date: date_type = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: GET /admin/billing/by-date?date=YYYY-MM-DD
    Returns billings for a specific calendar date.
    """
    start = datetime.combine(date, datetime.min.time())
    end = datetime.combine(date, datetime.max.time())

    params = BillingSearchParams(
        start_date=start,
        end_date=end,
        page=1,
        page_size=1000,
    )
    return BillingService(db).search_billings(params)


@app.get(
    "/admin/billing/by-month",
    response_model=BillingListResponse,
    tags=["admin-billing"],
)
async def admin_billing_by_month(
    year: int = Query(..., ge=2000),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: GET /admin/billing/by-month?year=YYYY&month=MM
    Returns billings for a specific month.
    """
    start = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    end = next_month - timedelta(microseconds=1)

    params = BillingSearchParams(
        start_date=start,
        end_date=end,
        page=1,
        page_size=1000,
    )
    return BillingService(db).search_billings(params)


@app.get(
    "/admin/billing/by-user",
    response_model=BillingListResponse,
    tags=["admin-billing"],
)
async def admin_billing_by_user(
    userId: str = Query(..., description="User ID (from users.user_id)"),
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: GET /admin/billing/by-user?userId=...
    Returns billings for a specific user.
    """
    params = BillingSearchParams(user_id=userId, page=1, page_size=1000)
    return BillingService(db).search_billings(params)


@app.get(
    "/admin/billing/{billing_id}",
    response_model=BillingResponse,
    tags=["admin-billing"],
)
async def admin_get_billing(
    billing_id: str,
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: GET /admin/billing/{billingId}
    """
    billing = BillingService(db).get_billing(billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")
    if isinstance(billing, dict):
        return BillingResponse(**billing)
    return billing


@app.put(
    "/admin/billing/{billing_id}/status",
    response_model=BillingResponse,
    tags=["admin-billing"],
)
async def admin_update_billing_status(
    billing_id: str,
    body: AdminStatusUpdateRequest,
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: PUT /admin/billing/{billingId}/status
    Body: { "status": "pending" | "completed" | "failed" | "refunded" }
    """
    billing = db.query(Billing).filter(Billing.billing_id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")

    status_str = body.status.lower()
    try:
        new_status = PaymentStatus(status_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    billing.payment_status = new_status
    db.commit()
    db.refresh(billing)

    return BillingResponse.model_validate(billing)


@app.get(
    "/admin/billing/revenue-summary",
    tags=["admin-billing"],
)
async def admin_revenue_summary(
    year: int = Query(..., ge=2000),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_mysql_session),
    _: None = Depends(require_admin),
):
    """
    Admin: GET /admin/billing/revenue-summary?year=YYYY&month=MM
    Returns a simple aggregated revenue summary for the given month.
    """
    start = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    end = next_month - timedelta(microseconds=1)

    params = BillingSearchParams(
        start_date=start,
        end_date=end,
        page=1,
        page_size=10000,
    )
    result = BillingService(db).search_billings(params)

    # BillingListResponse.total_amount is a Decimal
    return {
        "year": year,
        "month": month,
        "totalRevenue": float(result.total_amount),
        "totalCount": result.total_count,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
