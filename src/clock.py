# Provides date and time tools in UTC.
from datetime import datetime, timezone


# Returns the actual current time when MiniDash is running.
class Clock:
    def now(self):
        return datetime.now(timezone.utc)


# Allows tests to control the current time.
# This makes it possible to test scheduling rules without waiting.
class FakeClock:
    def __init__(self, fixed_time):
        self.fixed_time = fixed_time

    def now(self):
        return self.fixed_time