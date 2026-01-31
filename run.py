import sys
import datetime
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel

import json
from PyQt5 import QtNetwork
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtNetwork import QNetworkRequest

import keys


def move_hand(hand, now):
    # Calculate the angle to maove the hand
    if hand == "hour":
        angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
    elif hand == "min":
        angle = now.minute * 6
    else:
        angle = now.second * 6
    # Move the hand the appropriate angle
    ts = clock_hands[hand]["pixmap"][0].size()
    clock_hands[hand]["pixmap"][1] = clock_hands[hand]["pixmap"][0].transformed(
        QTransform()
        .scale(
            float(clockrect.width()) / ts.height(),
            float(clockrect.height()) / ts.height(),
        )
        .rotate(angle),
        Qt.SmoothTransformation,
    )
    clock_hands[hand]["label"].setPixmap(clock_hands[hand]["pixmap"][1])
    ts = clock_hands[hand]["pixmap"][1].size()
    clock_hands[hand]["label"].setGeometry(
        int(clockrect.center().x() - ts.width() / 2),
        int(clockrect.center().y() - ts.height() / 2),
        ts.width(),
        ts.height(),
    )


def tick():
    # Use the global variable
    global lastmin, lastday
    # Get the current time
    now = datetime.datetime.now()
    # Update the second hand
    move_hand("sec", now)
    # If the minute has changed, update the minute and hour hand
    if now.minute != lastmin:
        # Update the global variable
        lastmin = now.minute
        # Update the minute hand
        move_hand("min", now)
        # Update the hour hand
        move_hand("hour", now)
    # If the day has changed, update the date
    if now.day != lastday:
        # Update the global variable
        lastday = now.day
        # Get the super script
        sup = "th"
        if now.day == 1 or now.day == 21 or now.day == 31:
            sup = "st"
        if now.day == 2 or now.day == 22:
            sup = "nd"
        if now.day == 3 or now.day == 23:
            sup = "rd"
        # Update the date
        ds = "{0:%A %B} {0.day}<sup>{1}</sup> {0.year}".format(now, sup)
        datex.setText(ds)
        # Update the weather
        get_weather()


def get_weather():
    # Create the URL
    url = QUrl(
        "https://api.openweathermap.org/data/2.5/onecall?"
        + "lat="
        + lat
        + "&lon="
        + lon
        + "&units=imperial"
        + "&exclude=minutely,alerts&appid="
        + keys.owm_api
    )
    # Create the network request
    req = QNetworkRequest(url)
    # Get the request
    manager.get(req)


def wxupdate(reply):
    if reply.error() != QNetworkReply.NoError:
        return
    tempstr = str(reply.readAll(), "utf-8")
    tempdata = json.loads(tempstr)
    # Update the sunrise and sunset
    sunrise = datetime.datetime.fromtimestamp(tempdata["current"]["sunrise"])
    sunset = datetime.datetime.fromtimestamp(tempdata["current"]["sunset"])
    sun_text["rise"].setText(sunrise.strftime("%I:%M %p"))
    sun_text["set"].setText(sunset.strftime("%I:%M %p"))
    # Update the temperature
    cur_temp = tempdata["current"]["temp"]
    min_temp = min((tempdata["daily"][0]["temp"]["min"], cur_temp))
    max_temp = max((tempdata["daily"][0]["temp"]["max"], cur_temp))
    temp_text["min"].setText("%2.2f" % min_temp + "\u00b0")
    temp_text["max"].setText("%2.2f" % max_temp + "\u00b0")
    temp_diff = (cur_temp - min_temp) / (max_temp - min_temp)
    sliders["tempslide"]["label"].setGeometry(10, int(-190 * temp_diff), 40, 272)
    temp_text["cur"].setGeometry(40, int(100 - 190 * temp_diff - 3), width, height)
    temp_text["cur"].setText("%2.2f" % cur_temp + "\u00b0")
    # Update the precipitation
    cur_pop = int(tempdata["hourly"][0]["pop"] * 100)
    max_pop = int(max((tempdata["daily"][0]["pop"] * 100, cur_pop)))
    prec_text["min"].setText("0%")
    prec_text["max"].setText(str(max_pop) + "%")
    if max_pop == 0:
        pop_diff = 0
    else:
        pop_diff = cur_pop / max_pop
    sliders["precslide"]["label"].setGeometry(430, int(-190 * pop_diff), 40, 272)
    prec_text["cur"].setGeometry(-40, int(100 - 190 * pop_diff - 3), width, height)
    prec_text["cur"].setText(str(cur_pop) + "%")


