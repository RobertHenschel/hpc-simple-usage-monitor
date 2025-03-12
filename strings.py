#!/usr/bin/env python3
"""
strings.py - Contains all externalized strings for the Simple Usage Monitor application.
"""

import settings  # Import settings to access memory limit

# Application general strings
APP_NAME = "Simple Usage Monitor"

# Window titles
MAIN_WINDOW_TITLE = "Simple Usage Monitor"
FEEDBACK_DIALOG_TITLE = "Send Simple Usage Monitor Feedback"

# Toolbar buttons
TOGGLE_LEGEND_BUTTON = "Toggle Legend"
MINIMAL_VIEW_BUTTON = "Minimal"
SEND_FEEDBACK_BUTTON = "Send App Feedback/Bug Report"
CLEAR_ALERT_BUTTON = "Clear Alert"

# System tray
TRAY_SHOW = "Show"
TRAY_HIDE = "Hide"
TRAY_CLEAR_ALERT = "Clear Alert"
TRAY_QUIT = "Quit"
TRAY_TOOLTIP_NO_ALERTS = "Simple Usage Monitor: No alerts"
TRAY_TOOLTIP_WARNING = "Simple Usage Monitor: Warning"
TRAY_TOOLTIP_ALERT = "Simple Usage Monitor: Alert"
TRAY_TOOLTIP_DEFAULT = "Simple Usage Monitor"

# Plot labels
CPU_PLOT_TITLE = "CPU Usage - Stacked View"
CPU_PLOT_Y_LABEL = "Usage (%)"
MEM_PLOT_TITLE = "Memory Usage - Stacked View"
MEM_PLOT_Y_LABEL = "Usage (%)"
TIME_AXIS_LABEL = "Time (s)"

# Status messages
STATUS_CPU_HIGH = f"[{{0}}] CPU Usage at or above {settings.CPU_HIGH_THRESHOLD}%"
STATUS_CPU_MEDIUM = f"[{{0}}] CPU Usage at or above {settings.CPU_MEDIUM_THRESHOLD}%"
STATUS_MEM_HIGH = "[{0}] Memory consumption at {1} GB"
STATUS_MEM_MEDIUM = "[{0}] Memory consumption at {1} GB"

# Feedback dialog
FEEDBACK_INSTRUCTIONS = "Please enter your bug report, feedback or questions for Simple Usage Monitor below:"
FEEDBACK_ATTACH_APP = "Attach screenshot of SimpleUsageMonitor window"
FEEDBACK_ATTACH_SCREEN = "Attach screenshot of entire RED desktop"
FEEDBACK_CANCEL = "Cancel"
FEEDBACK_SEND = "Send"
FEEDBACK_SUCCESS = "Thank you for your feedback!"
FEEDBACK_EMPTY = "Feedback was empty, not sent."
FEEDBACK_ERROR = "Error sending feedback. Please try again."
FEEDBACK_EMAIL_SUBJECT = "SimpleUsageMonitor Feedback from {0} on {1}"
FEEDBACK_EMAIL_CONTENT = "This is Feedback from user {0} on {1}\n\n{2}"
FEEDBACK_APP_SCREENSHOT_MSG = "\n\n[Application screenshot attached]"
FEEDBACK_SCREEN_SCREENSHOT_MSG = "\n\n[Full screen screenshot attached]"

# Error messages
ERROR_SYSTEM_USAGE = "Error in get_system_usage: {0}"
ERROR_SCREENSHOT_APP = "Error capturing app screenshot: {0}"
ERROR_SCREENSHOT_SCREEN = "Error capturing screen screenshot: {0}"
ERROR_TEMP_FILE = "Error removing temporary file {0}: {1}"
ERROR_SEND_FEEDBACK = "Error sending feedback: {0}"

# CPU and Memory labels
CPU_LABEL_FULL = f"My CPU Usage: {{0:.1f}}% (Should not exceed {settings.CPU_MEDIUM_THRESHOLD}%)"
CPU_LABEL_COMPACT = "My CPU Usage: {0:.1f}%"
MEM_LABEL_FULL = "My Memory Usage: {0:.1f}% (Cannot exceed {1:.1f}%)"
MEM_LABEL_COMPACT = "My Memory Usage: {0:.1f}%"

# Legend text
GUIDELINES_TEXT = f"""
<b>Usage Guidelines:</b><br>
• CPU: Your usage should stay under {settings.CPU_MEDIUM_THRESHOLD}% for extended periods<br>
• Memory: Your usage cannot exceed the specified limit of {settings.MEMORY_LIMIT_GB}GB<br>
• The stacked view shows both your usage and others' usage combined
"""

LEGEND_TEXT = """
<b>Chart Legend:</b><br>
<font color='blue'>■</font> Blue Area: Your usage (your applications)<br>
<font color='red'>■</font> Red Area: Other users' usage (system & other users)
""" 