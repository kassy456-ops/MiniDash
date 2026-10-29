MiniDash — AI Usage Log

Entry 1 — Project Architecture

Task: Plan the MiniDash application structure.

Prompt: I requested ChatGPT to provide a minimalistic FastAPI application architecture (SQLite + vanilla JavaScript) for a food delivery application.

What ChatGPT wrote: ChatGPT recommended a modular monolith and suggested separating the API, database, frontend, scheduling logic, and tests.

What I reviewed: I reviewed ChatGPT's suggested project structure to make sure it was simple enough for me to develop and maintain.

What I changed or decided: I chose the modular monolith because MiniDash is a small academic project being developed by one person. Separate microservices would add unnecessary deployment and communication complexity.

Outcome: I accepted the recommended architecture.



Entry 2 — Restaurant and Menu API

Task: Develop functionality for users to view menus at each restaurant.

Prompt: I asked ChatGPT to help create a FastAPI backend that stores five restaurants and their menus in SQLite.

What ChatGPT wrote: ChatGPT created the database creation SQL to establish the tables to store the restaurant data. It also produced sample restaurant and menu data to populate the database. Finally, ChatGPT produced API endpoint routes to access restaurant data and retrieve menu item data for a selected restaurant.

What I reviewed: I confirmed that the data stored in the SQLite database was related properly to allow for easy selection and retrieval of restaurant and menu item data. Additionally, I verified that the API returned the necessary data to support the frontend.

What I changed or decided: I chose to keep the restaurant and menu data in SQLite instead of storing it statically within the frontend. This will make future changes easier to implement without having to modify multiple parts of the application.

Outcome: I approved the initial design as a base for developing MiniDash.



Entry 3 — Order Creation and Validation

Task: Allow customers to create orders.

Prompt: I asked ChatGPT to create order placement and retrieval functionality, including multiple menu items, quantities, delivery addresses, and order totals.

What ChatGPT wrote: ChatGPT created code for handling orders, database queries for storing orders, and calculations for determining totals.

What I reviewed: I verified that the price information used by the application is stored within the database and not provided directly by the user.

What I changed or requested: I explicitly told ChatGPT to process invalid restaurant IDs, invalid menu item IDs, and delivery address fields populated entirely with whitespace.

Outcome: I modified my validation requirements before accepting the complete functionality of the ordering feature.



Entry 4 — Automated API Tests

Task: Write automated tests for the FastAPI endpoints.

Prompt: I asked ChatGPT how to use pytest and FastAPI's TestClient to test restaurants, menus, order creation, order retrieval, and status updates.

What ChatGPT wrote: ChatGPT developed an automated test client for testing APIs and described how to run these tests without manually starting the development server.

What I reviewed: I reviewed the tests to ensure they were processing valid requests, both successful and failing, as well as invalid input.

What I changed or requested: I asked for an independent temporary SQLite database so automated testing did not interfere with existing data in the production order table. Additionally, I requested that the testing be organized simply rather than having a separate fixture file.

Outcome: I modified the testing environment to provide a more self-contained and easily maintained testing environment.



Entry 5 — Scheduled Delivery Implementation

Task: Implement scheduled deliveries.

Prompt: I asked ChatGPT to support deliveries scheduled between 45 minutes and seven days in advance, with a release time 30 minutes before delivery.

What ChatGPT wrote: To schedule future orders, ChatGPT initially used the status PLACED to represent that the order had been scheduled. Then, ChatGPT added another flag indicating whether the kitchen had received it.

Problem identified: Using this method made the meaning of the PLACED status confusing because a future order would appear to have been placed before it was actually released to the kitchen.

What I corrected or requested: I asked ChatGPT to use a different status called SCHEDULED instead of using an additional flag. Orders scheduled for the future should have a status of SCHEDULED until the release time is reached, whereas regular orders should still begin with a status of PLACED.

Outcome: I substantially revised the first AI-generated solution. The transition between statuses became clearer and much simpler to test.



Entry 6 — Time-Based Testing with FakeClock

Task: Create reliable scheduling tests.

Prompt: I asked ChatGPT how to test the exact 45-minute minimum, seven-day maximum, and 30-minute release cutoff.

What ChatGPT wrote: The earlier approach relied on the real system clock for time-based behavior.

Problem identified: It can be challenging to make tests that rely on the current time easy to repeat, particularly when testing exact limits.

What I corrected or requested: I asked ChatGPT to create Clock and FakeClock classes so that tests could specify exactly what the current time was. Additionally, I asked ChatGPT to write tests that check the timing immediately before and after each limit.

Outcome: I completely changed the way ChatGPT tested time. Tests could now simulate a specific moment instead of waiting for real time to pass.



Entry 7 — Restaurant Hours and Cancellation Rules

Task: Verify scheduled-delivery restrictions.

Prompt: I asked ChatGPT to review the scheduling logic and tests for restaurant opening hours, cancellations, and the release cutoff.

What ChatGPT wrote: ChatGPT suggested additional test cases covering restaurant opening and closing times, cancellation before the cutoff, and cancellation at or after the cutoff.

What I reviewed: I focused on whether scheduled deliveries could be accepted outside the allowed hours and whether cancelled orders could accidentally be released later.

What I changed or requested: I instructed ChatGPT to add missing tests and change the backend only if an actual problem was found. I also required regular orders to keep their existing behavior.

Outcome: I strengthened the scheduling test coverage while limiting unnecessary changes.



Entry 8 — Frontend Development

Task: Build the frontend website.

Prompt: I asked ChatGPT to create a simple HTML, CSS, and JavaScript frontend that connects to the existing FastAPI endpoints.

What ChatGPT wrote: ChatGPT generated the restaurant browsing page, the menu display, the shopping cart, the quantity controls on items in the cart, and the total calculation for all items in the cart.

What I reviewed: I reviewed the separation of the frontend code from the backend code, as well as the use of API calls instead of storing restaurant information within JavaScript.

What I changed or requested: I asked ChatGPT to keep the interface simple and suitable for a single-developer project.

Outcome: I accepted the basic frontend structure.



Entry 9 — Scheduled Orders and Tracking in the Frontend

Task: Connect the remaining customer features.

Prompt: I asked ChatGPT to extend the frontend so customers could enter an address, place regular orders, schedule deliveries, track orders by order number, and cancel eligible scheduled orders.

What ChatGPT wrote: ChatGPT generated additional checkout options, scheduled delivery input handling, order tracking, and cancellation of eligible scheduled orders.

What I reviewed: I checked that the interface allowed users to perform the required customer actions and could communicate with the existing FastAPI backend endpoints.

What I changed or requested: I specifically asked ChatGPT to preserve the existing restaurant browsing and cart functionality while adding the new features.

Outcome: I added the new features to the frontend without intentionally replacing its original functions.