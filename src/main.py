
# Imports FastAPI, database, scheduling, and application lifecycle tools.
import asyncio
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from .database import initialize_database


# Runs the scheduler every 10 seconds in the background.
# It checks whether any scheduled orders should become PLACED.
async def scheduler_loop():
    while True:
        await asyncio.to_thread(release_due_orders, clock)
        await asyncio.sleep(10)


# Initializes the database and starts the scheduler when
# FastAPI starts. Stops the scheduler when FastAPI shuts down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    scheduler_task = asyncio.create_task(scheduler_loop())

    try:
        yield
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass


# Creates the MiniDash FastAPI application.
app = FastAPI(title="MiniDash", lifespan=lifespan)

from .database import get_connection


# GET /restaurants
# Retrieves all five restaurants from SQLite and returns them as JSON.
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


# GET /restaurants/{restaurant_id}/menu
# Checks that the restaurant exists, then returns its menu.
# Returns HTTP 404 for an invalid restaurant ID.
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
from zoneinfo import ZoneInfo
from src.clock import Clock
from src.scheduler import release_due_orders

# Creates the clock used for real-time scheduling.
clock = Clock()


# Defines the required information for each food item.
# Quantities must be greater than zero.
class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


# Defines the data required to place an order.
# scheduled_for is optional because regular orders do not need it.
class CreateOrderRequest(BaseModel):
    restaurant_id: int
    address: str = Field(min_length=1)
    items: list[OrderItemRequest] = Field(min_length=1)
    scheduled_for: datetime | None = None


# POST /orders
# Validates an order, checks scheduling rules, calculates
# the total using database prices, and saves the order.
@app.post("/orders", status_code=201)
def create_order(order: CreateOrderRequest):

    # For scheduled orders, require a timezone and enforce
    # the 45-minute minimum and seven-day maximum.
    if order.scheduled_for is not None:
        if order.scheduled_for.tzinfo is None:
            raise HTTPException(
                status_code=400,
                detail="Scheduled time must include a timezone"
            )

        now = clock.now()
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

        # Confirm that the restaurant exists.
        restaurant = connection.execute(
            "SELECT id, opens_at, closes_at FROM restaurants WHERE id = ?",
            (order.restaurant_id,),
        ).fetchone()

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        # Scheduled deliveries must be within restaurant hours.
        # Times are converted to New York time before comparison.
        # The second condition handles restaurants open past midnight.
        if order.scheduled_for is not None:
            local_time = scheduled_time.astimezone(
                ZoneInfo("America/New_York")
            ).time()

            opening_time = datetime.strptime(
                restaurant["opens_at"], "%H:%M"
            ).time()

            closing_time = datetime.strptime(
                restaurant["closes_at"], "%H:%M"
            ).time()

            if opening_time <= closing_time:
                is_open = opening_time <= local_time < closing_time
            else:
                is_open = (
                    local_time >= opening_time
                    or local_time < closing_time
                )

            if not is_open:
                raise HTTPException(
                    status_code=400,
                    detail="Restaurant is closed at the scheduled delivery time"
                )

        # Validate every menu item and calculate the total.
        # Prices come from SQLite rather than the frontend,
        # preventing customers from submitting their own prices.
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

        # Regular orders start as PLACED.
        # Future deliveries start as SCHEDULED.
        order_status = "SCHEDULED" if order.scheduled_for is not None else "PLACED"

        # Save the main order record, including its status,
        # total, address, creation time, and scheduled time.
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
                clock.now().isoformat(),
                (
                    order.scheduled_for.astimezone(timezone.utc).isoformat()
                    if order.scheduled_for is not None
                    else None
                ),
            ),
        )

        # Retrieve the automatically generated order ID.
        order_id = cursor.lastrowid

        # Save each ordered food item and its quantity.
        for menu_item_id, quantity in order_items:
            connection.execute(
                """
                INSERT INTO order_items
                (order_id, menu_item_id, quantity)
                VALUES (?, ?, ?)
                """,
                (order_id, menu_item_id, quantity),
            )

        # Permanently save the database changes.
        connection.commit()

    # Return the new order's details to the frontend.
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


# GET /orders/{order_id}
# Retrieves an order and its food items using the order number.
# Returns HTTP 404 if the order does not exist.
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


# Defines the information required to update an order's status.
class UpdateOrderStatusRequest(BaseModel):
    status: str


# PATCH /orders/{order_id}/status
# Validates status changes and handles scheduled-order cancellation.
@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, request: UpdateOrderStatusRequest):

    # Only these status values are accepted for manual updates.
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

        # Retrieve the order and reject invalid order IDs.
        order = connection.execute(
            "SELECT id, status, scheduled_for FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # Cancelled orders cannot be updated again.
        if order["status"] == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail="Cancelled orders cannot be updated"
            )

        # Scheduled orders can only be cancelled manually.
        # Cancellation must happen before the 30-minute cutoff.
        if order["status"] == "SCHEDULED":
            if request.status != "CANCELLED":
                raise HTTPException(
                    status_code=400,
                    detail="Scheduled orders cannot be manually updated before release"
                )

            scheduled_time = datetime.fromisoformat(
                order["scheduled_for"]
            )

            release_time = scheduled_time - timedelta(minutes=30)

            if clock.now() >= release_time:
                raise HTTPException(
                    status_code=400,
                    detail="Scheduled order can no longer be cancelled"
                )

        # Uses an additional SQL condition to make sure
        # the order is still scheduled and outside the cutoff.
        if order["status"] == "SCHEDULED":
            cursor = connection.execute(
                """
                UPDATE orders
                SET status = 'CANCELLED'
                WHERE id = ?
                  AND status = 'SCHEDULED'
                  AND scheduled_for > ?
                """,
                (order_id, (clock.now() + timedelta(minutes=30)).isoformat())
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Scheduled order can no longer be cancelled"
                )

        else:
            # Regular and already released orders use
            # the normal status update operation.
            connection.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (request.status, order_id)
            )

        connection.commit()

    # Return the updated status to the frontend.
    return {
        "id": order_id,
        "status": request.status
    }


# Locates the frontend folder containing HTML, CSS, and JavaScript.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# Redirects the homepage to the MiniDash frontend.
@app.get("/", include_in_schema=False)
def frontend_home():
    return RedirectResponse(url="/app/")


# Serves the frontend files at the /app URL.
app.mount(
    "/app",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend"
)
