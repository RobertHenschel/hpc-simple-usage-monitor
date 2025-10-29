# Simple Usage Monitor for HPC Desktops
The goal of this application is to make users aware of their resource consumption (CPU cycles and memory) when running in the shared environment of an [HPC Desktop](https://github.com/RobertHenschel/HPCDesktop). The application shows a users CPU and memory consumption (in blue) in relation to the resource consumption of all other users (in red) on the same system. The main window of the application can be configured in 3 views, full (see below), without legend and minimal. The application has a system tray widget that changes color from green to orange to red as a users resource consumption increases. A warning message is also shown in the application window.

If sending of email messages via the `mail` command is available on the system, the application allows users to submit feedback or a bug report with the push of a button. Attaching a screenshot of the application or the whole desktop is also supported.
<img src="https://github.com/user-attachments/assets/3a280068-3c33-4dd7-931f-89893c7d1b59" />


# Features
- System tray icon that changes color (green/orange/red) based on user resource consumption.
- 3 views:
  - Full: Show charts and legend
  - Toggle legend: Show or hide the legend.
  - Minimal mode: Hide the legend and axis labels to show more of the chart.
- Save settings: Window geometry and view state are saved between launches.
- Memory alert when memory usage is at or above 50% (orange) or 80% (red) of 100GB limit. (configurable)
- CPU alert when CPU usage is at or above 20% (orange) or 40% (red) of total node. (configurable)
- App Feedback/Bug Report: Send a bug report or feedback, can include screenshots. (configurable email address)

# Running
- Open a terminal
- Clone this repo
  - `git clone https://github.com/RobertHenschel/hpc-simple-usage-monitor.git`
- Change into the repo directory
  - `cd hpc-simple-usage-monitor/`
- Create a python virtual environment
  - `python3 -m venv ./venv`
- Activate the environment
  - `source ./venv/bin/activate`
- Upgrade pip
  - `pip install --upgrade pip`
  - This step may or may not be required, depending on your setup. 
- Install the required python packages
  - `pip install -r requirements.txt`
- Start the app
  - `python3 ./SimpleUsageMonitor.py`

# How to Contribute
The application was build to run on Indiana Universities RED system, and I have refactored it to be more general. It should run on most Linux systems now. [Contact me](https://github.com/RobertHenschel) if you want to share your feedback.


