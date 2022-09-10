# Notebook Tutorials and Demonstrations

This is a collection of tutorial notebooks and demonstrations for the
self-driving-lab-demo! These notebooks will start by going over the hardware basics of the LEDs and
sensor (`Blinkt! Getting Started`) and testing out different search algorithms with the bonus of
designing a simulation (`Search Algorithms using Blinkt!`). Rather than edit the notebooks ad-hoc when
something goes wrong, it can be more instructive to see the behind-the-scenes
development process, mistakes and all! Not every mistake will be instructive, so I try
to leave only the ones that teach important principals related to self-driving
laboratories such as validating results and troubleshooting software-hardware
interfacing. Next comes the use of the PicoW-SDL-Demo via hosting a local web server (`Pico W / MicroPython implementation`) and
then using Internet-of-things-style communication to remotely control the PicoW
(`Controlling the Pico W Remotely (IoT-style)`). There is also a notebook on controlling
the Pico using a nonwireless option (i.e. compatible when WiFi is not available /
difficult to connect to or when nonwireless Pico is being used).

## 1.* Blinkt! Getting Started

- [`1.0-sgb-blinkt-as7341-basic.ipynb`](1.0-sgb-blinkt-as7341-basic.ipynb)
  - > Let's flash the LED and print out the sensor data!

## 2.* Search Algorithms using Blinkt!

- [`2.0-random-search.ipynb`](2.0-random-search.ipynb)
  - > 🚗 Let's run a test drive of 100 random search iterations! 🚗
- [`2.1-bayesian-optimization-blooper.ipynb`](2.1-bayesian-optimization-blooper.ipynb)
   - > 💥Bayesian optimization is worse than random search and grid search.. Wait what?💥
- [`2.2-sensor-simulator.ipynb`](2.2-sensor-simulator.ipynb)
  - > 🕵️ Time to troubleshoot! Running simulations can help us to troubleshoot the source
    > of the discrepancy. SPOILER: Oh! It was an issue with data processing 🤦 (but was that
    > all? 🤨)
- [`2.3-bayesian-optimization.ipynb`](2.3-bayesian-optimization.ipynb)
  - > 🔁 Back to the algorithm comparison experiments! Lo and behold, Bayesian
    > optimization is the most efficient. 😌

## 3.* Pico W / MicroPython implementation
- [`3.1-random-vs-grid-vs-bayesian.ipynb`](3.1-random-vs-grid-vs-bayesian.ipynb)
  - > 🥑 Algorithm comparison using the Pico W that's running a local web server 🥑
- [`3.2-random-vs-grid-vs-bayesian-simulator.ipynb`](3.2-random-vs-grid-vs-bayesian-simulator.ipynb)
  - > 🥑 Algorithm comparison using a vamped up simulation based on the NeoPixel
    > (as opposed to DotStar) LED 🥑

## 4.* Controlling the Pico W Remotely (IoT-style)
  - [`4.0-paho-mqtt-colab-sdl-demo.ipynb`](4.0-paho-mqtt-colab-sdl-demo.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.0-paho-mqtt-colab-sdl-demo.ipynb)
  - > 📡 Control the Pico W remotely using [MQTT (The Standard for IoT Messaging)](https://mqtt.org/) 📡
  - [`4.1-paho-mqtt-colab-sdl-demo-search.ipynb`](4.1-paho-mqtt-colab-sdl-demo-search.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.1-paho-mqtt-colab-sdl-demo-search.ipynb)
  - > 🔁 Run the same algorithm comparison experiments controlled from the cloud! 🔁

## 5.* Nonwireless Control of Pico
  - [`5.0-nonwireless-search.ipynb`](5.0-nonwireless-search.ipynb)
  - > No PicoW? No problem! 🤖 Run the same algorithm comparison experiments using a nonwireless Pico! 🤖

## More to come!

- multi-fidelity optimization (simulation and experiments)
- high-dimensional Bayesian optimization
- asynchronous/batch optimization using network of experiments
- [Bluesky example](https://github.com/bluesky/bluesky)
- Grid search vs. random vs. Sobol vs. stochastic gradient descent vs. genetic algorithm
  vs. Bayesian optimization (e.g. via [Olympus benchmarking platform](https://github.com/aspuru-guzik-group/olympus))

Any requests? Post on the [issue
tracker](https://github.com/sparks-baird/self-driving-lab-demo/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)
😉
