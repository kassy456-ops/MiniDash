MiniDash — Design

1. System Architecture

I used an Architecture that has a Modular Monolith. The application is still running in one system, however the code for each file was written with a specific responsibility. This makes building and testing much easier than microservices.

2. Architecture Diagram

                 Customer
                    |
                    v
       Frontend (HTML, CSS, JS)
                    |
                    v
          FastAPI (src/main.py)
                    |
          +---------+---------+
          |         |         |
          v         v         v
       Database  Scheduler   Clock
      database.py scheduler.py clock.py
          |         |
          v         |
        SQLite <----+
        Database

     Tests (pytest + FakeClock)
          |
          v
     API and Scheduler


The customer interacts directly with the Frontend of the application via using HTML/CSS/JavaScript. Frontend sends requests to Fast API in order to obtain restaurant data, create orders, track delivery status.

Fast API utilizes a Database to both Store and Retrieve Data. Scheduler periodically checks for any Scheduled Orders and Updates Statuses of these orders when they become ready for release. Clock is used as a means to provide Time to Scheduling Operations.

3. Main Components

| File                      | Responsibility                                                     |
| ------------------------- | ------------------------------------------------------------------ |
| `src/main.py`             | Handles API requests, order creation, tracking, and status updates |
| `src/database.py`         | Creates and manages the SQLite database                            |
| `src/scheduler.py`        | Automatically releases scheduled orders                            |
| `src/clock.py`            | Provides Clock and FakeClock for time-based operations             |
| `frontend/index.html`     | Contains the website structure                                     |
| `frontend/style.css`      | Controls the website's appearance                                  |
| `frontend/app.js`         | Connects the frontend to the FastAPI endpoints                     |
| `tests/test_api.py`       | Tests the API functionality                                        |
| `tests/test_scheduler.py` | Tests scheduling and cancellation behavior                         |

4. Database Design

MiniDash uses four database tables.

| Table         | Purpose                                                                         |
| ------------- | ------------------------------------------------------------------------------- |
| `restaurants` | Stores restaurant names, cuisines, opening hours, and preparation times         |
| `menu_items`  | Stores menu items, prices, and their associated restaurants                     |
| `orders`      | Stores order details, delivery addresses, statuses, totals, and scheduled times |
| `order_items` | Stores the menu items and quantities included in each order                     |

The `orders` table includes a `scheduled_for` field for future deliveries.

Prices are stored in cents to avoid rounding errors.

5. API Endpoints

| Method | Endpoint                            | Purpose                                              |
| ------ | ----------------------------------- | ---------------------------------------------------- |
| GET    | `/restaurants`                      | Retrieve all five restaurants                        |
| GET    | `/restaurants/{restaurant_id}/menu` | Retrieve a restaurant's menu                         |
| POST   | `/orders`                           | Place regular or scheduled orders                    |
| GET    | `/orders/{order_id}`                | Retrieve order details and status                    |
| PATCH  | `/orders/{order_id}/status`         | Update an order's status or cancel a scheduled order |

The frontend uses these five endpoints to communicate with the backend.

For scheduled orders, the `POST /orders` request includes an optional `scheduled_for` field.

The system uses the following order statuses: PLACED, SCHEDULED, PREPARING, OUT_FOR_DELIVERY, DELIVERED, and CANCELLED.

6. Scheduled Delivery Process

When a customer places a scheduled order:

    1. The customer selects a restaurant, food items, delivery address, and scheduled delivery time.
    2. FastAPI checks that the delivery time is at least 45 minutes and no more than seven days in advance.
    3. The system checks that the selected delivery time falls within the restaurant's opening hours.
    4. If the request is valid, the order is saved in SQLite with the status SCHEDULED.
    5. The scheduler checks for scheduled orders that are ready to be released.
    6. Once an order reaches the 30-minute release window, its status changes from SCHEDULED to PLACED.

The scheduler runs approximately every 10 seconds while the FastAPI application is running.

7. Scheduled Order Cancellation

Customers have the ability to cancel their pre-scheduled orders up until the 30 minutes prior to when they are set to "release." Once a customer has reached the time frame of releasing (the cutoff), if he/she tries to cancel an order the system will reject that cancellation. Orders canceled in this manner, will now have a status of CANCELLED; however, due to how the scheduling process is designed, these orders will not be able to be released through the scheduler as the scheduling tool only updates orders that have a SCHEDULED status. Scheduled orders will continue to operate independently of regular orders.


8. Clock and FakeClock

The use of Clock and FakeClock by MiniDash facilitates the testing of time-related features within the application (i.e., the 45 minute minimum wait period, the 7 day maximum wait period and the 30 minute wait period before being able to "release") through simulating various times without having to wait in actual real-time. FakeClock is used to allow the simulation of specified times when running tests, whereas Clock allows you to obtain the current time for your application. FastAPI applications utilize a shared Clock instance, which can be passed into the Scheduler as one of its parameters.

9. Architecture Decision Record (ADR)

ADR 1 — Modular Monolith vs. Microservices
Problem: I needed to decide which architecture would be better for MiniDash.

Option 1 — Microservices
   With microservices, different features would run as separate services.
Advantages:
- Services can be deployed independently.
- Individual services can scale separately.
Disadvantages:
- Requires more setup.
- More difficult to test and maintain.
- Adds unnecessary complexity for a small project.

Option 2 — Modular Monolith
With a modular monolith, the backend runs as one application, but the code is divided into separate files.
Advantages:
- Easier to develop and maintain.
- Simpler testing and deployment.
- Suitable for a single developer.
Disadvantages:
- Components cannot be deployed separately.
- The application scales as one system.

Decision: I chose the modular monolith because it is easier to manage and provides enough separation for MiniDash without the complexity of microservices.

10. Design Limitations

MiniDash does not have real payment, account management or gps tracking for drivers. The scheduler in this example is running inside of the FastAPI application as opposed to running as a separate background application. The restaurant hours check validates the scheduled delivery time versus when the order was released. The application has a shared Clock object for all of its api requests and will use this clock object instead of passing the clock into each function that relies on time.