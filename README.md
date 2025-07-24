# IP Phone Reboot Automation


This Python script automates the mass reboot of IP phones by detecting, logging into, and rebooting multiple devices from various brands — including Grandstream, Snom, and Polycom (**Only Polycom SoundPoint IP 331**) — using Selenium WebDriver. It also measures and logs reboot durations for each device.


## Features


- Detects device type by inspecting the web UI content using Selenium.
- Supports Grandstream, Snom, and Polycom (**Only supports the model Polycom Sound Point IP 331**) IP phones.
- Logs into each device with predefined credentials.
- Triggers a reboot via the web interface.
- Waits for the device to go offline and measures reboot time by checking port 80 accessibility.
- Logs all actions and results to `results.txt`.
- Runs headless (browser UI hidden) by default (can be changed in the script).


## Prerequisites


- Python 3.8 or newer.
- Google Chrome browser installed.
- Required Python packages (`requirements.txt`).


## Installation


1. Clone this repository or download the script files.


2. Install dependencies:

```bash
pip install -r requirements.txt
```


3. Prepare a `data.txt` file listing IP addresses of your devices, one per line.

Example:
```bash
192.168.1.1
192.168.1.2
192.168.2.1
192.168.2.2
```


## Before using


- Ensure devices are reachable over the network on port 80.


## Usage


Run the script:


```bash
python mass-reboot.py
```


The script will check the IP list, detect device type, reboot devices, and log the reboot durations in `results.txt`.


## Configuration


- Device credentials are defined inside the script and can be updated according to your environment (**the credentials that are in the script are default for all the models**).
- The script currently supports: Grandstream, Snom, and Polycom (**Only supports the model Polycom Sound Point IP 331**).


## Tested phones


- Grandstreams (GXP1625; GXP1628)
- Snoms (300; 710; 712; 715)
- Polycom (Sound Point IP 331)

