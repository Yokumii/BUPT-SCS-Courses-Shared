from datetime import datetime, timedelta


class TimeService:
    def __init__(self):
        self._offset = timedelta(0)

    def now(self) -> datetime:
        return datetime.now() + self._offset

    def advance(self, minutes: int) -> datetime:
        self._offset += timedelta(minutes=minutes)
        return self.now()

    def reset(self) -> datetime:
        self._offset = timedelta(0)
        return self.now()


time_service = TimeService()