# Set the size of the screen
height = 272
width = 480

# Set scale factors
xscale = float(width) / 1440.0
yscale = float(height) / 900.0

# Set the latitude and longitude for the weather
lat = "40.0931191"
lon = "-83.017962"

# Initialize update trackers
lastmin = -1
lastday = -1

# Initialize the app
app = QApplication(sys.argv)

# Initialize and size the widget
w = QWidget()
w.setCursor(Qt.BlankCursor)
w.resize(width, height)

# Add the background frame
background = QFrame(w)
background.setObjectName("background")
background.setGeometry(0, 0, width, height)
background.setStyleSheet(
    "#background { background-color: black; border-image: url("
    + "./images/clockbackground_small.png"
    + ") 0 0 0 0 stretch stretch;}"
)

# Add the foreground frame
foreground = QFrame(background)
foreground.setObjectName("foreground")
foreground.setStyleSheet("#foreground { background-color: transparent; }")
foreground.setGeometry(0, 0, width, height)

# Add the clock face
clockface = QFrame(foreground)
clockface.setObjectName("clockface")
clockrect = QRect(
    int(width / 2 - height * 0.4),
    int(height * 0.45 - height * 0.4),
    int(height * 0.8),
    int(height * 0.8),
)
clockface.setGeometry(clockrect)
clockface.setStyleSheet(
    "#clockface { background-color: transparent; border-image: url("
    + "./images/clockface3.png"
    + ") 0 0 0 0 stretch stretch;}"
)

# Add the clock hands
clock_hands = {}
clock_hands["hour"] = {}
clock_hands["hour"]["label"] = QLabel(foreground)
clock_hands["hour"]["label"].setObjectName("hourhand")
clock_hands["hour"]["label"].setStyleSheet(
    "#hourhand { background-color: transparent; }"
)
clock_hands["min"] = {}
clock_hands["min"]["label"] = QLabel(foreground)
clock_hands["min"]["label"].setObjectName("minhand")
clock_hands["min"]["label"].setStyleSheet("#minhand { background-color: transparent; }")
clock_hands["sec"] = {}
clock_hands["sec"]["label"] = QLabel(foreground)
clock_hands["sec"]["label"].setObjectName("sechand")
clock_hands["sec"]["label"].setStyleSheet("#sechand { background-color: transparent; }")

# Add the pixel maps for updating the clock hands
clock_hands["hour"]["pixmap"] = []
clock_hands["hour"]["pixmap"].append(QPixmap("./images/hourhand.png"))
clock_hands["hour"]["pixmap"].append(QPixmap("./images/hourhand.png"))
clock_hands["min"]["pixmap"] = []
clock_hands["min"]["pixmap"].append(QPixmap("./images/minhand.png"))
clock_hands["min"]["pixmap"].append(QPixmap("./images/minhand.png"))
clock_hands["sec"]["pixmap"] = []
clock_hands["sec"]["pixmap"].append(QPixmap("./images/sechand.png"))
clock_hands["sec"]["pixmap"].append(QPixmap("./images/sechand.png"))

# Add the date
datex = QLabel(foreground)
datex.setObjectName("datex")
datex.setStyleSheet(
    "#datex { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(70 * xscale))
    + "px; }"
)
datex.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
datex.setGeometry(0, -10, width, height)

# Add the sunrise and sunset icons
sricon = QLabel(foreground)
sricon.setObjectName("sricon")
sricon.setStyleSheet("#sricon { background-color: transparent; }")
sricon.setGeometry(100, 10, int(150 * xscale), int(150 * yscale))
sriconpixmap = QPixmap("./images/sun-rise.png")
sricon.setPixmap(
    sriconpixmap.scaled(
        sricon.width(), sricon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
    )
)
ssicon = QLabel(foreground)
ssicon.setObjectName("ssicon")
ssicon.setStyleSheet("#ssicon { background-color: transparent; }")
ssicon.setGeometry(int(380 - 150 * xscale), 10, int(150 * xscale), int(150 * yscale))
ssiconpixmap = QPixmap("./images/sun-rise.png")
ssicon.setPixmap(
    ssiconpixmap.scaled(
        ssicon.width(), ssicon.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
    )
)

