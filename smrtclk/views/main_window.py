"""Main window for Smart Clock Dashboard."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QMainWindow, QWidget

from config.constants import BACKGROUND_IMAGE
from config.settings import Config
from smrtclk.controllers.clock_controller import ClockController
from smrtclk.models.clock_model import ClockModel

from .clock_widget import ClockWidget
from .styles import Styles


class ClockMainWindow(QMainWindow):
    """
    Main window for the Smart Clock Dashboard application.

    This is the top-level window that contains all clock and weather widgets.
    Follows PyQt5 best practices with proper parent-child relationships and
    separation of concerns.
    """

    def __init__(self, config: Config):
        """
        Initialize the main window.

        Args:
            config: Application configuration object
        """
        super().__init__(parent=None)
        self.config = config

        # Initialize controllers
        self.clock_controller = None

        self._setupWindow()
        self._createCentralWidget()
        self._createWidgets()
        self._createLayout()
        self._setupControllers()

    def _setupWindow(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle("Smart Clock Dashboard")
        self.setFixedSize(self.config.width, self.config.height)
        self.setCursor(Qt.BlankCursor)

    def _createCentralWidget(self) -> None:
        """Create and set the central widget."""
        # Create main widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create background frame
        self.background = QFrame(central_widget)
        self.background.setObjectName("background")
        self.background.setGeometry(0, 0, self.config.width, self.config.height)

        # Apply background styling with image
        image_path = self.config.images_path / BACKGROUND_IMAGE
        self.background.setStyleSheet(Styles.get_background_style(str(image_path)))

        # Create foreground frame for widgets
        self.foreground = QFrame(self.background)
        self.foreground.setObjectName("foreground")
        self.foreground.setStyleSheet(Styles.get_transparent_style("foreground"))
        self.foreground.setGeometry(0, 0, self.config.width, self.config.height)

    def _createWidgets(self) -> None:
        """Create all child widgets (clock, weather, etc.)."""
        # Create clock widget
        self.clock_widget = ClockWidget(self.foreground, self.config)

        # TODO: Create WeatherWidget when ready

    def _createLayout(self) -> None:
        """Set up layout managers for widgets."""
        # For analog clock, we use absolute positioning due to the nature
        # of the rotating hands and precise clock face alignment.
        # The clock widget handles its own internal positioning.
        pass

    def _setupControllers(self) -> None:
        """Initialize and start all controllers."""
        # Create clock model and controller
        clock_model = ClockModel()
        self.clock_controller = ClockController(clock_model, self.clock_widget)

        # Start the clock
        self.clock_controller.start()

        # Trigger initial update to show current time immediately
        clock_model.update_time()

    def closeEvent(self, event) -> None:
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Stop all controllers and cleanup resources
        if self.clock_controller:
            self.clock_controller.stop()

        super().closeEvent(event)
