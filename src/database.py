import sqlite3
from pathlib import Path

# Defines where the SQLite database file is stored.
DATABASE_PATH = Path(__file__).resolve().parent.parent / "minidash.db"


# Opens the database, makes rows accessible by column name,
# and enables foreign key relationships between tables.
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Initializes MiniDash's database.
# Creates four related tables, supports existing databases,
# and inserts five sample restaurants and ten menu items.
def initialize_database():
    with get_connection() as connection:

        # Creates tables only if they do not already exist.
        # restaurants: restaurant information and operating hours.
        # menu_items: food names, prices, and restaurant relationships.
        # orders: customer addresses, totals, statuses, and delivery times.
        # order_items: items and quantities belonging to each order.
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

        # Checks whether an older database is missing the
        # scheduled_for column and adds it if necessary.
        columns = connection.execute("PRAGMA table_info(orders)").fetchall()
        column_names = [column["name"] for column in columns]

        if "scheduled_for" not in column_names:
            connection.execute(
                "ALTER TABLE orders ADD COLUMN scheduled_for TEXT"
            )

        # Defines the five sample restaurants with their cuisines,
        # operating hours, and average preparation times.
        restaurants = [
            (1, "Pizza Palace", "Italian", "10:00", "22:00", 25),
            (2, "Sushi House", "Japanese", "11:00", "21:00", 30),
            (3, "Taco Town", "Mexican", "10:00", "23:00", 20),
            (4, "Burger Corner", "American", "09:00", "22:00", 15),
            (5, "Curry Kitchen", "Indian", "11:00", "22:00", 35),
        ]

        # Adds the restaurants without duplicating existing records.
        connection.executemany(
            """
            INSERT OR IGNORE INTO restaurants
            (id, name, cuisine, opens_at, closes_at, avg_prep_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            restaurants,
        )

        # Defines ten sample menu items.
        # Prices are stored in cents to avoid floating-point issues.
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

        # Inserts the menu items without duplicating existing records.
        connection.executemany(
            """
            INSERT OR IGNORE INTO menu_items
            (id, restaurant_id, name, price_cents)
            VALUES (?, ?, ?, ?)
            """,
            menu_items,
        )