# Add the sunrise and sunset text
sun_text = {}
sun_text["rise"] = QLabel(foreground)
sun_text["rise"].setObjectName("srtext")
sun_text["rise"].setStyleSheet(
    "#srtext { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(40 * xscale))
    + "px; }"
)
sun_text["rise"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
sun_text["rise"].setGeometry(int(-140 + 150 * xscale // 2), -88, width, height)
sun_text["set"] = QLabel(foreground)
sun_text["set"].setObjectName("sstext")
sun_text["set"].setStyleSheet(
    "#sstext { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(40 * xscale))
    + "px; }"
)
sun_text["set"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
sun_text["set"].setGeometry(int(140 - 150 * xscale // 2), -88, width, height)

# Add the temperature and precipitation bars
temp_bar = QLabel(foreground)
temp_bar.setObjectName("tempbar")
temp_bar.setStyleSheet("#tempbar { background-color: transparent; }")
temp_bar.setGeometry(10, 0, 40, 272)
temp_bar.setPixmap(QPixmap("./images/slider-bar.png"))
prec_bar = QLabel(foreground)
prec_bar.setObjectName("precbar")
prec_bar.setStyleSheet("#precbar { background-color: transparent; }")
prec_bar.setGeometry(430, 0, 40, 272)
prec_bar.setPixmap(QPixmap("./images/slider-bar.png"))

# Add the temperature and precipitation sliders
sliders = {}
sliders["tempslide"] = {}
sliders["tempslide"]["label"] = QLabel(foreground)
sliders["tempslide"]["label"].setObjectName("tempslide")
sliders["tempslide"]["label"].setStyleSheet(
    "#tempslide { background-color: transparent; }"
)
sliders["tempslide"]["label"].setGeometry(10, -100, 40, 272)
sliders["tempslide"]["label"].setPixmap(QPixmap("./images/slider.png"))
sliders["precslide"] = {}
sliders["precslide"]["label"] = QLabel(foreground)
sliders["precslide"]["label"].setObjectName("precslide")
sliders["precslide"]["label"].setStyleSheet(
    "#precslide { background-color: transparent; }"
)
sliders["precslide"]["label"].setGeometry(430, -100, 40, 272)
sliders["precslide"]["label"].setPixmap(QPixmap("./images/slider.png"))

# Add the temperature text
temp_text = {}
temp_text["min"] = QLabel(foreground)
temp_text["min"].setObjectName("tempmin")
temp_text["min"].setStyleSheet(
    "#tempmin { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(50 * xscale))
    + "px; }"
)
temp_text["min"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
temp_text["min"].setGeometry(-206, 115, width, height)
temp_text["max"] = QLabel(foreground)
temp_text["max"].setObjectName("tempmax")
temp_text["max"].setStyleSheet(
    "#tempmax { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(50 * xscale))
    + "px; }"
)
temp_text["max"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
temp_text["max"].setGeometry(-206, -115, width, height)
temp_text["cur"] = QLabel(foreground)
temp_text["cur"].setObjectName("tempcur")
temp_text["cur"].setStyleSheet(
    "#tempcur { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(45 * xscale))
    + "px; }"
)
temp_text["cur"].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
temp_text["cur"].setGeometry(45, -115, width, height)

# Add the precipitation text
prec_text = {}
prec_text["min"] = QLabel(foreground)
prec_text["min"].setObjectName("precmin")
prec_text["min"].setStyleSheet(
    "#precmin { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(50 * xscale))
    + "px; }"
)
prec_text["min"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
prec_text["min"].setGeometry(210, 115, width, height)
prec_text["max"] = QLabel(foreground)
prec_text["max"].setObjectName("precmax")
prec_text["max"].setStyleSheet(
    "#precmax { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(50 * xscale))
    + "px; }"
)
prec_text["max"].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
prec_text["max"].setGeometry(210, -115, width, height)
prec_text["cur"] = QLabel(foreground)
prec_text["cur"].setObjectName("preccur")
prec_text["cur"].setStyleSheet(
    "#preccur { font-family:sans-serif; color: "
    + "#bef"
    + "; background-color: transparent; font-size: "
    + str(int(45 * xscale))
    + "px; }"
)
prec_text["cur"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
prec_text["cur"].setGeometry(-45, -115, width, height)

# Start the clock timer
ctimer = QTimer()
ctimer.timeout.connect(tick)
ctimer.start(1000)

# Start the weather update timer
wtimer = QTimer()
wtimer.timeout.connect(get_weather)
wtimer.start(1000 * 60 * 5)

# Create the network manager
manager = QtNetwork.QNetworkAccessManager()
# Attach the weather interface update function
manager.finished.connect(wxupdate)

# Show the widget, add the exit, and launch the app
w.show()
sys.exit(app.exec_())
