#!/usr/bin/env python3
"""
settings.py - Contains configuration settings for the Simple Usage Monitor application.
"""

# Email settings
# If "mail" is configured in the system, this email will be used to send feedback to.
FEEDBACK_EMAIL = "your-email@your-domain.something"

# QSettings configuration
# This is used to store user preferences and settings, it basically 
# identifies the application and the organization that created it.
ORGANIZATION_NAME = "IndianaUniversity" #needs to be one word, no special characters
APPLICATION_NAME = "SimpleUsageMonitor" #needs to be one word, no special characters

# Alert thresholds for CPU and memory alerts in the app and system tray
# Memory thresholds (in GB)
MEMORY_HIGH_THRESHOLD = 80.0  # Red alert threshold
MEMORY_MEDIUM_THRESHOLD = 50.0  # Orange alert threshold

# CPU thresholds (in percentage)
CPU_HIGH_THRESHOLD = 40.0  # Red alert threshold
CPU_MEDIUM_THRESHOLD = 20.0  # Orange alert threshold 

# System limits
# If the system has memory limits for users, for example using cgroups,
# you can set the MEMORY_LIMIT_GB and DRAW_MEMORY_LINE to True to draw a 
# ine at the memory limit in the memory plot.
# If your system doesn't support cgroups, you still need MEMORY_LIMIT_GB defined
# to avoid errors. But then set DRAW_MEMORY_LINE to False.
MEMORY_LIMIT_GB = 100    # Memory limit in GB
DRAW_MEMORY_LINE = True  # Draw a line at the memory limit in the memory plot

# Application resources
APP_ICON = "icon.png"