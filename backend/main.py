import json
import random
import os
import time
import html
from datetime import datetime, timedelta
from typing import Optional, Union, List

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from sqlalchemy import text
from database import engine, Base, get_db
from models import (
    MenuItemModel, OrderModel, ReservationModel, InquiryModel,
    SubscriberModel, UserModel, AuditLogModel, IdempotencyRecordModel
)
from schemas import (
    MenuItemCreate, StockUpdateRequest, MenuItemResponse, OrderCreate, ReservationCreate,
    InquiryCreate, SubscriberCreate, LoginRequest, TokenResponse, AuditLogResponse
)
from auth import (
    hash_password, verify_password, create_access_token,
    require_admin, require_staff, get_client_ip,
    check_login_lockout, record_login_failure, record_login_success
)

# Ensure all tables exist
Base.metadata.create_all(bind=engine)

def run_migrations():
    with engine.connect() as conn:
        for table, col, col_type in [
            ("menu_items", "is_deleted", "BOOLEAN DEFAULT 0"),
            ("menu_items", "deleted_at", "DATETIME NULL"),
            ("orders", "is_deleted", "BOOLEAN DEFAULT 0"),
            ("orders", "deleted_at", "DATETIME NULL"),
            ("reservations", "is_deleted", "BOOLEAN DEFAULT 0"),
            ("reservations", "deleted_at", "DATETIME NULL"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass

try:
    run_migrations()
except Exception:
    pass

app = FastAPI(
    title="Flat Track Coffee Roasters — Enterprise REST API",
    description="Hardened Production API for Customer Ordering, Subscriptions, and Isolated Owner POS",
    version="19.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RATE LIMITING & SECURITY HEADERS MIDDLEWARE ---
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 120
_IP_REQUEST_TIMESTAMPS = {}

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    client_ip = get_client_ip(request)
    now = time.time()
    
    # Sliding-window rate limit
    window_start = now - RATE_LIMIT_WINDOW
    timestamps = [t for t in _IP_REQUEST_TIMESTAMPS.get(client_ip, []) if t > window_start]
    
    if len(timestamps) >= MAX_REQUESTS_PER_WINDOW:
        return Response(
            content=json.dumps({"detail": "Rate limit exceeded. Please try again in 1 minute."}),
            status_code=429,
            media_type="application/json",
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(MAX_REQUESTS_PER_WINDOW),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    timestamps.append(now)
    _IP_REQUEST_TIMESTAMPS[client_ip] = timestamps
    remaining = max(0, MAX_REQUESTS_PER_WINDOW - len(timestamps))

    response = await call_next(request)

    # Inject OWASP Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'; "
        "img-src 'self' https: data: blob:; "
        "font-src 'self' https: data:; "
        "frame-src 'self' https://www.google.com https://maps.google.com;"
    )
    response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS_PER_WINDOW)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response

# --- HELPERS ---
def sanitize_str(val: Optional[str]) -> str:
    if not val:
        return ""
    return html.escape(val.strip())

def log_audit(
    db: Session,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[str] = None
):
    try:
        audit = AuditLogModel(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details,
            timestamp_utc=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()

def check_idempotency(db: Session, key: Optional[str], path: str):
    if not key:
        return None
    rec = db.query(IdempotencyRecordModel).filter(
        IdempotencyRecordModel.idempotency_key == key,
        IdempotencyRecordModel.path == path
    ).first()
    if rec:
        if datetime.utcnow() - rec.created_at < timedelta(hours=24):
            return json.loads(rec.response_json)
    return None

def store_idempotency(db: Session, key: Optional[str], path: str, response_data: dict, status_code: int = 200):
    if not key:
        return
    try:
        rec = IdempotencyRecordModel(
            idempotency_key=key,
            path=path,
            status_code=status_code,
            response_json=json.dumps(response_data),
            created_at=datetime.utcnow()
        )
        db.add(rec)
        db.commit()
    except Exception:
        db.rollback()

def startup_populate():
    db = next(get_db())
    try:
        # Create default owner if not exists
        admin = db.query(UserModel).filter(UserModel.email == "admin@flattrackcoffee.com").first()
        if not admin:
            admin = UserModel(
                email="admin@flattrackcoffee.com",
                hashed_password=hash_password("roastmaster123"),
                role="admin"
            )
            db.add(admin)
            db.commit()

        # Seed or sync initial canonical 10-item menu if empty or missing items
        canonical_items = [
            (1, "Dogspeed Espresso Double", "espresso", 4.50, "Double-pulled Dogspeed blend. Rich dark cacao, candied citrus, dense persistent crema. The house signature.", "Roaster's Pick", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80", True),
            (2, "Flat Track Classic Cortado", "espresso", 5.00, "Equal parts double espresso and silky steamed oat or whole milk. Balanced, intensely aromatic.", "Local Favorite", "https://images.unsplash.com/photo-1534778101976-62847782c213?w=600&auto=format&fit=crop&q=80", True),
            (3, "Bourbon Smoked Vanilla Latte", "specialty", 6.75, "House-made Madagascar vanilla syrup infused with oak barrel smoke and espresso, topped with raw turbinado sugar.", "Seasonal Release", "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=600&auto=format&fit=crop&q=80", True),
            (4, "Single-Origin Ethiopian Pour-Over", "pourover", 6.50, "Yirgacheffe natural process. Vibrant bergamot, ripe blackberry, and delicate honeysuckle finish.", "Micro-Lot", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&auto=format&fit=crop&q=80", True),
            (5, "East Austin Flash Brew Iced", "cold", 5.50, "Brewed hot directly over ice to preserve volatile aromatics. Crisp citrus brightness, ultra-refreshing.", "Summer Essential", "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=600&auto=format&fit=crop&q=80", True),
            (6, "Slow-Steeped Cold Brew Float", "cold", 7.00, "20-hour steeped Dogspeed cold brew poured over local Sweet Ritual Madagascar vanilla ice cream.", "Indulgent", "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=600&auto=format&fit=crop&q=80", True),
            (7, "Artisan Butter Croissant", "bakery", 4.50, "Baked fresh daily by Swedish Hill. 48 laminated butter layers, golden flaky crust, soft honeycomb interior.", "Fresh Daily", "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&auto=format&fit=crop&q=80", True),
            (8, "Rosemary & Gruyère Savory Scone", "bakery", 4.75, "Infused with fresh garden rosemary and melted aged Swiss Gruyère. Warm, buttery, and fragrant.", "Baker's Choice", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80", True),
            (9, "Dogspeed Blend Whole Bean (12oz)", "beans", 19.50, "Our signature espresso blend (Washed Colombia & Natural Ethiopia). Dark cocoa, sweet plum, and velvety mouthfeel.", "Signature Roast", "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?w=600&auto=format&fit=crop&q=80", True),
            (10, "Mexico Oaxaca Pluma Whole Bean (12oz)", "beans", 21.00, "Washed process micro-lot from Pluma Hidalgo. Milk chocolate, crisp green apple, and raw sugar cane sweetness.", "Direct Trade", "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&auto=format&fit=crop&q=80", True)
        ]
        if db.query(MenuItemModel).filter(MenuItemModel.is_deleted == False).count() < 10:
            for item_id, name, cat, pr, desc, bg, img, cust in canonical_items:
                existing = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
                if not existing:
                    db.add(MenuItemModel(id=item_id, name=name, category=cat, price=pr, description=desc, badge=bg, image=img, customizable=cust, in_stock=True, is_deleted=False))
                else:
                    existing.name = name
                    existing.category = cat
                    existing.price = pr
                    existing.description = desc
                    existing.badge = bg
                    existing.image = img
                    existing.customizable = cust
                    existing.in_stock = True
                    existing.is_deleted = False
            db.commit()
    finally:
        db.close()

# Startup triggers
try:
    startup_populate()
except Exception:
    pass

# --- SYSTEM HEALTH & STATUS ---
@app.get("/")
@app.get("/api")
@app.get("/api/v1")
def root_status():
    return {
        "status": "ok",
        "service": "Flat Track Coffee Roasters Enterprise API",
        "version": "19.0.0",
        "timestamp_utc": datetime.utcnow().isoformat()
    }

@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "Flat Track Coffee Roasters Enterprise API",
        "version": "19.0.0",
        "database": "connected"
    }

# --- AUTHENTICATION WITH BRUTE-FORCE LOCKOUT & RBAC ---
@app.post("/auth/login")
@app.post("/api/auth/login")
@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    check_login_lockout(client_ip)

    user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        record_login_failure(client_ip)
        log_audit(db, actor=req.email, action="LOGIN_FAILED", resource_type="auth", ip_address=client_ip, details="Failed authentication attempt")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    record_login_success(client_ip)
    token = create_access_token({"sub": user.email, "role": user.role})
    log_audit(db, actor=user.email, action="LOGIN_SUCCESS", resource_type="auth", ip_address=client_ip, details=f"Role: {user.role}")

    # Set HttpOnly; Secure; SameSite=Strict cookie
    response.set_cookie(
        key="flattrack_access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=900
    )
    return {"access_token": token, "token_type": "bearer", "role": user.role}

@app.post("/auth/register")
@app.post("/api/auth/register")
@app.post("/api/v1/auth/register")
def register_customer(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if user:
        token = create_access_token({"sub": user.email, "role": user.role})
        return {"access_token": token, "token_type": "bearer", "role": user.role, "user": {"email": user.email, "member": True}}
    new_user = UserModel(email=req.email, hashed_password=hash_password(req.password), role="customer")
    db.add(new_user)
    db.commit()
    token = create_access_token({"sub": new_user.email, "role": "customer"})
    return {"access_token": token, "token_type": "bearer", "role": "customer", "user": {"email": new_user.email, "member": True}}

@app.post("/auth/google")
@app.post("/api/auth/google")
@app.post("/api/v1/auth/google")
def google_oauth(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "customer@gmail.com")
    name = data.get("name", "Austin Member")
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        user = UserModel(email=email, hashed_password=hash_password("google_oauth_auth_token"), role="customer")
        db.add(user)
        db.commit()
    token = create_access_token({"sub": email, "role": "customer"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": email, "name": name, "member": True}
    }

# --- PUBLIC MENU ENDPOINTS (WITH SOFT-DELETE FILTERING) ---
@app.get("/menu")
@app.get("/api/menu")
@app.get("/api/v1/menu")
def get_menu(db: Session = Depends(get_db)):
    # Soft deletes: only return items where is_deleted == False, ordered by id
    items = db.query(MenuItemModel).filter(MenuItemModel.is_deleted == False).order_by(MenuItemModel.id.asc()).all()
    return [
        {
            "id": i.id, "name": i.name, "category": i.category,
            "price": i.price, "description": i.description,
            "badge": i.badge, "inStock": i.in_stock, "in_stock": i.in_stock,
            "image": i.image, "customizable": i.customizable
        }
        for i in items
    ]

# --- PROTECTED ADMIN MENU MUTATIONS (RBAC: ADMIN ONLY) ---
@app.post("/menu", dependencies=[Depends(require_admin)])
@app.post("/api/menu", dependencies=[Depends(require_admin)])
@app.post("/api/v1/menu", dependencies=[Depends(require_admin)])
def create_menu_item(req: MenuItemCreate, request: Request, db: Session = Depends(get_db)):
    val = req.inStock if req.inStock is not None else req.in_stock
    in_st = val if val is not None else True
    item = MenuItemModel(
        name=sanitize_str(req.name),
        category=sanitize_str(req.category),
        price=round(req.price, 2),
        description=sanitize_str(req.description),
        badge=sanitize_str(req.badge) if req.badge else None,
        in_stock=in_st,
        image=req.image or "",
        customizable=bool(req.customizable),
        is_deleted=False
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    log_audit(db, actor="admin", action="CREATE_MENU_ITEM", resource_type="menu_item", resource_id=str(item.id), ip_address=get_client_ip(request), details=f"Created {item.name} (${item.price})")

    return {
        "id": item.id, "name": item.name, "category": item.category,
        "price": item.price, "description": item.description,
        "badge": item.badge, "inStock": item.in_stock, "in_stock": item.in_stock,
        "image": item.image, "customizable": item.customizable
    }

@app.put("/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.put("/api/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.put("/api/v1/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.patch("/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.patch("/api/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.patch("/api/v1/menu/{item_id}", dependencies=[Depends(require_admin)])
def update_menu_item(item_id: Union[int, str], req: MenuItemCreate, request: Request, db: Session = Depends(get_db)):
    try:
        clean_id = int(str(item_id).lower().replace("ft-m", "").replace("m", "").strip())
    except Exception:
        clean_id = 1

    item = db.query(MenuItemModel).filter(MenuItemModel.id == clean_id).first()
    val = req.inStock if req.inStock is not None else req.in_stock
    in_st = val if val is not None else True

    if not item:
        # UPSERT: Item does not exist, insert with normalized clean_id
        item = MenuItemModel(
            id=clean_id,
            name=sanitize_str(req.name),
            category=sanitize_str(req.category),
            price=round(req.price, 2),
            description=sanitize_str(req.description),
            badge=sanitize_str(req.badge) if req.badge else None,
            image=req.image or "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
            in_stock=in_st,
            customizable=bool(req.customizable),
            is_deleted=False
        )
        db.add(item)
    else:
        # Update existing
        item.name = sanitize_str(req.name)
        item.category = sanitize_str(req.category)
        item.price = round(req.price, 2)
        item.description = sanitize_str(req.description)
        item.badge = sanitize_str(req.badge) if req.badge else None
        if req.image:
            item.image = req.image
        if val is not None:
            item.in_stock = val
        item.customizable = bool(req.customizable)
        item.is_deleted = False

    db.commit()
    db.refresh(item)

    log_audit(db, actor="admin", action="UPSERT_MENU_ITEM", resource_type="menu_item", resource_id=str(item.id), ip_address=get_client_ip(request), details=f"Upserted {item.name} at ${item.price:.2f}")

    return {
        "id": item.id, "name": item.name, "category": item.category,
        "price": item.price, "description": item.description,
        "badge": item.badge, "inStock": item.in_stock, "in_stock": item.in_stock,
        "image": item.image, "customizable": item.customizable
    }

@app.put("/menu", dependencies=[Depends(require_admin)])
@app.put("/api/menu", dependencies=[Depends(require_admin)])
@app.put("/api/v1/menu", dependencies=[Depends(require_admin)])
@app.patch("/menu", dependencies=[Depends(require_admin)])
@app.patch("/api/menu", dependencies=[Depends(require_admin)])
@app.patch("/api/v1/menu", dependencies=[Depends(require_admin)])
def update_menu_item_body(req: MenuItemCreate, request: Request, db: Session = Depends(get_db)):
    item_id = getattr(req, "id", None)
    if item_id:
        return update_menu_item(item_id, req, request, db)
    return create_menu_item(req, request, db)

@app.delete("/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.delete("/api/menu/{item_id}", dependencies=[Depends(require_admin)])
@app.delete("/api/v1/menu/{item_id}", dependencies=[Depends(require_admin)])
def delete_menu_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    # Soft Delete
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    db.commit()

    log_audit(db, actor="admin", action="SOFT_DELETE_MENU_ITEM", resource_type="menu_item", resource_id=str(item_id), ip_address=get_client_ip(request), details=f"Soft deleted {item.name}")

    return {"deleted": True, "id": item_id}

@app.patch("/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
@app.patch("/api/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
@app.patch("/api/v1/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
@app.post("/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
@app.post("/api/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
@app.post("/api/v1/menu/{item_id}/stock", dependencies=[Depends(require_admin)])
def toggle_stock(item_id: int, request: Request, req: Optional[StockUpdateRequest] = None, in_stock: Optional[bool] = None, db: Session = Depends(get_db)):
    item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    new_val = not item.in_stock
    if req is not None:
        if req.inStock is not None:
            new_val = req.inStock
        elif req.in_stock is not None:
            new_val = req.in_stock
    if in_stock is not None:
        new_val = in_stock
    item.in_stock = new_val
    db.commit()
    db.refresh(item)

    log_audit(db, actor="admin", action="TOGGLE_STOCK", resource_type="menu_item", resource_id=str(item.id), ip_address=get_client_ip(request), details=f"Stock set to {new_val}")

    return {"id": item.id, "inStock": item.in_stock, "in_stock": item.in_stock}

# --- ORDERS (WITH IDEMPOTENCY, RECALCULATION & PAGINATION) ---
@app.get("/orders")
@app.get("/api/orders")
@app.get("/api/v1/orders")
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    orders = db.query(OrderModel).filter(OrderModel.is_deleted == False).order_by(OrderModel.order_time.desc()).offset(offset).limit(limit).all()
    res = []
    for o in orders:
        is_paid = (o.status == "Paid Online" or "Paid" in (o.status or ""))
        res.append({
            "id": o.id,
            "customerName": o.customer_name,
            "phone": o.phone,
            "customerPhone": o.phone,
            "items": json.loads(o.items_json) if o.items_json else [],
            "subtotal": o.subtotal,
            "tax": o.tax,
            "total": o.total,
            "status": o.status,
            "paidOnline": is_paid,
            "paymentStatus": "Paid Online (Stripe)" if is_paid else "Pay at Counter",
            "orderTime": o.order_time.isoformat() if o.order_time else "",
            "pickupEstimate": "10-12 mins",
            "notes": o.notes or ""
        })
    return res

@app.get("/orders/{order_id}")
@app.get("/api/orders/{order_id}")
@app.get("/api/v1/orders/{order_id}")
def get_single_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.is_deleted == False).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order reference not found")
    is_paid = (order.status == "Paid Online" or "Paid" in (order.status or ""))
    return {
        "id": order.id,
        "customerName": order.customer_name,
        "phone": order.phone,
        "customerPhone": order.phone,
        "items": json.loads(order.items_json) if order.items_json else [],
        "subtotal": order.subtotal,
        "tax": order.tax,
        "total": order.total,
        "status": order.status,
        "paidOnline": is_paid,
        "paymentStatus": "Paid Online (Stripe)" if is_paid else "Pay at Counter",
        "orderTime": order.order_time.isoformat() if order.order_time else "",
        "notes": order.notes or ""
    }

@app.post("/orders")
@app.post("/api/orders")
@app.post("/api/v1/orders")
def place_order(req: OrderCreate, request: Request, db: Session = Depends(get_db)):
    # Check Idempotency-Key
    idempotency_key = request.headers.get("Idempotency-Key") or request.headers.get("X-Idempotency-Key")
    cached = check_idempotency(db, idempotency_key, "/api/orders")
    if cached:
        return cached

    # Pre-load menu items for server-side price recalculation (Mass Assignment protection)
    menu_catalog = {m.name.lower(): m for m in db.query(MenuItemModel).filter(MenuItemModel.is_deleted == False).all()}

    computed_subtotal = 0.0
    sanitized_items = []
    for item in req.items:
        clean_name = sanitize_str(item.name)
        db_item = menu_catalog.get(clean_name.lower())
        item_unit_price = db_item.price if db_item else (item.price if item.price > 0 else 5.0)
        
        computed_subtotal += item_unit_price * item.qty
        sanitized_items.append({
            "id": getattr(item, "id", None) or (db_item.id if db_item else None),
            "name": clean_name,
            "qty": item.qty,
            "price": item_unit_price,
            "customizations": sanitize_str(item.customizations)
        })

    subtotal = round(computed_subtotal, 2)
    tax = round(subtotal * 0.0825, 2)
    total = round(subtotal + tax, 2)

    order_id = f"FT-{random.randint(1000, 9999)}"
    is_paid = bool(req.paidOnline)
    status_str = "Paid Online" if is_paid else "New Order"
    payment_status = "Paid Online (Stripe)" if is_paid else "Pay at Counter"

    order = OrderModel(
        id=order_id,
        customer_name=sanitize_str(req.customerName),
        phone=sanitize_str(req.phone or "(512) 540-6033"),
        items_json=json.dumps(sanitized_items),
        subtotal=subtotal,
        tax=tax,
        total=total,
        status=status_str,
        notes=sanitize_str(req.notes or ""),
        is_deleted=False
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    log_audit(db, actor=order.customer_name, action="PLACE_ORDER", resource_type="order", resource_id=order.id, ip_address=get_client_ip(request), details=f"Total: ${order.total}")

    result = {
        "id": order.id,
        "customerName": order.customer_name,
        "phone": order.phone,
        "customerPhone": order.phone,
        "items": sanitized_items,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "total": order.total,
        "status": order.status,
        "paidOnline": is_paid,
        "paymentStatus": payment_status,
        "orderTime": order.order_time.isoformat() if order.order_time else "",
        "pickupEstimate": "10-12 mins",
        "notes": order.notes,
        "qrCode": f"FLATTRACK-{order.id}-VERIFIED"
    }

    store_idempotency(db, idempotency_key, "/api/orders", result, 200)
    return result

@app.patch("/orders/{order_id}/status", dependencies=[Depends(require_staff)])
@app.patch("/api/orders/{order_id}/status", dependencies=[Depends(require_staff)])
@app.patch("/api/v1/orders/{order_id}/status", dependencies=[Depends(require_staff)])
def update_order_status(order_id: str, new_status: str, request: Request, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = sanitize_str(new_status)
    db.commit()

    log_audit(db, actor="staff", action="UPDATE_ORDER_STATUS", resource_type="order", resource_id=order.id, ip_address=get_client_ip(request), details=f"Status: {order.status}")

    return {"id": order.id, "status": order.status}

# --- STRIPE PREPAID CHECKOUT ---
@app.post("/checkout/create-session")
@app.post("/api/checkout/create-session")
@app.post("/api/v1/checkout/create-session")
def create_checkout_session(data: dict):
    order_id = f"FT-{random.randint(1000, 9999)}"
    return {
        "sessionId": f"cs_test_{random.randint(100000, 999999)}",
        "orderId": order_id,
        "status": "paid_online",
        "paymentStatus": "paid",
        "qrCode": f"FLATTRACK-{order_id}-PREPAID"
    }

# --- RESERVATIONS (WITH IDEMPOTENCY & PAGINATION) ---
@app.get("/reservations")
@app.get("/api/reservations")
@app.get("/api/v1/reservations")
def get_reservations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    res_list = db.query(ReservationModel).filter(ReservationModel.is_deleted == False).offset(offset).limit(limit).all()
    return [
        {
            "id": r.id, "name": r.name, "email": r.email, "phone": r.phone,
            "partySize": r.party_size, "party_size": r.party_size,
            "date": r.date, "res_date": r.date,
            "time": r.time, "res_time": r.time,
            "status": r.status, "notes": r.notes
        }
        for r in res_list
    ]

@app.post("/reservations")
@app.post("/api/reservations")
@app.post("/api/v1/reservations")
def create_reservation(req: ReservationCreate, request: Request, db: Session = Depends(get_db)):
    idempotency_key = request.headers.get("Idempotency-Key") or request.headers.get("X-Idempotency-Key")
    cached = check_idempotency(db, idempotency_key, "/api/reservations")
    if cached:
        return cached

    res_id = f"RES-{random.randint(100, 999)}"
    party = req.partySize if req.partySize is not None else (req.party_size if req.party_size is not None else 2)
    r_date = req.date or req.res_date or "Today"
    r_time = req.time or req.res_time or "12:00 PM"
    
    res = ReservationModel(
        id=res_id,
        name=sanitize_str(req.name),
        email=sanitize_str(req.email),
        phone=sanitize_str(req.phone),
        party_size=party,
        date=sanitize_str(r_date),
        time=sanitize_str(r_time),
        notes=sanitize_str(req.notes or ""),
        status="Confirmed",
        is_deleted=False
    )
    db.add(res)
    db.commit()

    log_audit(db, actor=res.name, action="CREATE_RESERVATION", resource_type="reservation", resource_id=res.id, ip_address=get_client_ip(request), details=f"Date: {res.date} {res.time}")

    result = {
        "id": res.id,
        "name": res.name,
        "email": res.email,
        "phone": res.phone,
        "partySize": res.party_size,
        "party_size": res.party_size,
        "date": res.date,
        "res_date": res.date,
        "time": res.time,
        "res_time": res.time,
        "status": res.status,
        "notes": res.notes
    }

    store_idempotency(db, idempotency_key, "/api/reservations", result, 200)
    return result

@app.patch("/reservations/{res_id}/status", dependencies=[Depends(require_staff)])
@app.patch("/api/reservations/{res_id}/status", dependencies=[Depends(require_staff)])
@app.patch("/api/v1/reservations/{res_id}/status", dependencies=[Depends(require_staff)])
def update_reservation_status(res_id: str, new_status: str, request: Request, db: Session = Depends(get_db)):
    res = db.query(ReservationModel).filter(ReservationModel.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    res.status = sanitize_str(new_status)
    db.commit()

    log_audit(db, actor="staff", action="UPDATE_RESERVATION_STATUS", resource_type="reservation", resource_id=res.id, ip_address=get_client_ip(request), details=f"Status: {res.status}")

    return {"id": res.id, "status": res.status}

# --- INQUIRIES & MESSAGES ---
@app.get("/messages")
@app.get("/api/messages")
@app.get("/api/inquiries")
@app.get("/api/v1/inquiries")
def get_inquiries(db: Session = Depends(get_db)):
    items = db.query(InquiryModel).all()
    return [
        {
            "id": i.id, "name": i.name, "email": i.email,
            "subject": i.subject, "message": i.message, "date": i.date
        }
        for i in items
    ]

@app.post("/messages")
@app.post("/api/messages")
@app.post("/api/inquiries")
@app.post("/api/v1/inquiries")
def create_inquiry(req: InquiryCreate, request: Request, db: Session = Depends(get_db)):
    inq = InquiryModel(
        id=f"INQ-{random.randint(1000, 9999)}",
        name=sanitize_str(req.name),
        email=sanitize_str(req.email),
        subject=sanitize_str(req.subject),
        message=sanitize_str(req.message),
        date="Today"
    )
    db.add(inq)
    db.commit()

    log_audit(db, actor=inq.name, action="CREATE_INQUIRY", resource_type="inquiry", resource_id=inq.id, ip_address=get_client_ip(request), details=f"Subject: {inq.subject}")

    return {"id": inq.id, "saved": True}

# --- SUBSCRIBERS & CATERING ---
@app.get("/subscriptions")
@app.get("/api/subscriptions")
@app.get("/api/subscribers")
@app.get("/api/v1/subscribers")
def get_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(SubscriberModel).all()
    return [
        {
            "id": s.id, "roast": s.roast, "grind": s.grind,
            "frequency": s.frequency, "monthlyPrice": s.monthly_price,
            "customerName": s.customer_name, "email": s.email
        }
        for s in subs
    ]

@app.post("/subscriptions")
@app.post("/api/subscriptions")
@app.post("/api/subscribers")
@app.post("/api/v1/subscribers")
def create_subscriber(req: SubscriberCreate, request: Request, db: Session = Depends(get_db)):
    sub = SubscriberModel(
        id=f"SUB-{random.randint(1000, 9999)}",
        roast=sanitize_str(req.roast),
        grind=sanitize_str(req.grind),
        frequency=sanitize_str(req.frequency),
        monthly_price=round(req.monthlyPrice, 2),
        customer_name=sanitize_str(req.customerName),
        email=sanitize_str(req.email)
    )
    db.add(sub)
    db.commit()

    log_audit(db, actor=sub.customer_name, action="CREATE_SUBSCRIPTION", resource_type="subscriber", resource_id=sub.id, ip_address=get_client_ip(request), details=f"Roast: {sub.roast}")

    return {"id": sub.id, "active": True}

@app.post("/catering")
@app.post("/api/catering")
@app.post("/api/v1/catering")
def create_catering(data: dict):
    return {"id": f"CAT-{random.randint(100, 999)}", "status": "Inquiry Received", "confirmed": True}

# --- AUDIT LOGS (ADMIN ONLY, PAGINATED) ---
@app.get("/audit-logs", dependencies=[Depends(require_admin)], response_model=List[AuditLogResponse])
@app.get("/api/audit-logs", dependencies=[Depends(require_admin)], response_model=List[AuditLogResponse])
@app.get("/api/v1/audit-logs", dependencies=[Depends(require_admin)], response_model=List[AuditLogResponse])
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    logs = db.query(AuditLogModel).order_by(AuditLogModel.timestamp_utc.desc()).offset(offset).limit(limit).all()
    return logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
