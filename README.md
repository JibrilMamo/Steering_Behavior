Steering Behavior Simulation with Evolution
This project is a simulation of vehicles (cars) and monsters with steering behavior implemented using the pygame library. The simulation incorporates an evolutionary approach to control the vehicles and monsters, allowing them to seek out and consume food. The goal is to observe the evolution of these creatures' behavior over time through natural selection.

Features
Interactive simulation of cars and monsters navigating an environment
Cars are attracted to food, guided by their DNA weights
Monsters are also attracted to cars, and their DNA determines their behavior
Evolutionary algorithm to control the cars and monsters' DNA
Real-time visualization of creatures' health and other attributes
Graphical representation of the number of monsters and cars over time

How to Run
Install Python and ensure that pygame, numpy, and matplotlib libraries are installed.
Clone this repository to your local machine.
Run the main.py file to start the simulation.
Press the 'Space' key to toggle the debug mode, which displays extra information.
Evolution
The creatures' DNA is represented as a set of attributes, including attraction to food, repulsion from poison, and perception range. Through natural selection and genetic mutation, the DNA evolves over generations, leading to better-adapted creatures that can find and consume food more efficiently.
