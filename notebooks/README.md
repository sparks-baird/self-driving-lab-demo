# Notebook Tutorials and Demonstrations

This is a collection of tutorial notebooks and demonstrations for the
self-driving-lab-demo! These notebooks will go over the hardware basics of the LEDs and
sensor (`Getting Started`) and testing out different search algorithms with the bonus of
designing a simulation (`Search Algorithms`). Rather than edit the notebooks ad-hoc when
something goes wrong, it can be more instructive to see the behind-the-scenes
development process, mistakes and all! Not every mistake will be instructive, so I try
to leave only the ones that teach important principals related to self-driving
laboratories such as validating results and troubleshooting software-hardware interfacing.

## 1.* Getting Started

- [`1.0-sgb-blinkt-as7341-basic.ipynb`](1.0-sgb-blinkt-as7341-basic.ipynb)
  - > Let's flash the LED and print out the sensor data!

## 2.* Search Algorithms

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

## More to come!

- multi-fidelity optimization (simulation and experiments)
- controlling the RPi from the cloud
- high-dimensional Bayesian optimization
- Grid search vs. random vs. Sobol vs. stochastic gradient descent vs. genetic algorithm
  vs. Bayesian optimization

Any requests? Post on the [issue
tracker](https://github.com/sparks-baird/self-driving-lab-demo/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)
😉
