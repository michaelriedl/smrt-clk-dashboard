"""Clock model for managing time and clock state."""

import datetime

from PyQt5.QtCore import QObject, pyqtSignal


class ClockModel(QObject):
    """
    Model for managing clock state and time calculations.

    Tracks current time, last updated minute/day, and provides
    methods for calculating clock hand angles.

    Signals:
        timeChanged: Emitted when time is updated
        minuteChanged: Emitted when minute changes
        dayChanged: Emitted when day changes
    """

    # Signals
    timeChanged = pyqtSignal(datetime.datetime)
    minuteChanged = pyqtSignal(datetime.datetime)
    dayChanged = pyqtSignal(datetime.datetime)

    def __init__(self):
        """Initialize the clock model."""
        super().__init__()
        self._current_time: datetime.datetime = datetime.datetime.now()
        self._last_minute: int = -1
        self._last_day: int = -1

    @property
    def current_time(self) -> datetime.datetime:
        """Get the current time."""
        return self._current_time

    @property
    def last_minute(self) -> int:
        """Get the last recorded minute."""
        return self._last_minute

    @property
    def last_day(self) -> int:
        """Get the last recorded day."""
        return self._last_day

    def update_time(self) -> None:
        """
        Update the current time and emit appropriate signals.

        Emits timeChanged always, minuteChanged when minute changes,
        and dayChanged when day changes.
        """
        self._current_time = datetime.datetime.now()
        self.timeChanged.emit(self._current_time)

        # Check if minute has changed
        if self._current_time.minute != self._last_minute:
            self._last_minute = self._current_time.minute
            self.minuteChanged.emit(self._current_time)

        # Check if day has changed
        if self._current_time.day != self._last_day:
            self._last_day = self._current_time.day
            self.dayChanged.emit(self._current_time)

    def calculate_hand_angle(self, hand_type: str) -> float:
        """
        Calculate the angle for a clock hand.

        Args:
            hand_type: Type of hand ('hour', 'min', or 'sec')

        Returns:
            Angle in degrees for the specified hand
        """
        now = self._current_time

        if hand_type == "hour":
            # Hour hand: 30 degrees per hour + 0.5 degrees per minute
            return ((now.hour % 12) + now.minute / 60.0) * 30.0
        elif hand_type == "min":
            # Minute hand: 6 degrees per minute
            return now.minute * 6.0
        elif hand_type == "sec":
            # Second hand: 6 degrees per second
            return now.second * 6.0
        else:
            return 0.0

    def get_formatted_date(self) -> str:
        """
        Get formatted date string with ordinal suffix.

        Returns:
            Formatted date string (e.g., "Monday February 1st 2026")
        """
        now = self._current_time

        # Determine ordinal suffix
        day = now.day
        if day in (1, 21, 31):
            suffix = "st"
        elif day in (2, 22):
            suffix = "nd"
        elif day in (3, 23):
            suffix = "rd"
        else:
            suffix = "th"

        # Format: "Monday February 1st 2026"
        return f"{now:%A %B} {day}<sup>{suffix}</sup> {now.year}"
