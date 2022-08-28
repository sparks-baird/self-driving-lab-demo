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

port = 5000

# Wait for connect or fail
max_wait = 10
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
    form_cookie = None
    message_cookie = None
    if request.method == "POST":
        form_cookie = str(list(request.form.values()))
        if "control_led" in request.form:
            form = request.form
            R = int(form["red"])
            G = int(form["green"])
            B = int(form["blue"])
            print(f"red: {R}, green: {G}, blue: {B}")

            pixels[0] = (R, G, B)
            pixels.write()

        response = redirect("/")  # type: ignore

    else:  # GET
        if "message" not in request.cookies:
            message_cookie = "Select a pin and an operation below."

        channel_names = [
            "ch415",
            "ch445",
            "ch480",
            "ch515",
            "ch560",
            "ch615",
            "ch670",
            "ch720",
        ]
        channel_dict = {
            ch: datum for ch, datum in zip(channel_names, sensor.all_channels)
        }

        R, G, B = pixels[0]
        color_dict = {"red": R, "green": G, "blue": B}

        def merge_two_dicts(x, y):
            z = x.copy()  # start with keys and values of x
            z.update(y)  # modifies z with keys and values of y
            return z

        response_dict = merge_two_dicts(color_dict, channel_dict)

        with open(template_fname, "r", encoding="utf-8") as template:
            with open(fname, "w", encoding="utf-8") as f:
                html_text = template.read()
                write_text = html_text % response_dict
                f.write(write_text)

        response = send_file(fname)  # type: ignore
    if form_cookie:
        response.set_cookie("form", form_cookie)
    if message_cookie:
        response.set_cookie("message", message_cookie)
    return response


app.run(debug=True)

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
