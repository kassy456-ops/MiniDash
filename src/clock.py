from datetime import datetime, timezone


class Clock:
    def now(self):
        return datetime.now(timezone.utc)


class FakeClock:
    def __init__(self, fixed_time):
        self.fixed_time = fixed_time

    def now(self):
        return self.fixed_time