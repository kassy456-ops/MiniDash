
# MiniDash — AI Assistance Log

## Entry 1 — October 16, 2026
**Task:** Create the baseline MiniDash application.

**AI Assistance:** Asked ChatGPT to help build a food delivery REST API using Python, FastAPI, and SQLite.

**Result:** Created the initial project structure, database, and API code.

**Verification:** Ran the application locally using Uvicorn.

## Entry 2 — October 16, 2026
**Task:** Implement restaurant endpoints.

**AI Assistance:** Used ChatGPT for step-by-step guidance implementing GET /restaurants and GET /restaurants/{id}/menu.

**Result:** Both endpoints returned restaurant and menu information.

**Verification:** Tested both endpoints using FastAPI's Swagger interface.

## Entry 3 — October 16, 2026
**Task:** Implement order creation.

**AI Assistance:** Used ChatGPT to help implement POST /orders and understand the request body.

**Result:** Successfully created an order with menu items, a delivery address, and a calculated total.

**Verification:** Tested POST /orders in Swagger and received a successful response.

## Entry 4 — October 19, 2026
**Task:** Implement order retrieval.

**AI Assistance:** Used ChatGPT to help implement GET /orders/{order_id}.

**Result:** Retrieved an existing order and its details.

**Verification:** Tested the endpoint using Swagger.

## Entry 5 — October 19, 2026
**Task:** Implement order status updates.

**AI Assistance:** Used ChatGPT to help implement PATCH /orders/{order_id}/status.

**Result:** Updated an existing order's status from PLACED to PREPARING.

**Verification:** Retrieved the order again and confirmed the updated status was saved.

## Entry 6 — October 19, 2026
**Task:** Write Scheduled Orders requirements.

**AI Assistance:** Asked ChatGPT to draft user stories, EARS acceptance criteria, and out-of-scope features for Track A.

**Result:** Created docs/requirements.md.

**Review:** Requirements will be checked against the assignment and tested during implementation.

## Entry 7 — October 19, 2026
**Task:** Plan the Scheduled Orders architecture.

**AI Assistance:** Asked ChatGPT to help prepare a system design, architecture diagram, and Architecture Decision Record.

**Result:** Created docs/design.md describing the proposed components, database changes, and release processor.

**Review:** The design will be validated against the implemented code.

## Entry 8 — October 19, 2026
**Task:** Break implementation into smaller tasks.

**AI Assistance:** Asked ChatGPT to create an ordered implementation plan with testing activities.

**Result:** Created docs/tasks.md containing ten implementation and submission tasks.

**Review:** Tasks will be completed and verified during development.

## Rejected or Revised AI Suggestions

To be completed when an AI suggestion is genuinely rejected or substantially rewritten during development. Each entry will explain the original suggestion, why it was unsuitable, and what was changed.
