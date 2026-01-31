from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPixmap


class MinuteHand:
    def __init__(self, frame: QFrame):
        # Create a label for the minute hand
        self.label = QLabel(frame)
        self.label.setObjectName("minute_hand")
        self.label.setStyleSheet("#minute_hand { background-color: transparent; }")
        # Create the pixel map for the minute hand
        self.pixmap = QPixmap("src/clock/images/minute_hand.png")

    def get_angle(self):
        return self.minute * 6
