from contextlib import asynccontextmanager

from fastapi import FastAPI
from .database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="MiniDash", lifespan=lifespan)

from .database import get_connection


@app.get("/restaurants")
def list_restaurants():
    with get_connection() as connection:
        restaurants = connection.execute(
            """
            SELECT id, name, cuisine, opens_at,
                   closes_at, avg_prep_minutes
            FROM restaurants
            ORDER BY id
            """
        ).fetchall()

    return [dict(restaurant) for restaurant in restaurants]

from fastapi import HTTPException

@app.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: int):
    with get_connection() as connection:
        restaurant = connection.execute(
            "SELECT id FROM restaurants WHERE id = ?",
            (restaurant_id,),
        ).fetchone()

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        menu_items = connection.execute(
            """
            SELECT id, restaurant_id, name, price_cents
            FROM menu_items
            WHERE restaurant_id = ?
            ORDER BY id
            """,
            (restaurant_id,),
        ).fetchall()

        return [dict(item) for item in menu_items]
    
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta


class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


class CreateOrderRequest(BaseModel):
    restaurant_id: int
    address: str = Field(min_length=1)
    items: list[OrderItemRequest] = Field(min_length=1)
    scheduled_for: datetime | None = None




@app.post("/orders", status_code=201)
def create_order(order: CreateOrderRequest):
    if order.scheduled_for is not None:
        if order.scheduled_for.tzinfo is None:
            raise HTTPException(
                status_code=400,
                detail="Scheduled time must include a timezone"
            )

        now = datetime.now(timezone.utc)
        scheduled_time = order.scheduled_for.astimezone(timezone.utc)

        if scheduled_time < now + timedelta(minutes=45):
            raise HTTPException(
                status_code=400,
                detail="Scheduled delivery must be at least 45 minutes from now"
            )

        if scheduled_time > now + timedelta(days=7):
            raise HTTPException(
                status_code=400,
                detail="Scheduled delivery cannot be more than 7 days away"
            )
    with get_connection() as connection:
        restaurant = connection.execute(
            "SELECT id FROM restaurants WHERE id = ?",
            (order.restaurant_id,),
        ).fetchone()

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        total_cents = 0
        order_items = []

        for item in order.items:
            menu_item = connection.execute(
                """
                SELECT id, price_cents
                FROM menu_items
                WHERE id = ? AND restaurant_id = ?
                """,
                (item.menu_item_id, order.restaurant_id),
            ).fetchone()

            if menu_item is None:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid menu item for this restaurant"
                )

            total_cents += menu_item["price_cents"] * item.quantity
            order_items.append((item.menu_item_id, item.quantity))

        order_status = "SCHEDULED" if order.scheduled_for is not None else "PLACED"

        cursor = connection.execute(
            """
            INSERT INTO orders
            (restaurant_id, status, total_cents, address, created_at, scheduled_for)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order.restaurant_id,
                order_status,
                total_cents,
                order.address,
                datetime.now(timezone.utc).isoformat(),
                (
                    order.scheduled_for.astimezone(timezone.utc).isoformat()
                    if order.scheduled_for is not None
                    else None
                ),
            ),
        )

        order_id = cursor.lastrowid

        for menu_item_id, quantity in order_items:
            connection.execute(
                """
                INSERT INTO order_items
                (order_id, menu_item_id, quantity)
                VALUES (?, ?, ?)
                """,
                (order_id, menu_item_id, quantity),
            )

        connection.commit()

    return {
        "id": order_id,
        "restaurant_id": order.restaurant_id,
        "status": order_status,
        "total_cents": total_cents,
        "address": order.address,
        "scheduled_for": (
            order.scheduled_for.astimezone(timezone.utc).isoformat()
            if order.scheduled_for is not None
            else None
        ),
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with get_connection() as connection:
        order = connection.execute(
            """
            SELECT id, restaurant_id, status, total_cents,
                   address, created_at, scheduled_for
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        items = connection.execute(
            """
            SELECT menu_item_id, quantity
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
            """,
            (order_id,),
        ).fetchall()

        result = dict(order)
        result["items"] = [dict(item) for item in items]

        return result
    

class UpdateOrderStatusRequest(BaseModel):
    status: str


@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, request: UpdateOrderStatusRequest):
    allowed_statuses = [
        "PLACED",
        "PREPARING",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED"
    ]

    if request.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    with get_connection() as connection:
        order = connection.execute(
            "SELECT id FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        connection.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (request.status, order_id)
        )
        connection.commit()

    return {
        "id": order_id,
        "status": request.status
    }
