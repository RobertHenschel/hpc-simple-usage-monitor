# Simple Usage Monitor for HPC Desktops
The goal of this application is to make users aware of their resource consumption (CPU cycles and memory) when running in the shared environment of an HPC Desktop. The application shows a users CPU and memory consumption (in blue) in relation to the resource consumption of all other users (in red) on the same system. The main window of the application can be configured in 3 views, full (see below), without legend and minimal. The application has a system tray widget that changes color from green to orange to red as a users resource consumption increases. A warning message is also shown in the application window.

If sending of email messages via the `mail` command is available on the system, the application allows users to submit feedback or a bug report with the push of a button. Attaching a screenshot of the application or the whole desktop is also supported.
![image](https://github.com/user-attachments/assets/3ad54b62-4054-4635-8502-3a14df22a8e2)



The application was build to run on Indiana Universities RED system, and I am in the process of making it more general so it will run on other systems as well. [Contact me](https://github.com/RobertHenschel) if you are interested in testing it out.

# Features
- System tray icon that changes color (green/orange/red) based on user resource consumption.
- 3 views:
  - Full: Show charts and legend
  - Toggle legend: Show or hide the legend.
  - Minimal mode: Hide the legend and axis labels to show more of the chart.
- Save settings: Window geometry and view state are saved between launches.
- Memory alert when memory usage is at or above 50% (orange) or 80% (red) of 100GB limit.
- CPU alert when CPU usage is at or above 20% (orange) or 40% (red) of total node.
- App Feedback/Bug Report: Send a bug report or feedback to the developer, can include screenshots.

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
