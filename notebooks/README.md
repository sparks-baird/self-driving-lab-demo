# Notebook Tutorials and Demonstrations

This is a collection of tutorial notebooks and demonstrations for the
self-driving-lab-demo!

First, you should get started with the main, public-facing tutorial. Just click
the following "Open in Colab" badge! [![Open In
Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.1-paho-mqtt-colab-sdl-demo-search.ipynb)

<!-- Next comes the use of the PicoW-SDL-Demo via hosting a local web server (`Pico W / MicroPython implementation`) and
then using Internet-of-things-style communication to remotely control the PicoW
(`Controlling the Pico W Remotely (IoT-style)`). There is also a notebook on controlling
the Pico using a nonwireless option (i.e. compatible when WiFi is not available /
difficult to connect to or when nonwireless Pico is being used). -->

> Note: The 1.*, 2.*, and 3.* tutorials are deprecated due to changes in hardware and
> software design of
the demo (i.e., dropping "Blinkt!" in favor of built-in RGB LED on Maker Pi Pico base,
and dropping a web server interface in favor of MQTT).
Since they are instruction and also show parts of the behind-the-scenes development process, they are kept here for reference and provenance.

## Hand-selected gallery of tutorials

```{nbgallery}
notebooks/4.2-paho-mqtt-colab-sdl-demo-test.ipynb
notebooks/escience/1.0-traditional-doe-vs-bayesian.ipynb
notebooks/6.1-multi-objective.ipynb
notebooks/6.2.1-multi-fidelity-continuous.ipynb
notebooks/6.2.2-multi-fidelity-discrete.ipynb
notebooks/escience/2.7.1-multi_task.ipynb
notebooks/6.3-batch-optimization.ipynb
notebooks/escience/2.8.2-ax_service_existing_data_saasbo_multi_objective.ipynb
notebooks/escience/2.11-predefined-candidates.ipynb
notebooks/7.3-benchmark-dataset-generation.ipynb
```

## 1.* ~~Blinkt! Getting Started~~ (deprecated)

<details close>
<summary>Details</summary>

- [`1.0-sgb-blinkt-as7341-basic.ipynb`](1.0-sgb-blinkt-as7341-basic.ipynb)
  - > Let's flash the LED and print out the sensor data!

</details>

## 2.* ~~Search Algorithms using Blinkt!~~ (deprecated)

<details close>
<summary>Details</summary>

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

</details>

## ~~3.* Pico W with a Web Server~~ (deprecated)

<details close>
<summary>Details</summary>

- [`3.1-random-vs-grid-vs-bayesian.ipynb`](3.1-random-vs-grid-vs-bayesian.ipynb)
  > 🥑 Algorithm comparison using the Pico W that's running a local web server 🥑
- [`3.2-random-vs-grid-vs-bayesian-simulator.ipynb`](3.2-random-vs-grid-vs-bayesian-simulator.ipynb)
  > 🥑 Algorithm comparison using a vamped up simulation based on the NeoPixel
  > (as opposed to DotStar) LED 🥑

</details>

## 4.* Controlling the Pico W Remotely (IoT-style)

- [`4.0-paho-mqtt-colab-sdl-demo.ipynb`](4.0-paho-mqtt-colab-sdl-demo.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.0-paho-mqtt-colab-sdl-demo.ipynb)
  > 📡 Control the Pico W remotely using [MQTT (The Standard for IoT Messaging)](https://mqtt.org/) 📡
- [`4.1-paho-mqtt-colab-sdl-demo-search.ipynb`](4.1-paho-mqtt-colab-sdl-demo-search.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.1-paho-mqtt-colab-sdl-demo-search.ipynb)
  > 🔁 Run the same algorithm comparison experiments controlled from the cloud! 🔁
- [`4.2-paho-mqtt-colab-sdl-demo-test.ipynb`](4.2-paho-mqtt-colab-sdl-demo-test.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.2-paho-mqtt-colab-sdl-demo-test.ipynb)
  > 🌎 Remotely access a free, public test demo from anywhere in the world 🌍

## 5.* Nonwireless Control of Pico

- [`5.0-nonwireless-search.ipynb`](5.0-nonwireless-search.ipynb)
  > No PicoW? No problem! 🤖 Run the same algorithm comparison experiments using a nonwireless Pico! 🤖

## 6.* Advanced optimization

- [`6.0-olympus-benchmarking-basic.ipynb`](6.0-olympus-benchmarking-basic.ipynb)
  > 🏋️ Let's run some benchmarking experiments using the Olympus simulator! 🏋️
- [`6.1-multi-objective.ipynb`](6.1-multi-objective.ipynb)
  > 🎯 When more than one property is important (meaning virtually all real-world tasks 😉) 🎯
- [`6.2-multi-fidelity.ipynb`](6.2-multi-fidelity.ipynb)
  > 📈 Optimization using multiple information sources of varying cost and quality 📈
  - [`6.2.1-multi-fidelity-continuous.ipynb`](6.2.1-multi-fidelity-continuous.ipynb)
    > 📈 Optimization using continuous fidelities (e.g., runtime of a molecular dynamics
    > simulation) 📈
  - [`6.2.2-multi-fidelity-discrete.ipynb`](6.2.2-multi-fidelity-discrete.ipynb) (WIP)
    > 📈 Optimization using discrete fidelities (e.g., finite number of allowed grid
    > sizes in a simulation) 📈
  - [`6.2.3-multi-task.ipynb`](6.2.3-multi-task.ipynb) (WIP)
    > 📈 Optimization using multiple, correlated information sources (e.g., simulations
    > and experiments) 📈
- [`6.3-batch-optimization.ipynb`](6.3-batch-optimization.ipynb)
  > 📦 Optimization using batches of samples. Don't forget to condition your batches!
  > (handled automatically via Ax platform 😁) 📦

## 7.* Data ecosystem

- [`7.0-data-ecosystem.ipynb`](7.0-data-ecosystem.ipynb) (WIP)
  > 📊 Overview of notebooks in this section 📊
- [`7.1-mongodb-read.ipynb`](7.1-mongodb-read.ipynb)
  > 📊 Read data from MongoDB 📊
- [`7.2-robust-data-logging.ipynb`](7.2-robust-data-logging.ipynb) (WIP)
  > 📊 Robust data logging 📊
- [`7.2.1-hivemq-openssl-certificate`](7.2.1-hivemq-openssl-certificate.ipynb)
  > 📊 Generate an OpenSSL certificate for HiveMQ 📊
- [`7.3-benchmark-dataset-generation.ipynb`](7.3-benchmark-dataset-generation.ipynb)
  > 📊 Generate a benchmark dataset 📊

## eScience 2022

See also a set of tutorials prepared for [the eScience 2022
conference](https://www.escience-conference.org/2022/tutorials/adaptive_experimentation_for_science/).
Video tutorials corresponding to these notebooks are [published on YouTube in Taylor
Sparks' Optimization
playlist](https://www.youtube.com/playlist?list=PLL0SWcFqypClTIMQDOs_Jug70qaVPOzEc).

- [1.0-traditional-doe-vs-bayesian.ipynb](escience/1.0-traditional-doe-vs-bayesian.ipynb)
- [2.1-gpei_hartmann_loop.ipynb](escience/2.1-gpei_hartmann_loop.ipynb)
- [2.2-tune_cnn.ipynb](escience/2.2-tune_cnn.ipynb)
- [2.3-gpei_hartmann_service.ipynb](escience/2.3-gpei_hartmann_service.ipynb)
- [2.4-raytune_pytorch_cnn.ipynb](escience/2.4-raytune_pytorch_cnn.ipynb)
- [2.5-multiobjective_optimization.ipynb](escience/2.5-multiobjective_optimization.ipynb)
- [2.6-continuous-multi-fidelity.ipynb](escience/2.6-continuous-multi-fidelity.ipynb)
- [2.7-discrete_multi_fidelity_bo.ipynb](escience/2.7-discrete_multi_fidelity_bo.ipynb)
- [2.7.1-multi_task.ipynb](escience/2.7.1-multi_task.ipynb)
- [2.8-ax_service_existing_data.ipynb](escience/2.8-ax_service_existing_data.ipynb)
  - see also 2.8.0.* [notebook variations](https://github.com/sparks-baird/self-driving-lab-demo/tree/main/notebooks/escience) (e.g., SAASBO, MOO, batch, etc.)
- [2.8.1-human_in_the_loop.ipynb](escience/2.8.1-human_in_the_loop.ipynb)
- [2.8.2-ax_service_existing_data_saasbo_multi_objective.ipynb](escience/2.8.2-ax_service_existing_data_saasbo_multi_objective.ipynb)
- [2.9-scheduler.ipynb](escience/2.9-scheduler.ipynb)
- [2.10-paho-mqtt-colab-sdl-demo-test.ipynb](escience/2.10-paho-mqtt-colab-sdl-demo-test.ipynb)
- [2.11-predefined-candidates.ipynb](escience/2.11-predefined-candidates.ipynb)

## More to come!

- discrete multi-fidelity optimization (simulation and experiments)
- high-dimensional Bayesian optimization ([SAASBO](https://ax.dev/tutorials/saasbo.html), [MORBO](https://github.com/facebookresearch/morbo))
- scalable Bayesian optimization ([MORBO](https://github.com/facebookresearch/morbo), [Dragonfly](https://github.com/dragonfly/dragonfly))
- asynchronous/batch optimization using network of experiments
- Grid search vs. random vs. Sobol vs. stochastic gradient descent vs. genetic algorithm
  vs. Bayesian optimization (e.g. via [Olympus benchmarking platform](https://github.com/aspuru-guzik-group/olympus))
- Repeat experiments for high-variance or failure-prone experiments via [RayTune Repeater](https://docs.ray.io/en/latest/tune/api_docs/suggestion.html#repeated-evaluations-tune-search-repeater)
- Combinations of above
- External evaluation of simulation functions (e.g. FuncX, Slurm, AWS, Google Cloud)
- Experimental orchestration software via [Bluesky](https://github.com/bluesky/bluesky)
- Storing experiments in a database backend (e.g. SQL, MongoDB)
- Combinations of above

Any requests? Post on the [issue
tracker](https://github.com/sparks-baird/self-driving-lab-demo/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)
😉
