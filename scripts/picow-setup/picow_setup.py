import os
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import requests

# Install MicroPython

fpath = (
    ".\\scripts\\picow-setup\\rp2-pico-w-20230309-unstable-v1.19.1-953-gb336b6bb7.uf2"
)

os.system(f'copy "{fpath}" e:')

# Transfer sdl_demo.zip files
r = requests.get(
    "https://github.com/sparks-baird/self-driving-lab-demo/releases/latest"
)
print(r.url)
version = r.url.split("tag/")[-1]

sdl_demo_url = f"https://github.com/sparks-baird/self-driving-lab-demo/releases/download/{version}/sdl_demo.zip"  # noqa: E501

# https://stackoverflow.com/a/56951038/13697228
urllib.request.urlretrieve(sdl_demo_url, "sdl_demo.zip")

# https://stackoverflow.com/a/3451150/13697228
with zipfile.ZipFile("sdl_demo.zip", "r") as zip_ref:
    zip_ref.extractall("sdl_demo")

# https://stackoverflow.com/a/54585257/13697228
path = Path("sdl_demo/secrets.py")
text = path.read_text()
text = text.replace("Enter your SSID here", "Pixel_5861")
text = text.replace("Enter your WiFi password here", "b502619807fe")
path.write_text(text)

dmesg_text = subprocess.check_output(["wsl", "dmesg"])
serial_port_stem = "ttyS"
serial_port_num = str(dmesg_text).split()[1].split(" at I/O")[0]
serial_port = serial_port_stem + serial_port_num

# In WSL, run the following command manually:
# `sudo usermod -a -G dialout $USER`
# Then log out and log back in

# print(subprocess.check_call(["wsl", "dmesg", "|", "grep", "-o", '"tty.."']))
1 + 1
