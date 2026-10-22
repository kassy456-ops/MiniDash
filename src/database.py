import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "minidash.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                opens_at TEXT NOT NULL,
                closes_at TEXT NOT NULL,
                avg_prep_minutes INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY,
                restaurant_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price_cents INTEGER NOT NULL,
                FOREIGN KEY (restaurant_id)
                    REFERENCES restaurants(id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                restaurant_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                total_cents INTEGER NOT NULL,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL,
                scheduled_for TEXT,
                FOREIGN KEY (restaurant_id)
                    REFERENCES restaurants(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id)
                    REFERENCES orders(id),
                FOREIGN KEY (menu_item_id)
                    REFERENCES menu_items(id)
            );
        """)

        columns = connection.execute("PRAGMA table_info(orders)").fetchall()
        column_names = [column["name"] for column in columns]

        if "scheduled_for" not in column_names:
            connection.execute(
                "ALTER TABLE orders ADD COLUMN scheduled_for TEXT"
            )

        restaurants = [
            (1, "Pizza Palace", "Italian", "10:00", "22:00", 25),
            (2, "Sushi House", "Japanese", "11:00", "21:00", 30),
            (3, "Taco Town", "Mexican", "10:00", "23:00", 20),
            (4, "Burger Corner", "American", "09:00", "22:00", 15),
            (5, "Curry Kitchen", "Indian", "11:00", "22:00", 35),
        ]

        connection.executemany(
            """
            INSERT OR IGNORE INTO restaurants
            (id, name, cuisine, opens_at, closes_at, avg_prep_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            restaurants,
        )

        menu_items = [
            (1, 1, "Cheese Pizza", 1200),
            (2, 1, "Pepperoni Pizza", 1500),
            (3, 2, "Salmon Roll", 900),
            (4, 2, "Tuna Roll", 1000),
            (5, 3, "Chicken Taco", 400),
            (6, 3, "Veggie Taco", 350),
            (7, 4, "Cheeseburger", 1100),
            (8, 4, "French Fries", 450),
            (9, 5, "Vegetable Curry", 1300),
            (10, 5, "Garlic Naan", 400),
        ]

        connection.executemany(
            """
            INSERT OR IGNORE INTO menu_items
            (id, restaurant_id, name, price_cents)
            VALUES (?, ?, ?, ?)
            """,
            menu_items,
        )