MiniDash — Development Tasks

Task 1 — Project Setup

Goal: Establish the overall project structure and database of MiniDash.

Work: Create separate files for the FastAPI application, the SQLite database, the scheduler, the clock, the frontend, and the tests. Establish the schema of the database tables; insert five example restaurants into the database.

Verification: Launch the FastAPI application and verify that there are five restaurants in the database.


Task 2 — Restaurant & Menu Endpoints
Requirements: AC1, AC2, AC3

Goal: Permit customers to search through restaurants and examine menus.

Work: Develop API endpoints to pull in restaurants and their respective menu items (with prices).

Verification: Verify that all five restaurants are displayed, that menus display the appropriate items, and that an attempt to pull a non-existent restaurant ID returns HTTP 404.


Task 3 — Regular Orders
Requirements: AC4, AC5, AC6

Goal: Enable customers to create and monitor regular orders.

Work: Develop endpoints for creating orders (and determining the total cost based on the prices stored in the database), and endpoints for displaying orders and for modifying order status.

Verification: Check that orders have been successfully created, that total costs were calculated correctly, that orders can be retrieved, and that invalid order information returns an error.


Task 4 — Scheduled Orders
Requirements: AC7, AC8, AC9, AC10

Goal: Enable customers to set up deliveries at some point in the future.

Work: Insert the scheduled_for column into orders. Validate that the minimum is 45 minutes, maximum is seven days, and the selected delivery time falls within restaurant opening hours. Store valid scheduled orders as SCHEDULED.

Verification: Test both valid and invalid delivery times, restaurant hours, and that orders begin with status SCHEDULED.


Task 5 — Automatic Order Release
Requirements: AC11

Goal: Automatically release scheduled orders thirty minutes prior to delivery time.

Work: Develop the scheduler in src/scheduler.py, which updates eligible orders (those in SCHEDULED status) from SCHEDULED to PLACED.

Verification: Use FakeClock to verify that orders are not released before the 30-minute cutoff, are released when eligible, and cannot be released twice.


Task 6 — Scheduled Order Cancellation
Requirements: AC12

Goal: Permit customers to cancel scheduled orders before they are automatically released.

Work: Implement cancellation logic for changing the status of an order to CANCELLED if it has not yet reached its automatic release (30 minutes prior to delivery) and reject cancellation attempts at or after the cutoff.

Verification: Test cancellation before, at, and after the cutoff period. Verify that cancelled orders do not get released.


Task 7 — Automated Testing
Requirements: AC1–AC12

Goal: Test the API and scheduling functions of MiniDash.

Work: Utilize pytest, FastAPI TestClient, and a separate SQLite test database. For testing of scheduling related functions utilize FakeClock.

Verification: Run the API and scheduling tests and check whether they pass.


Task 8 — Frontend Development
Requirements: AC1, AC2, AC4, AC6, AC10, AC12

Goal: Build a minimalistic customer interface to access the MiniDash application.

Work: Create restaurant listing/browsing page, menus for each restaurant, shopping cart feature, order placement function, scheduled deliveries feature, order tracking feature and cancellation of scheduled deliveries via HTML/CSS/JavaScript.

Verification: Manually test the web application to ensure customers can browse restaurants listings, review menus for each restaurant listing, add products to shopping cart, create and schedule deliveries, track their placed orders and cancel scheduled deliveries.