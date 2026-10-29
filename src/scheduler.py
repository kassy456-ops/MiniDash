from datetime import timedelta
from src.database import get_connection


# Finds orders scheduled for delivery within the next 30 minutes.
# Changes eligible orders from SCHEDULED to PLACED.
# Only SCHEDULED orders are updated, preventing cancelled or
# previously released orders from being released again.
def release_due_orders(clock, connection=None):
    now = clock.now()
    cutoff = now + timedelta(minutes=30)

    # Uses a supplied database connection during testing,
    # or the normal MiniDash database during regular operation.
    with (connection if connection is not None else get_connection()) as connection:
        cursor = connection.execute(
            """
            UPDATE orders
            SET status = 'PLACED'
            WHERE status = 'SCHEDULED'
              AND scheduled_for <= ?
            """,
            (cutoff.isoformat(),)
        )

        # Saves the updates and returns the number of orders released.
        connection.commit()
        return cursor.rowcount