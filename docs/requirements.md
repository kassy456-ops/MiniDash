
# MiniDash — Track A: Scheduled Orders

## Feature Overview

MiniDash will allow customers to schedule food orders for future delivery instead of placing only immediate orders.

## User Stories

1. As a customer, I want to choose a future delivery time so that my food arrives when I need it.

2. As a customer, I want to know when a scheduled delivery time is invalid so that I can select an acceptable time.

3. As a customer, I want to schedule an order only when the restaurant is open so that my order can be fulfilled.

4. As a customer, I want to cancel a scheduled order before it is released so that I can change my plans.

5. As the system, I want to release scheduled orders automatically so that restaurants have time to prepare them.

## Acceptance Criteria (EARS Format)

1. **Optional scheduling:** When a customer places an order without a scheduled delivery time, the system shall create an order with status `PLACED`.

2. **Minimum scheduling time:** When a customer requests delivery less than 45 minutes from the current time, the system shall reject the request.

3. **Maximum scheduling time:** When a customer requests delivery more than 7 days from the current time, the system shall reject the request.

4. **Restaurant availability:** When a customer requests scheduled delivery outside the restaurant's operating hours, the system shall reject the request.

5. **Scheduled status:** When a customer places a valid scheduled order, the system shall save it with status `SCHEDULED`.

6. **Automatic release:** When a scheduled order reaches 30 minutes before its requested delivery time, the system shall change its status to `PLACED`.

7. **Exactly-once release:** While processing scheduled orders, the system shall prevent an order from being released more than once.

8. **Cancellation:** When a customer cancels a scheduled order before its release time, the system shall change its status to `CANCELLED`.

9. **Cancellation restriction:** When a customer attempts to cancel a scheduled order after it has been released, the system shall reject the cancellation through the scheduled-order cancellation operation.

10. **Testable time:** The system shall use an injectable clock for scheduling calculations so tests can control the current time.

## Out of Scope

- Group ordering
- Live driver tracking
- Payment processing
- User authentication
- A customer-facing website or mobile application
