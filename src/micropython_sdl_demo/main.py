from secrets import PASSWORD, SSID
from time import sleep

import network
from as7341_sensor import Sensor
from machine import Pin
from microdot import Microdot, redirect, send_file
from neopixel import NeoPixel

pixels = NeoPixel(Pin(28), 1)  # 1 pixel on Pin 28

sensor = Sensor()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

port = 80

# Wait for connect or fail
max_wait = 30
while max_wait > 0:  # type: ignore
    if wlan.status() < 0 or wlan.status() >= 3:  # type: ignore
        break
    max_wait -= 1
    print("waiting for connection...")
    sleep(1)

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

template_fname = "sdl-demo-template.html"
fname = "sdl-demo.html"


@app.route("/", methods=["GET", "POST"])
def index(request):
    rgb_cookie = None
    sensor_cookie = None
    if request.method == "POST":
        form = request.form
        rgb_cookie = {
            "red": int(form["red"]),
            "green": int(form["green"]),
            "blue": int(form["blue"]),
            "astep": int(form["astep"]),
            "atime": int(form["atime"]),
            "gain": int(form["gain"]),
        }
        if "control_led" in form:
            keys = ["red", "green", "blue", "astep", "atime", "gain"]
            R, G, B, astep, atime, gain = [rgb_cookie[key] for key in keys]
            print(
                f"red: {R}, green: {G}, blue: {B}, astep: {astep}, atime: {atime}, gain: {gain}"  # noqa: E501
            )

            pixels[0] = (R, G, B)
            pixels.write()
            sensor._astep = astep
            sensor._atime = atime
            sensor._gain = gain

        response = redirect("/")  # type: ignore

    else:  # GET
        channel_names = [
            "ch410",
            "ch440",
            "ch470",
            "ch510",
            "ch550",
            "ch583",
            "ch620",
            "ch670",
        ]
        channel_dict = {
            ch: datum for ch, datum in zip(channel_names, sensor.all_channels)  # type: ignore
        }
        print(channel_dict)
        sensor_cookie = channel_dict

        R, G, B = pixels[0]
        atime = sensor._atime
        astep = sensor._astep
        gain = sensor._gain
        input_dict = {
            "red": R,
            "green": G,
            "blue": B,
            "atime": atime,
            "astep": astep,
            "gain": gain,
        }

        def merge_two_dicts(x, y):
            z = x.copy()  # start with keys and values of x
            z.update(y)  # modifies z with keys and values of y
            return z

        response_dict = merge_two_dicts(input_dict, channel_dict)

        with open(template_fname, "r", encoding="utf-8") as template:
            with open(fname, "w", encoding="utf-8") as f:
                html_text = template.read()
                write_text = html_text % response_dict
                f.write(write_text)

        response = send_file(fname)  # type: ignore
    if rgb_cookie:
        response.set_cookie("rgb", rgb_cookie)
    if sensor_cookie:
        response.set_cookie("sensor_data", sensor_cookie)
    return response


app.run(debug=False, port=port)

# %% Code Graveyard
# form_cookie = f"{request.form['brightness']},{request.form['pull']}"

# if request.form["pull"] == "pullup":
#     pull = machine.Pin.PULL_UP
# elif request.form["pull"] == "pulldown":
#     pull = machine.Pin.PULL_DOWN
# pin = machine.Pin(int(request.form["pin"]), machine.Pin.IN, pull)
# message_cookie = "Input pin {pin} is {state}.".format(
#     pin=request.form["pin"], state="high" if pin.value() else "low"
# )


# else:
#     pin = Pin(int(request.form["pin"]), Pin.OUT)
#     value = 0 if "set-low" in request.form else 1
#     pin.value(value)
#     message_cookie = "Output pin {pin} is now {state}.".format(
#         pin=request.form["pin"], state="high" if value else "low"
#     )

# response = redirect("/")  # type: ignore

# if "message" not in request.cookies:
#     message_cookie = "Select a pin and an operation below."
