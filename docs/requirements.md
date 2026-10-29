MiniDash — Requirements

1. Project Description

MiniDash is a basic food ordering app, which will allow users to find restaurants; look at their menu options and pricing; place an order and include their delivery address. Users may also use this app to monitor their orders by entering their order number. For Track A, I added the ability to set up pre-scheduled delivery times for orders. When you select a date/time for your delivery, the system will automatically release the order thirty minutes prior to the selected delivery time.

For this project, I used FastAPI as the back-end framework; SQLite as the database; and HTML/CSS/JavaScript for creating the user interface.

2. User Stories

- As a customer, I want to see all of the restaurants available, so I can determine which one to order from.
- As a customer, I want to see all of the menus offered by each restaurant and prices, so I can make my selection.
- As a customer, I want to be able to submit an order and provide my delivery location.
- As a customer, I want to be able to locate my order based on my order number.
- As a customer, I want to be able to set up a delivery date/time for my order.
- As a customer, I want to be able to cancel an upcoming scheduled delivery before it is released.

3. Acceptance Criteria (EARS)

AC1 — Restaurants

WHEN a customer accesses the restaurant list, THE SYSTEM SHALL display all five available restaurants.

AC2 — Menus

WHEN a customer selects a restaurant, THE SYSTEM SHALL return all of the menu items and prices for the selected restaurant.

AC3 — Invalid Restaurants

IF a customer attempts to access a restaurant that is not found in the database, THEN THE SYSTEM SHALL return an HTTP 404 error.

AC4 — Regular Orders

WHEN a customer submits a valid regular order, THE SYSTEM SHALL store the submitted order with a status of "PLACED".

AC5 — Order Totals

WHEN an order is processed, THE SYSTEM SHALL calculate the correct total for the order using prices stored in the database.

AC6 — Order Tracking

WHEN a customer provides a valid order number, THE SYSTEM SHALL return the details for that order along with its current status.

AC7 — Minimum Delivery Time Prior to Order Submission

IF a customer attempts to schedule a delivery less than forty-five minutes in advance, THEN THE SYSTEM SHALL reject the request.

AC8 — Maximum Delivery Time in Advance

IF a customer attempts to schedule a delivery more than seven days in advance, THEN THE SYSTEM SHALL reject the attempt.

AC9 — Restaurant Hours

IF the delivery time chosen by the customer falls outside of the open hours of the restaurant, THEN THE SYSTEM SHALL reject the order.

AC10 — Scheduled Status

WHEN a customer creates a valid scheduled order, THE SYSTEM SHALL record it as having a status of "SCHEDULED".

AC11 — Auto-released Order Status Change

WHEN a scheduled order reaches the thirty-minute countdown period before being delivered, THE SYSTEM SHALL convert its status to "PLACED" only once.

AC12 — Cancelled Order Status

WHEN a customer cancels an upcoming scheduled order before the thirty-minute automatic-release deadline, THE SYSTEM SHALL update its status to "CANCELLED". IF the customer attempts to cancel at or after the cutoff point, THEN THE SYSTEM SHALL reject the cancellation request.

4. Functional Specifications

MiniDash MUST be able to:

- Show users restaurants and their respective menus;
- Permit customers to add items to their shopping cart;
- Correctly compute order totals;
- Store data about each customer's orders in SQLite;
- Permit customers to search for and keep tabs on their orders;
- Allow both normal and scheduled orders;
- Check if scheduled delivery times are valid;
- Automatically release scheduled orders to "PLACED" status;
- Permit customers to cancel scheduled orders until they are released.

5. Non-functional Specifications

Maintainability: All components of the application (the web API, database, scheduler, frontend and tests) are contained within different files.

Reliability: An order should never be released twice.

Testability: This application utilizes pytest and FakeClock to verify how well schedules are followed.

Persistence: Information related to customer orders is stored in SQLite.

Usability: The front end needs to be easy enough for customers to simply browse through; put in an order; and check on their deliveries.

6. Project Scope

In Scope

- Five restaurants and their menus
- Normal orders
- Order tracking
- Pre-scheduled delivery
- Validating restaurant hours
- Automatically releasing scheduled orders
- Canceling scheduled orders
- Automated testing
- Minimal frontend

Out of Scope

- Real payment processing
- Customer accounts
- Driver GPS tracking
- Employee accounts for restaurants
- Real delivery drivers
- Using external companies for delivering