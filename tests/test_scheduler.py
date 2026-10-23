import sqlite3
from datetime import datetime, timedelta, timezone

from src.clock import FakeClock
from src.scheduler import release_due_orders

def test_scheduled_order_releases_30_minutes_before():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            scheduled_for TEXT
        )
    """)

    delivery_time = datetime(
        2026, 10, 24, 18, 0,
        tzinfo=timezone.utc
    )

    connection.execute(
        """
        INSERT INTO orders (id, status, scheduled_for)
        VALUES (?, ?, ?)
        """,
        (1, "SCHEDULED", delivery_time.isoformat())
    )
    connection.commit()

    # Simulate 5:29 PM (31 minutes before delivery)
    fake_clock = FakeClock(
        datetime(2026, 10, 24, 17, 29, tzinfo=timezone.utc)
    )

    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 0
    assert order[0] == "SCHEDULED"

    # Simulate 5:30 PM (exactly 30 minutes before delivery)
    fake_clock.fixed_time = datetime(
        2026, 10, 24, 17, 30, tzinfo=timezone.utc
    )

    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 1
    assert order[0] == "PLACED"

    # Run the scheduler again at the same time
    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 0
    assert order[0] == "PLACED"

    
def test_cancelled_order_is_not_released():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            scheduled_for TEXT
        )
    """)

    delivery_time = datetime(
        2026, 10, 24, 18, 0,
        tzinfo=timezone.utc
    )

    connection.execute(
        """
        INSERT INTO orders (id, status, scheduled_for)
        VALUES (?, ?, ?)
        """,
        (1, "CANCELLED", delivery_time.isoformat())
    )
    connection.commit()

    fake_clock = FakeClock(
        datetime(2026, 10, 24, 17, 30, tzinfo=timezone.utc)
    )

    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 0
    assert order[0] == "CANCELLED"

    connection.close()
