"""Clock controller for managing clock updates."""

from PyQt5.QtCore import QObject, QTimer, pyqtSlot

from config.constants import CLOCK_UPDATE_INTERVAL
from smrtclk.models.clock_model import ClockModel
from smrtclk.views.clock_widget import ClockWidget


class ClockController(QObject):
    """
    Controller for managing clock updates.

    Connects the ClockModel to the ClockWidget, managing the timer
    for regular updates and signal/slot connections.
    """

    def __init__(self, model: ClockModel, view: ClockWidget):
        """
        Initialize the clock controller.

        Args:
            model: Clock model instance
            view: Clock widget instance
        """
        super().__init__()
        self.model = model
        self.view = view
        self._timer = QTimer(self)

        self._connectSignals()
        self._setupTimer()

    def _connectSignals(self) -> None:
        """Connect model signals to view update methods."""
        # Update second hand on every time change
        self.model.timeChanged.connect(self._updateSecondHand)
        # Update minute and hour hands when minute changes
        self.model.minuteChanged.connect(self._updateMinuteHand)
        # Update date display when day changes
        self.model.dayChanged.connect(self._updateDate)

    def _setupTimer(self) -> None:
        """Configure and start the update timer."""
        self._timer.setInterval(CLOCK_UPDATE_INTERVAL)
        self._timer.timeout.connect(self._onTimerTick)

    def start(self) -> None:
        """Start the clock update timer."""
        self._timer.start()

    def stop(self) -> None:
        """Stop the clock update timer."""
        self._timer.stop()

    @pyqtSlot()
    def _onTimerTick(self) -> None:
        """Handle timer tick event."""
        # Update model, which will emit signals to update the view
        self.model.update_time()

    @pyqtSlot()
    def _updateSecondHand(self) -> None:
        """Update the second hand position."""
        angle = self.model.calculate_hand_angle("sec")
        self.view.updateHand("sec", angle)

    @pyqtSlot()
    def _updateMinuteHand(self) -> None:
        """Update the minute and hour hand positions."""
        # Update minute hand
        min_angle = self.model.calculate_hand_angle("min")
        self.view.updateHand("min", min_angle)
        # Update hour hand
        hour_angle = self.model.calculate_hand_angle("hour")
        self.view.updateHand("hour", hour_angle)

    @pyqtSlot()
    def _updateDate(self) -> None:
        """Update the date display."""
        date_string = self.model.get_formatted_date()
        self.view.updateDate(date_string)
