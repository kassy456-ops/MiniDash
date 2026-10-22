
# MiniDash — Track A: Implementation Tasks

## Overview

The Scheduled Orders feature will be developed in small, testable steps. Each task builds on the previous one.

## Task 1: Prepare the Database

- Add an optional scheduled_for column to the orders table.
- Preserve existing orders and their information.
- Test that immediate orders can still be saved and retrieved.

## Task 2: Add Scheduled Delivery Input

- Update POST /orders to accept an optional scheduled_for field.
- Store scheduled delivery times in UTC.
- Test requests with and without scheduled_for.

## Task 3: Validate Scheduled Delivery Times

- Reject delivery times less than 45 minutes from now.
- Reject delivery times more than 7 days from now.
- Accept exactly 45 minutes and exactly 7 days.
- Test all four boundary conditions using a fake clock.

## Task 4: Check Restaurant Operating Hours

- Compare the requested delivery time with the restaurant's opening and closing hours.
- Reject scheduled orders when the restaurant is closed.
- Test both open and closed restaurant scenarios.

## Task 5: Add Scheduled Order Status

- Create valid scheduled orders with status SCHEDULED.
- Keep immediate orders with status PLACED.
- Return scheduled_for when retrieving an order.
- Test that both types of orders have the correct status.

## Task 6: Implement Automatic Order Release

- Find scheduled orders that are within 30 minutes of delivery.
- Change eligible orders from SCHEDULED to PLACED.
- Use a conditional database update to prevent duplicate releases.
- Test before, at, and after the release threshold.

## Task 7: Implement Cancellation Rules

- Allow scheduled orders to be cancelled before release.
- Reject cancellation through the scheduled-order cancellation operation after release.
- Test both successful and rejected cancellations.

## Task 8: Add Automated Tests and Run Quality Checks

- Add pytest tests for the five baseline API endpoints.
- Add tests for scheduled orders and edge cases.
- Run all tests and fix failures.
- Run a Python linter and address reported issues.

## Task 9: Complete Project Documentation

- Update README.md with setup and run instructions.
- Create or update AGENTS.md with development guidance.
- Record genuine AI interactions and decisions in AI_LOG.md.
- Check Git history for at least six meaningful commits.

## Task 10: Prepare Final Submission

- Write the individual reflection.
- Export the reflection as a 1–2 page PDF.
- Prepare a short demonstration of the API.
- Verify that all required files are included.
