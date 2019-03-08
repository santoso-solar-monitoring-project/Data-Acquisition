# Data-Acquisition
Software that acquires the data from the solar panels, sends the data to the server, and uses the data to control the solar panels.

## Getting Started
After cloning the repo, make sure you have installed the packages listed in the prerequisites section.

### Prerequisites
Software you need before using this project:
```
Python 3 (We use 3.5.3)
pip3
```
It is a good idea to use a virtual environment for this project as to not mess up pre-existing libraries on your machine. The link to virtualenv's tutorial is [here](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/).

In order to install the necessary Adafruit libraries, go into the base directory of the project and run
```
pip3 install -r requirements.txt
```

### Starting the Project
In this project we used three ADS1015s, addressed 0x48-0x4A, and two PCA9685s, addressed 0x40 and 0x41.

To run the main project, change into the ./monitor/ directory and run
```
python3 controller.py --help
```
From here the instructions listed by the script will help you decide what MPPT mode you would like to start with.

Each file in the MPPT_packages folder is runnable by itself, allowing you to test specific functionality of the monitor.

### Authors
[ZachPope531](https://github.com/ZachPope531) - Designed controller.py, adc.py, and pusher.py

[luisquint](https://github.com/luisquint) - Designed mppt.py
