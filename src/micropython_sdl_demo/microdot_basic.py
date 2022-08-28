"""Create a server with a server shutdown button. Access at http://<ip>:5000/"""
import time
from secrets import PASSWORD, SSID

import network
from microdot import Microdot

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

port = 5000  # default is 5000, but hard-coded here to print URL later

# Wait for connect or fail
max_wait = 10
while max_wait > 0:  # type: ignore
    if wlan.status() < 0 or wlan.status() >= 3:  # type: ignore
        break
    max_wait -= 1
    print("waiting for connection...")
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:  # type: ignore
    raise RuntimeError("network connection failed")
else:
    print("connected")
    status = wlan.ifconfig()
    ip = status[0]  # type: ignore
    print(f"ip: {ip}")
    print(f"In a browser, navigate to: http://{ip}:{port}/")

app = Microdot()

htmldoc = """<!DOCTYPE html>
<html>
    <head>
        <title>Microdot Example Page</title>
    </head>
    <body>
        <div>
            <h1>Microdot Example Page</h1>
            <p>Hello from Microdot!</p>
            <p><a href="/shutdown">Click to shutdown the server</a></p>
        </div>
    </body>
</html>
"""


@app.route("/")
def hello(request):
    return htmldoc, 200, {"Content-Type": "text/html"}


@app.route("/shutdown")
def shutdown(request):
    request.app.shutdown()
    return "The server is shutting down..."


app.run(debug=True, port=port)
