from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from datetime import datetime
from database import Base

class MenuItemModel(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    badge = Column(String(50), nullable=True)
    in_stock = Column(Boolean, default=True, index=True)
    image = Column(String(500), nullable=True)
    customizable = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    items_json = Column(Text, nullable=False)
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(50), default="New Order", index=True)
    order_time = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)

class ReservationModel(Base):
    __tablename__ = "reservations"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    party_size = Column(Integer, default=2)
    date = Column(String(50), nullable=False, index=True)
    time = Column(String(50), nullable=False)
    status = Column(String(50), default="Confirmed", index=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)

class InquiryModel(Base):
    __tablename__ = "inquiries"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    subject = Column(String(200), default="General Inquiry")
    message = Column(Text, nullable=False)
    date = Column(String(50), nullable=False)

class SubscriberModel(Base):
    __tablename__ = "subscribers"

    id = Column(String(50), primary_key=True, index=True)
    roast = Column(String(100), nullable=False)
    grind = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    monthly_price = Column(Float, nullable=False)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(String(50), default="admin", index=True)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(100), default="anonymous", index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp_utc = Column(DateTime, default=datetime.utcnow, index=True)

class IdempotencyRecordModel(Base):
    __tablename__ = "idempotency_records"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    path = Column(String(100), nullable=False)
    status_code = Column(Integer, default=200)
    response_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
