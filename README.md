MiniDash — Food Delivery Application

Project Overview

MiniDash is an example of a small food delivery application that was created with FastAPI and SQLite. It utilizes web development technology such as HTML/CSS/JavaScript in addition to Python for creating the functionality behind MiniDash. MiniDash provides customers with the ability to locate different restaurants, see what each restaurant offers (menu), select food items they want from each menu, put those selected items in a shopping cart, make selections from the shopping cart to complete orders, and follow the status of completed orders. In addition, MiniDash will allow customers to schedule deliveries at a later time. The structure for this project will utilize a monolithic modular design. This modular monolithic design allows MiniDash to be broken down into multiple smaller files (modules) but still run as if it were a single unit.

Features
- Browse five restaurants and their menus.
- Add menu items to a shopping cart and view the total price.
- Place regular orders with a delivery address.
- Schedule deliveries between 45 minutes and seven days in advance.
- Validate scheduled deliveries against restaurant opening hours.
- Automatically release scheduled orders 30 minutes before delivery.
- Track orders using an order number.
- Cancel scheduled orders before the 30-minute release cutoff.

Technologies Used
- Python and FastAPI for the backend.
- SQLite for storing restaurants, menus, and orders.
- HTML, CSS, and JavaScript for the frontend.
- pytest and FastAPI TestClient for automated testing.

Project Structure

Folder/File	                 Description
src/main.py	              FastAPI application and endpoints
src/database.py	          Database setup and operations
src/scheduler.py	      Scheduled order release logic
src/clock.py	          Clock and FakeClock
frontend/	              HTML, CSS, and JavaScript frontend
tests/	                  Automated API and scheduling tests
docs/	                  Requirements, design, and development tasks
AGENTS.md	              Project guidelines
AI_LOG.md	              AI usage documentation

How to Run MiniDash
1. Open the MiniDash project folder in VS Code.

2. Create a virtual environment if one does not already exist:  python3 -m venv .venv

3. Activate the virtual environment: source .venv/bin/activate

4. Install the required Python libraries:
pip install fastapi uvicorn pytest httpx

5. Start the FastAPI server from the project folder:
uvicorn src.main:app --reload

6. Open http://127.0.0.1:8000/app/ in your browser to use MiniDash.

The API documentation is available at http://127.0.0.1:8000/docs.


Testing
MiniDash uses pytest to test its API endpoints and scheduled delivery functionality.

To run the automated tests, open the VS Code terminal and enter:

python -m pytest tests/ -v

The tests use a separate SQLite database so they do not affect regular customer orders. FakeClock is used to test scheduling rules without waiting for real time to pass.