[<img src="https://hackaday-io-badges.herokuapp.com/186289.svg?b" height=23>](https://hackaday.io/project/186289-self-driving-optics-demo) [![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/) [![PyPI-Server](https://img.shields.io/pypi/v/self-driving-lab-demo.svg)](https://pypi.org/project/self-driving-lab-demo/) [![Monthly Downloads](https://pepy.tech/badge/self-driving-lab-demo/month)](https://pepy.tech/project/self-driving-lab-demo) [![Coveralls](https://img.shields.io/coveralls/github/sparks-baird/self-driving-lab-demo/main.svg)](https://coveralls.io/r/sparks-baird/self-driving-lab-demo)
<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/self-driving-lab-demo.svg?branch=main)](https://cirrus-ci.com/github/<USER>/self-driving-lab-demo)
[![ReadTheDocs](https://readthedocs.org/projects/self-driving-lab-demo/badge/?version=latest)](https://self-driving-lab-demo.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/self-driving-lab-demo/main.svg)](https://coveralls.io/r/<USER>/self-driving-lab-demo)
[![PyPI-Server](https://img.shields.io/pypi/v/self-driving-lab-demo.svg)](https://pypi.org/project/self-driving-lab-demo/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/self-driving-lab-demo.svg)](https://anaconda.org/conda-forge/self-driving-lab-demo)
[![Monthly Downloads](https://pepy.tech/badge/self-driving-lab-demo/month)](https://pepy.tech/project/self-driving-lab-demo)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/self-driving-lab-demo)
-->

**Check out [the notebooks](https://github.com/sparks-baird/self-driving-lab-demo/blob/main/notebooks/README.md) for some tutorials and demonstrations! See also [the updated manuscript](https://github.com/sparks-baird/self-driving-lab-demo/blob/main/reports/self_driving_optics_demo-rev1.pdf), the hackaday page, and [the WIP liquid spectrophotometry demo](https://github.com/sparks-baird/self-driving-lab-demo/discussions/89).**

# self-driving-lab-demo [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/4.2-paho-mqtt-colab-sdl-demo-test.ipynb)

> Software and instructions for setting up and running an autonomous (self-driving) laboratory optics demo using dimmable RGB LEDs, an 8-channel spectrophotometer, a microcontroller, and an adaptive design algorithm.

Self-driving labs are the future; however, the capital and expertise required can be daunting. We introduce the idea of an experimental optimization task for less than $100, a square foot of desk space, and an hour of total setup time from the shopping cart to the first "autonomous drive." We use optics rather than chemistry for our demo; after all, light is easier to move than matter. While not strictly materials-based, importantly, several core principles of a self-driving materials discovery lab are retained in this cross-domain example: sending commands to hardware to adjust physical parameters, receiving measured objective properties, decision-making via active learning, and utilizing cloud-based simulations. The demo is accessible, extensible, modular, and repeatable, making it an ideal candidate for both low-cost experimental adaptive design prototyping and learning the principles of self-driving laboratories in a low-risk setting.

## Overview

<img src="https://github.com/sparks-baird/self-driving-lab-demo/raw/main/reports/figures/abstract.png?a" width=750>

## Hardware

<img src="reports/figures/required-wishlist-pico.png" width=600>

Since the Pico WH is difficult to source (2022-09-15), you will likely need to purchase a Pico W (see [Raspberry Pi Official Resellers](https://www.raspberrypi.com/products/raspberry-pi-pico/?variant=raspberry-pi-pico-w)) and solder [male header pins](https://www.adafruit.com/product/5584) onto it.

<img src="reports/figures/materials-annotated.png" width=350>
<sup>Hardware parts</sup>

## Assembled

<img src="notebooks/sdl-demo-test.jpg" width=350>
<sup>assembled SDL-Demo</sup>

## Assembled (annotated)

<img src="reports/figures/sdl-demo-annotated.png" width=350>
<sup>assembled SDL-Demo (annotated)</sup>

## See Also

- [Journal of Brief Ideas submission](https://beta.briefideas.org/ideas/12372397dbaf594ca372f17ebbb8c2a3)
- [Hackaday project page](https://hackaday.io/project/186289-self-driving-optics-demo)
- [Adafruit Forum: Developing a closed-loop feedback system via DotStar
LEDs](https://forums.adafruit.com/viewtopic.php?f=8&t=192420&p=930915)

Most of the build instructions will go into the Hackaday project page, probably with periodic updates to GitHub. GitHub will host the software that I develop.

The BOM uses Raspberry Pi (RPi) in favor of Arduino to support running complex adaptive
design algorithms locally using the higher-end RPi models such as 4B with 8 GB RAM. RPi Zero 2 W and RPi 4B are standalone computers, whereas Arduino typically only has microcontrollers.

Due to the chip shortage, the current setup (2022-08-16) is designed for
RPi Pico W (see https://github.com/sparks-baird/self-driving-lab-demo/issues/8), but can be adapted to other models.

## ToDo:

- [x] order parts for initial prototype
- [x] assemble hardware
- [x] [set up RPi](https://learn.adafruit.com/raspberry-pi-zero-creation/overview)
- [x] [simple Blinkt! test](https://learn.pimoroni.com/article/getting-started-with-blinkt)
- [x] [simple 10-channel sensor test](https://github.com/adafruit/Adafruit_CircuitPython_AS7341)
- [x] [simple Blinkt! + 10-channel sensor test](https://github.com/sparks-baird/self-driving-lab-demo/blob/main/scripts/blinkt_as7341_basic.py)
- [x] fixture to mount sensor perpendicular to LED Blinkt!
- [x] write unit tests for Blinkt! and 10-channel sensor (simulations)
- [x] write script/library to integrate components
- [x] "first drive" using random search
- [ ] multi-fidelity optimization
- [ ] bluesky example
- [ ] network of cloud-based SDLs
- [ ] initial hackathon ([join the slack channel](https://join.slack.com/t/sdl2-workspace/shared_invite/zt-1fnsk7h1z-UwiewUn66ZhZIheYkH_daQ), invite link expires 10/9/2022. Open an issue if you need the invite link updated.)

## Quick Start

https://youtu.be/GVdfJCsQ8vk

### Purchase the hardware
1. [Pico W Bill of Materials](http://www.adafruit.com/wishlists/553992) or [DigiKey](https://www.digikey.com/short/045j7502)
  1. As of 2022-09-09, you will likely need to buy a RPi Pico W + loose headers from a separate supplier (see the [list of official suppliers](https://www.raspberrypi.com/products/raspberry-pi-pico/?variant=raspberry-pi-pico-w and the DigiKey cart linked above) and then solder the headers yourself (or ask a friend or go to a local makerspace or similar). You may wish to sign up for stock notifications for the Pico W at e.g. PiShop. DigiKey has many in stock (2022-09-19) and a quantity limit of 2 Pico W's. CanaKit seems to have them in stock without quantity restrictions, albeit with higher shipping fees.
1. 14 gauge (**outer thickness including insulation**) sculpting wire (preferably insulated), e.g. [20 gauge electrical wire at DigiKey](https://www.digikey.com/en/products/detail/remington-industries/20UL1007SLDBLA/11615372) or [14 gauge sculpting wire at Amazon](https://a.co/d/7rxgOeR)

### Pico W setup
1. If you're going to do any soldering, test to make sure that your Pico W works prior to soldering by connecting the USB-A to micro-USB-B cable between your computer and Pico W while holding the BOOTSEL button the Pico. It should open up a notification for a new drive on your computer.
1. Solder your headers to the Pico if necessary
1. Plug the Pico W into the Maker Pi Pico base (the board has an image of where the USB port should be pointing to help you know which orientation to put it in)
1. Cut (or bend repeatedly until it snaps) about 2.5-3 feet of sculpting wire. Loop the same wire through each of the four mounting holes on the Maker Pi Pico base and each of the four mounting holes on the AS7341, and position the AS7341 pinhole sensor perpendicular to and 2-3 inches away from the NeoPixel LED (labeled as GP28)
1. (Re)connect the USB cable from the Pico W to your computer while holding the BOOTSEL button on the Pico W, and drag-drop the appropriate MicroPython firmware onto the drive that opens up. This will install MicroPython
1. Download Thonny (for experienced users, you should still download Thonny for initial testing since it has nice features specific to microcontrollers, but of course for the actual programming you can use your preferred IDE)
1. Download the code from the appropriate `src` folder (recommended: [`public_mqtt_sdl_demo`](https://github.com/sparks-baird/self-driving-lab-demo/tree/main/src/public_mqtt_sdl_demo))
1. Rename `sample_secrets.py` to `secrets.py` and populate with the necessary WiFi info (and Pico ID if applicable). SSID is basically the WiFi network name. This may not work for school and work networks, so you can use a hotspot instead or only use the nonwireless functionality ([`nonwireless`](https://github.com/sparks-baird/self-driving-lab-demo/tree/main/src/nonwireless))
1. Upload the code to the Pico W
1. Open main.py and click "run" in Thonny

#### Running the optimizations

1. If you choose the `public_mqtt_sdl_demo`, you can control your SDL-Demo remotely from anywhere. Colab notebook WIP

## Advanced Installation

In order to set up the necessary environment:

1. review and uncomment what you need in `environment.yml` and create an environment `self-driving-lab-demo` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate self-driving-lab-demo
   ```

> **_NOTE:_**  The conda environment will have self-driving-lab-demo installed in editable mode.
> Some changes, e.g. in `setup.cfg`, might require you to run `pip install -e .` again.


Optional and needed only once after `git clone`:

3. install several [pre-commit] git hooks with:
   ```bash
   pre-commit install
   # You might also want to run `pre-commit autoupdate`
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

4. install [nbstripout] git hooks to remove the output cells of committed notebooks with:
   ```bash
   nbstripout --install --attributes notebooks/.gitattributes
   ```
   This is useful to avoid large diffs due to plots in your notebooks.
   A simple `nbstripout --uninstall` will revert these changes.


Then take a look into the `scripts` and `notebooks` folders.

## Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yml` for the exact reproduction of your
   environment with:
   ```bash
   conda env export -n self-driving-lab-demo -f environment.lock.yml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yml` using:
   ```bash
   conda env update -f environment.lock.yml --prune
   ```

## Other Builds


- [Adafruit required bill of materials (RPi Zero 2 W build)](http://www.adafruit.com/wishlists/551817)

  <img src="reports/figures/required-wishlist.png" width=500>
- [Adafruit optional bill of materials (RPi Zero 2 W build)](http://www.adafruit.com/wishlists/551821)

  <img src="reports/figures/optional-wishlist.png" width=500>
- [Adafruit bill of materials](https://www.adafruit.com/wishlists/551334) (my original one that I ordered and am planning to prototype with)

## Closed-loop Spectroscopy Laboratory: Liquid

CLSLab is an autonomous self-driving laboratory that uses dilluted food dye, peristaltic pumps, a light source, and a light sensor to perform liquid-based color-matching to a target color. See the following visual summary:

<img src=https://github.com/sparks-baird/self-driving-lab-demo/raw/main/reports/figures/cls-lab-liquid-summary.png width=450>

See https://github.com/sparks-baird/self-driving-lab-demo/discussions/89 for discussion of ongoing development.

### Bill of Materials

- Everything from the CLSLab:Light demo
  - Pico W + headers (need to solder headers)
  - Maker Pi Pico base
  - Stemma-QT to Grove connector
  - AS7341 Light Sensor
  - USB-A to micro-USB-B cable
  - 5V USB-A wall adapter
  - 20 AWG sculpting wire
- Plant drip bag (large) x2
- Party drink drip bag (small) x3
- Spectrophotometer cuvette
- Peristaltic pump x5
- silicone (or PTFE?) tubing (3 m) (what inner and outer diameter?)
- LED light source (see https://github.com/sparks-baird/self-driving-lab-demo/discussions/52 for context)
- tube connectors (which kind?)
- double Wye connectors
- silicone-to-glass glue or epoxy (to permanently fix a silicone lid to a cuvette)
-

The plant and party IV-style drip bags can be replaced with medical-grade chemically resistant versions that are made up of e.g. polyethylene.

### Required Tools, etc.
- Computer
- 2.4 GHz WiFi (needs to be simple SSID+PASSWORD login, no WPA-enterprise such as Eduroam without finagling https://github.com/sparks-baird/self-driving-lab-demo/discussions/83 https://github.com/sparks-baird/self-driving-lab-demo/discussions/88 https://github.com/sparks-baird/self-driving-lab-demo/issues/76)
- Wire cutters (optional)
- Scissors
- Hole punch (might need to be leather hole punch + hammer instead of handheld hole punch)

## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── self_driving_lab_demo <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.2.3.post1.dev10+g7a0f254 and the [dsproject extension] 0.7.2.post1.dev3+g948a662.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
