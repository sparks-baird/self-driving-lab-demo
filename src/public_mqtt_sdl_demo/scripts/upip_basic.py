from secrets import PASSWORD, SSID

from netman import connectWiFi

connectWiFi(SSID, PASSWORD, country="US")

import upip

# upip.install("micropython-umqtt.simple2")
# upip.install("micropython-umqtt.robust2")
upip.install("micropython-umqtt.robust")
