from datetime import timedelta
from src.database import get_connection


def release_due_orders(clock, connection=None):
    now = clock.now()
    cutoff = now + timedelta(minutes=30)

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

        connection.commit()
        return cursor.rowcount