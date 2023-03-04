# Response to Reviewer

> IN STAR-PROTOCOLS-D-23-00017 Baird and Sparks provide a wonderful example of a low cost tool that will allow educators to introduce their students to the concepts of a self-driving lab.  The manuscript is lovingly written (and the accompanying YouTube video is excellent even if it does illustrate that the authors have relatively poor musical sensibilities).

Thank you for the positive feedback! We are glad you enjoyed the manuscript and the
video, and the music stems in part from Sterling's past life as a breakdancer. Thanks
for bearing through it ;)

> The authors carefully followed the Protocol Template with section name and timings. They included a Key Resources table that included direct links to a digikey order.  I can't guarantee that those links work forever, but for right now they function.

Agreed, we hope the links will last, and we will try to check back periodically to ensure
working links.

> The steps (as written) are reasonably easy to follow. I personally find that words don't do a great job of describing physical builds and that their manuscript could have been more like Ikea instructions to promote clarity.  I would suggest that the YouTube video be explicitly called out as I found that to be very instructive.

I think making the build instructions more like Ikea
instructions is a great idea. We will try to incorporate this into future manuscripts.
Great suggestion about including the video. We have added that as the last sentence to
the Summary section to make it prominent.

> I really only have two major concerns for this protocol:

> 1. Folks will have versions of Python on their computer already and there may be some hesitancy around downloading Thonny and a new version of Python.  I tried pip installing thonny and it did some things with my packages which may or may not have broken my Python Environment.  Is there a MicroPython IDE that is compatible with Anaconda?  This will make folks like me more comfortable.  This might be a good split point (or an opportunity to remind folks that they should have (and use) an experimental environment for things like this.

This is a great point. From what I can tell, when Thonny is installed, it installs it's
own Python version (for mine, it is installed at
`C:\Users\<username>\AppData\Local\Programs\Thonny\python.exe`.

I use Miniconda instead of Anaconda distribution, so the package conflicts may not
appear on mine, but I gave the
`pip` installation procedure a try, and it seems to work OK in a fresh conda environment:
```bash
conda create -n sdl-demo-thonny python==3.10.*
conda activate sdl-demo-thonny
pip install self-driving-lab-demo thonny
thonny
```

Additional content has been added related to this.


> 2. I found sections on MongoDB and HiveMQ confusing in that they are labeled optional but the troubleshooting makes them almost seem mandatory? Likewise the YouTube video seems to make it mandatory. This part could be further clarified.

Thanks for the great suggestion. This has been clarified in both places as follows:

> a. (Optional) Set up a MongoDB database backend. If ignored, the demo will function, just without logging data to a database (i.e., the user becomes responsible for saving the data on the client side).
> ...
> b. (Optional) Create your own HiveMQ instance. If this setup is ignored, the demo will
> function properly; however, the hardware commands and sensor data will be transmitted
> via a default HiveMQ instance for which the credentials are public. Setting up your
> own HiveMQ instance ensures that the data you transfer remains private and secure.
> Other MQTT brokers such as Mosquitto or Adafruit IO are available. At the time of
> writing, we recommend HiveMQ because it provides free instances with generous limits. Setting up a private MQTT broker is in line with best practices for internet of things (IoT) security.

At the time the video was made, the MongoDB data logging was not implemented, and
test.mosquitto.org was being used as the MQTT broker, meaning anyone could be listening
in and even sending commands to the device. The switch to HiveMQ was to allow for a free
way to set up a private MQTT broker in order to follow [best practices for IoT security](https://iot.stackexchange.com/questions/554/is-there-any-advantage-in-encrypting-sensor-data-that-is-not-private).

> I think this is a really awesome project and it is unfortunate that I couldn't get all
> of the pieces together in time to have my students do an en masse build.  I will
> continue to interact with the authors moving forward and can hopefully provide them

Thank you for the great review, and we look forward to our future interactions.
