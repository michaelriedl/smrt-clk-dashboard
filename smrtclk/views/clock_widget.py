"""Clock widget for displaying analog clock."""

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import QFrame, QLabel, QWidget

from config.constants import (
    CLOCK_CENTER_Y_RATIO,
    CLOCK_FACE_IMAGE,
    CLOCK_FACE_SIZE_RATIO,
    DATE_FONT_SIZE_BASE,
    HOUR_HAND_IMAGE,
    MINUTE_HAND_IMAGE,
    SECOND_HAND_IMAGE,
)

from .styles import Styles


class ClockWidget(QWidget):
    """
    Widget for displaying an analog clock with date.

    Manages the clock face, hour/minute/second hands, and date display.
    Uses proper parent-child relationships for automatic memory management.
    """

    def __init__(self, parent: QWidget, config):
        """
        Initialize the clock widget.

        Args:
            parent: Parent widget
            config: Application configuration
        """
        super().__init__(parent)
        self.config = config

        self._clock_hands: dict = {}
        self._clockface: QFrame = None
        self._date_label: QLabel = None

        self._createClockFace()
        self._createClockHands()
        self._createDateDisplay()

    def _createClockFace(self) -> None:
        """Create the clock face background."""
        height = self.config.height
        width = self.config.width

        # Create clock face frame
        self._clockface = QFrame(self)
        self._clockface.setObjectName("clockface")

        # Calculate clock face position and size
        clock_size = int(height * CLOCK_FACE_SIZE_RATIO)
        clock_x = int(width / 2 - height * (CLOCK_FACE_SIZE_RATIO / 2))
        clock_y = int(
            height * CLOCK_CENTER_Y_RATIO - height * (CLOCK_FACE_SIZE_RATIO / 2)
        )

        self._clockrect = QRect(clock_x, clock_y, clock_size, clock_size)
        self._clockface.setGeometry(self._clockrect)

        # Apply clock face styling with image
        image_path = self.config.images_path / CLOCK_FACE_IMAGE
        self._clockface.setStyleSheet(Styles.get_clockface_style(str(image_path)))

    def _createClockHands(self) -> None:
        """Create hour, minute, and second hand widgets."""
        # Define hand types
        hands = [
            ("hour", HOUR_HAND_IMAGE),
            ("min", MINUTE_HAND_IMAGE),
            ("sec", SECOND_HAND_IMAGE),
        ]

        # Create each hand
        for hand_type, image_name in hands:
            self._clock_hands[hand_type] = {}

            # Create label for the hand
            label = QLabel(self)
            label.setObjectName(f"{hand_type}hand")
            label.setStyleSheet(Styles.get_transparent_style(f"{hand_type}hand"))

            # Load pixmaps (original and transformed)
            image_path = self.config.images_path / image_name
            original_pixmap = QPixmap(str(image_path))

            self._clock_hands[hand_type]["label"] = label
            self._clock_hands[hand_type]["pixmap"] = [original_pixmap, original_pixmap]

            # Initially position at 12 o'clock
            label.raise_()

    def _createDateDisplay(self) -> None:
        """Create the date display label."""
        self._date_label = QLabel(self)
        self._date_label.setObjectName("datex")

        # Calculate font size based on scale
        font_size = int(DATE_FONT_SIZE_BASE * self.config.xscale)
        self._date_label.setStyleSheet(Styles.get_text_style("datex", font_size))

        # Position at bottom center with padding to prevent cutoff
        self._date_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)  # ty: ignore[unresolved-attribute]
        self._date_label.setGeometry(0, 0, self.config.width, self.config.height - 5)

    def updateHand(self, hand_type: str, angle: float) -> None:
        """
        Update a clock hand to the specified angle.

        Args:
            hand_type: Type of hand ('hour', 'min', or 'sec')
            angle: Angle in degrees
        """
        if hand_type not in self._clock_hands:
            return

        hand = self._clock_hands[hand_type]
        original_pixmap = hand["pixmap"][0]
        label = hand["label"]

        # Scale and rotate the pixmap
        ts = original_pixmap.size()
        transform = QTransform()
        transform.scale(
            float(self._clockrect.width()) / ts.height(),
            float(self._clockrect.height()) / ts.height(),
        )
        transform.rotate(angle)

        transformed_pixmap = original_pixmap.transformed(
            transform,
            Qt.SmoothTransformation,  # ty: ignore[unresolved-attribute]
        )
        hand["pixmap"][1] = transformed_pixmap
        label.setPixmap(transformed_pixmap)

        # Center the hand on the clock face
        ts = transformed_pixmap.size()
        label.setGeometry(
            int(self._clockrect.center().x() - ts.width() / 2),
            int(self._clockrect.center().y() - ts.height() / 2),
            ts.width(),
            ts.height(),
        )

    def updateDate(self, date_string: str) -> None:
        """
        Update the date display.

        Args:
            date_string: Formatted date string
        """
        if self._date_label:
            self._date_label.setText(date_string)
