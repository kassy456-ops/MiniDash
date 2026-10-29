
# TEST SETUP
# Imports an in-memory SQLite database, date/time tools,
# FakeClock, and the scheduled-order release function.
import sqlite3
from datetime import datetime, timedelta, timezone

from src.clock import FakeClock
from src.scheduler import release_due_orders


# TEST 1: 30-MINUTE RELEASE CUTOFF
# Creates a scheduled order for 6:00 PM.
# Checks that it stays SCHEDULED at 5:29 PM,
# changes to PLACED at 5:30 PM,
# and cannot be released a second time.
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

    # Simulates 5:29 PM, which is 31 minutes before delivery.
    # The order must remain SCHEDULED.
    fake_clock = FakeClock(
        datetime(2026, 10, 24, 17, 29, tzinfo=timezone.utc)
    )

    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 0
    assert order[0] == "SCHEDULED"

    # Simulates exactly 5:30 PM, the 30-minute cutoff.
    # The scheduler must release the order now.
    fake_clock.fixed_time = datetime(
        2026, 10, 24, 17, 30, tzinfo=timezone.utc
    )

    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 1
    assert order[0] == "PLACED"

    # Runs the scheduler again at the same time.
    # The order must not be released twice.
    released_count = release_due_orders(fake_clock, connection)

    order = connection.execute(
        "SELECT status FROM orders WHERE id = 1"
    ).fetchone()

    assert released_count == 0
    assert order[0] == "PLACED"


# TEST 2: CANCELLED ORDERS
# Creates an already cancelled order and simulates
# the 30-minute release time.
# Verifies that the scheduler leaves it CANCELLED.
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
