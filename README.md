*This project has been created by Zakka01.*

# Fly-in

## Description

Fly-in is a drone simulation project that models autonomous drone navigation through a network of interconnected zones.

The project:

* Parses a configuration file describing hubs and connections
* Builds a graph representation of the environment
* Computes valid paths between start and end zones
* Simulates drone movement in real time
* Visualizes the simulation using Pygame

The objective of the project is to explore:

* Graph theory
* Pathfinding algorithms
* Turn-based simulation systems
* Dynamic routing
* Real-time visualization

---

# Instructions

## Input Format

The simulation is driven by a configuration file that defines the environment.

This file specifies:

- Total number of drones
- start and end hubs
- Intermediate hubs (zones)
- Links between hubs (connections)
- Optional attributes such as:
  - Zone type
  - zone maximum capacity
  - Color settings
  - Connection limits

---

## Project Workflow

Once the program starts, it follows a structured pipeline:

### 1. Parsing Phase

- Loads the configuration file
- Checks data validity and consistency
- Converts raw input into structured objects

### 2. Graph Building

- Constructs an adjacency list representation
- Establishes connections between all hubs

### 3. Path Computation

- Generates multiple possible routes
- Filters and organizes paths for drone assignment

### 4. Simulation Phase

- Advances the system step by step to simulate movement

### 5. Rendering

- The visualization part using pygame
- Renders hubs, links, and drone progression in real time
---


# Algorithm Explanation

## Graph Representation

The system models the environment as a weighted graph:

- Nodes represent zones
- Edges represent connections between zones

---

## Pathfinding Algorithm

The project is based on Weighted BFS algorithm.

### Principle

- Each zone has a cost
- The algorithm finds all paths between start and end hubs

---

## Multi-Path Strategy

The system:

- Generates several alternatives
- Evaluates their total cost
- Assigns paths to drones

This helps to:

- Balance load across the graph
- Avoid congestion
- Improve overall flow

---

## Constraint Management

Movement is limited by:

- Zone capacity (`max_drones`)
- Link capacity (`max_link_capacity`)

When constraints are reached, drones must:

- Wait
- Or switch to another route

---

## Turn-Based Simulation

The simulation runs in discrete steps.

Each turn:

- Updates all drones
- Moves drones when possible
- Applies constraints
- Updates system state

---


# Visual Representation Features

The project includes a real-time visualization system built using Pygame.

---

## Graph Visualization

* Zones are displayed as circles
* Connections are displayed as lines

This provides a clear visual representation of the network.

---

## Zone Visualization

Zones use:

* Colors
* Labels
* Different visual states

to represent:

* Normal zones
* Restricted zones
* Priority zones
* Blocked zones

---

## Drone Visualization

* Drones are animated in real time
* Each drone displays a unique identifier

This allows users to follow drone movement visually.

---

## Real-Time Animation

The renderer synchronizes with the simulation engine:

* Each simulation turn updates the display
* Transitions are animated progressively

---

## User Experience Benefits

The visualization system improves usability by:

* Making graph structures easier to understand
* Showing congestion visually
* Helping debug deadlocks and routing issues
* Providing immediate feedback on drone behavior

---

# Resources

## Documentation & References

* Pygame Documentation
  https://www.pygame.org/docs/

* Drone Map Visualizer
  https://flyin-drone-map-visualizer.vercel.app/

---

## AI Usage

AI tools were used as development assistants for:

### Debugging

* Resolving runtime and Flake8 & MyPy errors
* Understanding pdb debugging workflows

### Concept Explanations

* Graph structures
* Pygame rendering and event handling

### Development Support

* Improving project structure
* Refactoring code for readability
* Assisting with documentation organization


AI was used as a support tool for learning, debugging, and documentation only.
