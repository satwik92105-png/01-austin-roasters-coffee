from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union
from datetime import datetime

class MenuItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: Optional[Union[int, str]] = None
    name: str = Field(..., min_length=2, max_length=120)
    category: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., gt=0, le=500)
    description: Optional[str] = Field("", max_length=1000)
    badge: Optional[str] = Field(None, max_length=50)
    in_stock: Optional[bool] = None
    inStock: Optional[bool] = None
    image: Optional[str] = Field(None, max_length=500)
    customizable: Optional[bool] = False

class MenuItemCreate(MenuItemBase):
    pass

class StockUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    in_stock: Optional[bool] = None
    inStock: Optional[bool] = None

class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    description: str = ""
    badge: Optional[str] = None
    in_stock: bool = True
    inStock: bool = True
    image: Optional[str] = None
    customizable: bool = False

class OrderItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Optional[Union[int, str]] = None
    name: str = Field(..., min_length=1, max_length=120)
    qty: int = Field(1, ge=1, le=50)
    price: float = Field(0.0, ge=0, le=500)
    customizations: Optional[str] = Field(None, max_length=300)

class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customerName: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field("(512) 540-6033", max_length=50)
    email: Optional[str] = Field(None, max_length=120)
    items: List[OrderItem] = Field(default_factory=list)
    subtotal: float = Field(0.0, ge=0, le=10000)
    notes: Optional[str] = Field(None, max_length=500)
    paidOnline: Optional[bool] = False

class ReservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    phone: str = Field(..., min_length=7, max_length=50)
    partySize: Optional[int] = Field(None, ge=1, le=50)
    party_size: Optional[int] = Field(None, ge=1, le=50)
    date: Optional[str] = Field(None, max_length=50)
    res_date: Optional[str] = Field(None, max_length=50)
    time: Optional[str] = Field(None, max_length=50)
    res_time: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field("", max_length=500)

class InquiryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    subject: Optional[str] = Field("General Inquiry", max_length=200)
    message: str = Field(..., min_length=2, max_length=2000)

class SubscriberCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roast: str = Field(..., min_length=2, max_length=100)
    grind: str = Field(..., min_length=2, max_length=100)
    frequency: str = Field(..., min_length=2, max_length=100)
    monthlyPrice: float = Field(..., gt=0, le=1000)
    customerName: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=120)

class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    role: str

class EmailNotificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., min_length=5, max_length=120)
    subject: str = Field(..., min_length=1, max_length=200)
    details: Optional[dict] = Field(default_factory=dict)

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[str] = None
    timestamp_utc: datetime
