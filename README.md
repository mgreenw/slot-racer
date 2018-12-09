# Slot Racer

### Authors
- Nathan Allen
- Pulkit Jain
- Max Greenwald

### Slot Racer
This is a game that allows multiple players to play slot-car racing against
one another

### Setup

1. Use Python 3.7.1: `python --version`
2. Setup a virtual env: `python -m venv ./venv`
3. Then, activate the venv: `source ./venv/bin/activate`
4. Then, do `pip install -r requirements.txt`

When done, deactivate the venv: `deactivate`

NOTE: If glfw is not installed in your computer, do the following:
* If Mac:
    * Install brew
    * brew install glfw3
Ensure you have glfw3 on your device to run the above code.

### Usage

1. python run_server.py \[HOSTNAME, default='localhost'] \[PORT, default=8765]
2. python run_client.py \[HOSTNAME, default='localhost'] \[PORT, default=8765]

### Code Overview

* ./slot_racer
    * ./\_\_init__.py: packages the game
    * ./client
        * ./\_\_init__.py: packages the client
        * ./client.py: implements the Client and all its associated functions
        * ./extra.py: implements the extraneous functions this module needs
        * ./renderer.py: implements the Renderer which renders the game
        * ./socket.py: implements the Socket which allows each client to maintain a socket connection to the server
        * ./assets: contains files used to create the explosion effect
            * ./explosion-0.png
            * ./explosion-1.png
            * ./explosion-10.png
            * ./explosion-11.png
            * ./explosion-12.png
            * ./explosion-13.png
            * ./explosion-14.png
            * ./explosion-15.png
            * ./explosion-16.png
            * ./explosion-2.png
            * ./explosion-3.png
            * ./explosion-4.png
            * ./explosion-5.png
            * ./explosion-6.png
            * ./explosion-7.png
            * ./explosion-8.png
            * ./explosion-9.png
            * ./explosion.gif
    * ./communication
        * ./\_\_init__.py: packages the communication
        * ./serializer.py: implements the Serializer used by clients and servers to communicate with one another
    * ./game
        * ./\_\_init__.py: packages the game itself
        * ./physics
            * ./\_\_init__.py: packages the physics module
            * ./physics.py: contains all the helper functions that allow us to conduct physics
        * ./state
            * ./\_\_init__.py: packages the state of the game
            * ./extra.py: implements extraneous definitions used by the state
            * ./state.py: implements the state of the game itself. Specifically, the Car and the Track
            * ./test.py: implements tests for the state
    * ./server
        * ./\_\_init__.py: packages the server
        * ./extra.py: implements extraneous definitions used by the server
        * ./server.py: implements the Server and all its associated functions

