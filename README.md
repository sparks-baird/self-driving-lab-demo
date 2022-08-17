[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/self-driving-lab-demo.svg?branch=main)](https://cirrus-ci.com/github/<USER>/self-driving-lab-demo)
[![ReadTheDocs](https://readthedocs.org/projects/self-driving-lab-demo/badge/?version=latest)](https://self-driving-lab-demo.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/self-driving-lab-demo/main.svg)](https://coveralls.io/r/<USER>/self-driving-lab-demo)
[![PyPI-Server](https://img.shields.io/pypi/v/self-driving-lab-demo.svg)](https://pypi.org/project/self-driving-lab-demo/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/self-driving-lab-demo.svg)](https://anaconda.org/conda-forge/self-driving-lab-demo)
[![Monthly Downloads](https://pepy.tech/badge/self-driving-lab-demo/month)](https://pepy.tech/project/self-driving-lab-demo)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/self-driving-lab-demo)
-->

[![](https://hackaday-io-badges.herokuapp.com/186289.svg?)](https://hackaday.io/project/186289-self-driving-optics-demo)

# self-driving-lab-demo (WIP)

> Software and instructions for setting up and running an autonomous (self-driving) laboratory optics demo using dimmable RGB LEDs, a 10-channel spectrophotometer, a microcontroller, and an adaptive design algorithm.

Self-driving labs are the future; however, the capital and expertise required can be daunting. We introduce the idea of a constrained, high-dimensional, multi-objective optimization task for less than $100, a square foot of desk space, and an hour of total setup time from the shopping cart to the first "autonomous drive." We use optics rather than chemistry for our demo; after all, light is easier to move than matter. While not strictly materials-based, importantly, several core principles of a self-driving materials discovery lab are retained in this cross-domain example: sending commands to hardware to adjust physical parameters, receiving measured objective properties, decision-making via active learning, and utilizing cloud-based simulations. The demo is accessible, extensible, modular, and repeatable, making it an ideal candidate for both low-cost experimental adaptive design prototyping and learning the principles of self-driving laboratories in a low-risk setting.

<p align="center"><img src="https://github.com/sparks-baird/self-driving-lab-demo/raw/main/reports/figures/abstract.png?a" width=750></p>

## See Also

- [Journal of Brief Ideas submission](https://beta.briefideas.org/ideas/12372397dbaf594ca372f17ebbb8c2a3)
- [Hackaday project page](https://hackaday.io/project/186289-self-driving-optics-demo)
- [Adafruit Forum: Developing a closed-loop feedback system via DotStar
LEDs](https://forums.adafruit.com/viewtopic.php?f=8&t=192420&p=930915)
- [Adafruit required bill of materials (RPi Zero 2 W build)](http://www.adafruit.com/wishlists/551817)

  <img src="reports/figures/required-wishlist.png" width=500>
- [Adafruit optional bill of materials (RPi Zero 2 W build)](http://www.adafruit.com/wishlists/551821)

  <img src="reports/figures/optional-wishlist.png" width=500>
- [Adafruit bill of materials](https://www.adafruit.com/wishlists/551334) (my original one that I ordered and am planning to prototype with)

Most of the build instructions will go into the Hackaday project page, probably with periodic updates to GitHub. GitHub will host the software that I develop.

The BOM uses Raspberry Pi (RPi) in favor of Arduino to support running complex adaptive
design algorithms locally using the higher-end RPi models such as 4B with 8 GB RAM. RPi
is a standalone computer, whereas Arduino is a microcontroller.

Additionally, due to the chip shortage, the current setup (2022-08-16) is designed for
RPi Pico W (see https://github.com/sparks-baird/self-driving-lab-demo/issues/8), but can be adapted to other models.

## ToDo:

- [x] order parts for initial prototype
- [x] assemble hardware
- [x] [set up RPi](https://learn.adafruit.com/raspberry-pi-zero-creation/overview)
- [x] [simple Blinkt! test](https://learn.pimoroni.com/article/getting-started-with-blinkt)
- [x] [simple 10-channel sensor test](https://github.com/adafruit/Adafruit_CircuitPython_AS7341)
- [x] [simple Blinkt! + 10-channel sensor test](https://github.com/sparks-baird/self-driving-lab-demo/blob/main/scripts/blinkt_as7341_basic.py)
- [x] fixture to mount sensor perpendicular to LED Blinkt!
- [ ] write unit tests for Blinkt! and 10-channel sensor
- [ ] write script/library to integrate components
- [x] "first drive" using random search

## Installation

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
