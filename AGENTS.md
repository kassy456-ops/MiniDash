Project Overview

This food delivery application was created to complete an assignment in Software Engineering. It has been created using a variety of technologies including FastAPI as the web framework, SQLite as the relational database manager, HTML, CSS, and JavaScript. The main features that support the functionality of this application include allowing users to browse restaurants, view menus, create regular orders, track those orders, and schedule future delivery times.

Project Layout

This application utilizes a modular monolithic layout with each module or service having its own unique function within the larger structure of the application. These modules are defined by their respective files as listed below:

* src/main.py handles all API calls and performs most of the functions related to order management.
* src/database.py manages the interaction with the SQLite database.
* src/scheduler.py manages all scheduling and will automatically release any ordered items at the designated time.
* src/clock.py defines both the real-time clock (Clock) and fake clock (FakeClock).
* frontend/ holds the customer interface.
* tests/ holds automated tests.
* docs/ includes the requirements, design, and development task documentation.

Development Guidelines
1. Keep the project simple and suitable for one developer.
2. Use FastAPI for backend functionality and SQLite for data storage.
3. Use HTML, CSS, and vanilla JavaScript for the frontend.
4. Keep the existing project structure organized.
5. Avoid adding unnecessary frameworks, services, or dependencies.
6. Preserve existing functionality when making changes.
7. Use database prices when calculating order totals.

Scheduling Rules

Scheduled deliveries must follow these rules:
- Customers can schedule deliveries at least 45 minutes and no more than seven days in advance.
- Scheduled delivery times must fall within the restaurant's opening hours.
- New scheduled orders must have the status SCHEDULED.
- Scheduled orders change to PLACED when they reach the 30-minute release window.
- Each scheduled order must only be released once.
- Customers can cancel scheduled orders before the release cutoff.
- Cancellation requests at or after the cutoff must be rejected.
- Cancelled orders must not be released later.
- Regular orders must continue working normally.

Testing Guidelines
1. Use pytest and FastAPI TestClient for API testing.
2. Use a separate temporary SQLite database for tests.
3. Use FakeClock to test time-dependent behavior.
4. Test valid and invalid inputs.
5. Test scheduling boundaries, including the 45-minute minimum, seven-day maximum, and 30-minute release cutoff.
6. Run existing tests after changing backend functionality.
7. Only modify existing functionality when a problem has been identified.

AI Usage Guidelines
There are a number of ways an artificial intelligence tool could potentially assist in the development of a software application. This would include assistance with coding (including developing new algorithms), testing, planning, and debugging. All generated code produced by an artificial intelligence tool should be reviewed for inclusion into your project prior to acceptance. The developer should review each suggestion from the AI tool against both the documentation and the current implementation of your program to ensure all requirements have been met. As with any source of changes to your program, keep them as small as possible so they can easily be understood and verified. Any suggestions created by an artificial intelligence tool that create unnecessary complexity and/or do not comply with your programs' requirements should either be modified or dismissed.