#!/usr/bin/env python3
import sys
import psutil
from collections import deque
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import tempfile
import strings  # Import externalized strings
import settings  # Import settings

# Now import the rest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap, QColor
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QDialog, QTextEdit, QPushButton, QVBoxLayout, QSpacerItem, QSizePolicy, QCheckBox, QSystemTrayIcon, QMenu
from PyQt5.QtCore import QTimer, QSettings, Qt
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QFontMetrics

# Create QApplication instance first
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(settings.APP_ICON))  # Set application icon

class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(strings.FEEDBACK_DIALOG_TITLE)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.parent = parent
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add instructions
        instructions = QLabel(strings.FEEDBACK_INSTRUCTIONS)
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        # Add text edit for feedback
        self.feedback_text = QTextEdit()
        layout.addWidget(self.feedback_text)
        
        # Add screenshot checkboxes - both unchecked by default
        self.app_screenshot_checkbox = QCheckBox(strings.FEEDBACK_ATTACH_APP)
        self.app_screenshot_checkbox.setChecked(False)  # Default to unchecked
        layout.addWidget(self.app_screenshot_checkbox)
        
        self.screen_screenshot_checkbox = QCheckBox(strings.FEEDBACK_ATTACH_SCREEN)
        self.screen_screenshot_checkbox.setChecked(False)  # Default to unchecked
        layout.addWidget(self.screen_screenshot_checkbox)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        # Add spacer to push buttons to the right
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Add Cancel button
        self.cancel_button = QPushButton(strings.FEEDBACK_CANCEL)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Add Send button
        self.send_button = QPushButton(strings.FEEDBACK_SEND)
        self.send_button.clicked.connect(self.accept)
        self.send_button.setDefault(True)
        button_layout.addWidget(self.send_button)
        
        layout.addLayout(button_layout)

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(strings.MAIN_WINDOW_TITLE)
        self.setWindowIcon(QIcon(settings.APP_ICON))  # Set window icon
        
        # Setup system tray icon
        self.setup_system_tray()
               
        # Store window size
        self.window_width = 1000
        self.window_height = 600
        
        # Initialize settings
        self.settings = QSettings(settings.ORGANIZATION_NAME, settings.APPLICATION_NAME)
        
        # Set default geometry (will be overridden by restore_settings if saved settings exist)
        self.setGeometry(100, 100, self.window_width, self.window_height)
        
        # Create toolbar and buttons
        toolbar = self.addToolBar('Controls')
        
        # Add Toggle Legend button
        self.toggle_button = QAction(strings.TOGGLE_LEGEND_BUTTON, self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.triggered.connect(self.toggle_legend)
        toolbar.addAction(self.toggle_button)
        
        # Add Minimal mode button
        self.minimal_button = QAction(strings.MINIMAL_VIEW_BUTTON, self)
        self.minimal_button.setCheckable(True)
        self.minimal_button.setChecked(False)
        self.minimal_button.triggered.connect(self.toggle_minimal)
        toolbar.addAction(self.minimal_button)
        
        # Add Clear Message button
        self.clear_message_button = QAction(strings.CLEAR_ALERT_BUTTON, self)
        self.clear_message_button.triggered.connect(self.clear_status_message)
        toolbar.addAction(self.clear_message_button)
        
        # Add spacer to push feedback button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Add Feedback button (right-aligned)
        self.feedback_button = QAction(strings.SEND_FEEDBACK_BUTTON, self)
        self.feedback_button.triggered.connect(self.show_feedback_dialog)
        toolbar.addAction(self.feedback_button)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(10)  # Add some spacing between elements
        
        # Add status message label (initially hidden)
        self.status_message = QLabel()
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        self.status_message.setVisible(False)  # Initially hidden
        self.main_layout.addWidget(self.status_message)
        
        # Create charts layout with equal spacing
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)  # Add spacing between charts
        self.main_layout.addLayout(charts_layout)
        
        # Create vertical layouts for each chart and its label
        cpu_layout = QVBoxLayout()
        mem_layout = QVBoxLayout()
        charts_layout.addLayout(cpu_layout, stretch=1)  # Add stretch factor
        charts_layout.addLayout(mem_layout, stretch=1)  # Add stretch factor
        
        # Initialize data structures with zeros
        self.max_points = 60  # 1 minute of data (60 seconds)
        self.times = deque([i for i in range(1, self.max_points + 1)], maxlen=self.max_points)
        self.user_cpu_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.others_cpu_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.user_mem_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.others_mem_data = deque([0] * self.max_points, maxlen=self.max_points)
        
        # Initialize time counter to start at max_points
        self.current_time = self.max_points
        
        # Create and setup CPU plot and label
        self.cpu_plot = self.setup_plot(strings.CPU_PLOT_TITLE, strings.CPU_PLOT_Y_LABEL)
        self.cpu_label = QLabel('My CPU Usage: 0% (Should not exceed 20%)')
        self.cpu_label.setStyleSheet('font-size: 14px; font-weight: bold; color: blue;')
        cpu_layout.addWidget(self.cpu_plot['widget'])
        cpu_layout.addWidget(self.cpu_label)
        
        # Store the full text versions for labels
        self.cpu_full_text = strings.CPU_LABEL_FULL
        self.cpu_compact_text = strings.CPU_LABEL_COMPACT
        
        # Store total system memory and memory limit
        self.total_memory = psutil.virtual_memory().total
        self.memory_limit = settings.MEMORY_LIMIT_GB * 1024 * 1024 * 1024  # Convert GB to bytes
        self.max_memory_percent = min(100, (self.memory_limit / self.total_memory) * 100)
        
        # Create and setup Memory plot and label
        self.mem_plot = self.setup_plot(strings.MEM_PLOT_TITLE, strings.MEM_PLOT_Y_LABEL)
        self.mem_label = QLabel(f"{strings.MEM_LABEL_FULL.format(0, self.max_memory_percent)} ({settings.MEMORY_LIMIT_GB}GB)")
        self.mem_label.setStyleSheet('font-size: 14px; font-weight: bold; color: blue;')
        mem_layout.addWidget(self.mem_plot['widget'])
        mem_layout.addWidget(self.mem_label)
        
        # Store the full text versions for memory label
        self.mem_full_text = strings.MEM_LABEL_FULL + f" ({settings.MEMORY_LIMIT_GB}GB)"
        self.mem_compact_text = strings.MEM_LABEL_COMPACT
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(1000)  # Update every 1 second
        
        # Get current user ID
        self.current_user = os.getuid()
        
        # Add legend at the bottom
        legend_layout = QHBoxLayout()
        self.main_layout.addLayout(legend_layout)
        
        # Usage Guidelines on the left
        guidelines_text = strings.GUIDELINES_TEXT
        guidelines_label = QLabel(guidelines_text)
        guidelines_label.setStyleSheet('font-size: 12px; background-color: #f0f0f0; padding: 10px; border-radius: 5px;')
        legend_layout.addWidget(guidelines_label)
        
        # Chart Legend on the right
        legend_text = strings.LEGEND_TEXT
        legend_label = QLabel(legend_text)
        legend_label.setStyleSheet('font-size: 12px; background-color: #f0f0f0; padding: 10px; border-radius: 5px;')
        legend_layout.addWidget(legend_label)

        # Store legend widgets for toggling
        self.legend_layout = legend_layout
        self.guidelines_label = guidelines_label
        self.legend_label = legend_label

        # After all UI elements are created, restore settings
        self.restore_settings()

    def setup_system_tray(self):
        """Setup system tray icon with green color initially"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a menu for the tray icon
        tray_menu = QMenu()
        show_action = tray_menu.addAction(strings.TRAY_SHOW)
        show_action.triggered.connect(self.show)
        hide_action = tray_menu.addAction(strings.TRAY_HIDE)
        hide_action.triggered.connect(self.hide)
        
        # Add separator
        tray_menu.addSeparator()
        
        # Add Clear Alert option
        clear_alert_action = tray_menu.addAction(strings.TRAY_CLEAR_ALERT)
        clear_alert_action.triggered.connect(self.clear_status_message)
        
        # Add separator
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction(strings.TRAY_QUIT)
        quit_action.triggered.connect(app.quit)
        
        # Set the menu for the tray icon
        self.tray_icon.setContextMenu(tray_menu)
        
        # Set initial green icon
        self.set_tray_icon_color("green")
        
        # Show the tray icon
        self.tray_icon.show()
    
    def set_tray_icon_color(self, color):
        """Set the system tray icon color"""
        # Create a colored icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color))
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Set tooltip based on color
        if color == "green":
            self.tray_icon.setToolTip(strings.TRAY_TOOLTIP_NO_ALERTS)
        elif color == "orange":
            self.tray_icon.setToolTip(strings.TRAY_TOOLTIP_WARNING)
        elif color == "red":
            self.tray_icon.setToolTip(strings.TRAY_TOOLTIP_ALERT)
        else:
            self.tray_icon.setToolTip(strings.TRAY_TOOLTIP_DEFAULT)

    def setup_plot(self, title, ylabel):
        plot_widget = pg.PlotWidget()
        
        # Setup plot
        plot_widget.setBackground('w')
        plot_widget.setTitle(title, color='k')
        plot_widget.setLabel('left', ylabel, color='k')
        plot_widget.setLabel('bottom', strings.TIME_AXIS_LABEL, color='k')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.setYRange(0, 100)
        
        # Hide the auto-scale button
        plot_widget.hideButtons()
        
        # Disable mouse interaction (panning, zooming, etc.)
        plot_widget.setMouseEnabled(x=False, y=False)
        plot_widget.getViewBox().setMenuEnabled(False)
        
        # Set initial X range from 1 to max_points
        plot_widget.setXRange(1, self.max_points)
        
        # Create fill curves for stacked area plot
        user_fill = pg.FillBetweenItem(
            curve1=pg.PlotCurveItem(pen='b'),
            curve2=pg.PlotCurveItem(pen='b'),
            brush=pg.mkBrush((0, 0, 255, 100))  # Semi-transparent blue
        )
        others_fill = pg.FillBetweenItem(
            curve1=pg.PlotCurveItem(pen='r'),
            curve2=pg.PlotCurveItem(pen='r'),
            brush=pg.mkBrush((255, 0, 0, 100))  # Semi-transparent red
        )
        
        # Add fill curves to plot
        plot_widget.addItem(user_fill)
        plot_widget.addItem(others_fill)
        
        # Create curves for the lines
        user_curve = plot_widget.plot(pen=pg.mkPen('b', width=2), name='Current User')
        others_curve = plot_widget.plot(pen=pg.mkPen('r', width=2), name='Other Users')
        
        # Add legend
        plot_widget.addLegend()
        
        return {
            'widget': plot_widget,
            'user_fill': user_fill,
            'others_fill': others_fill,
            'user_curve': user_curve,
            'others_curve': others_curve
        }

    def get_system_usage(self):
        """Get CPU and memory usage using a single top command call."""
        try:
            # Initialize counters
            user_cpu = 0.0
            others_cpu = 0.0
            user_mem = 0.0
            others_mem = 0.0
          
            # Get current user's username
            current_user = os.environ.get('USER', '')
            
            # Get CPU count for normalization
            cpu_count = psutil.cpu_count()

            # Make a single call to top to get all processes
            cmd = [
                'top', '-b', '-n', '1',
                '-o', '+%CPU', # Sort by CPU usage
                '-w', '512'    # Set wide output to avoid truncation
            ]
            
            # Run command and get output
            output = subprocess.check_output(cmd, text=True)
            
            # Process all processes
            total_cpu = 0.0
            total_mem = 0.0
            # Skip header lines from top output
            lines = output.strip().split('\n')[7:]
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 10:  # Ensure we have enough columns
                        try:
                            # Find CPU and memory values indices
                            cpu_idx = 8
                            mem_idx = 9
                            user_idx = 1  # User column is typically the second column
                            
                            # Find indices by searching for % symbol
                            for i, part in enumerate(parts):
                                if '%CPU' in part:
                                    cpu_idx = i
                                elif '%MEM' in part:
                                    mem_idx = i
                            
                            # Extract CPU, memory, and user values
                            cpu_val = float(parts[cpu_idx])
                            mem_val = float(parts[mem_idx])
                            process_user = parts[user_idx]
                            
                            # Add to total counters
                            total_cpu += cpu_val
                            total_mem += mem_val
                            
                            # If this process belongs to current user, add to user counters
                            if process_user == current_user:
                                user_cpu += cpu_val
                                user_mem += mem_val
                                
                        except (ValueError, IndexError):
                            # Skip lines that don't have the expected format
                            pass
            
            # Calculate others' usage
            others_cpu = total_cpu - user_cpu
            others_mem = total_mem - user_mem
            
            # Normalize CPU usage to 0-100% range
            # top may show values exceeding 100% for multi-core systems
            # Normalize them to show proper percentages
            cpu_scale_factor = 100.0 / (100.0 * cpu_count)
            user_cpu = user_cpu * cpu_scale_factor
            others_cpu = others_cpu * cpu_scale_factor
            
            # Ensure values are within reasonable range
            user_cpu = min(100.0, max(0.0, user_cpu))
            others_cpu = min(100.0, max(0.0, others_cpu))
            user_mem = min(100.0, max(0.0, user_mem))
            others_mem = min(100.0, max(0.0, others_mem))
            
            return user_cpu, others_cpu, user_mem, others_mem
            
        except Exception as e:
            print(strings.ERROR_SYSTEM_USAGE.format(e))
            # Return zeros in case of error
            return 0.0, 0.0, 0.0, 0.0

    def update_plot_data(self, plot_dict, user_data, others_data, times):
        # Calculate stacked data
        stacked_data = [u + o for u, o in zip(user_data, others_data)]
        
        # Update user area
        plot_dict['user_fill'].setCurves(
            curve1=pg.PlotCurveItem(times, user_data, pen='b'),
            curve2=pg.PlotCurveItem(times, [0] * len(times), pen='b')
        )
        
        # Update others area
        plot_dict['others_fill'].setCurves(
            curve1=pg.PlotCurveItem(times, stacked_data, pen='r'),
            curve2=pg.PlotCurveItem(times, user_data, pen='r')
        )
        
        # Update line plots
        plot_dict['user_curve'].setData(times, user_data)
        plot_dict['others_curve'].setData(times, stacked_data)

   
    def update_plots(self):
        # Get usage data in a single call
        user_cpu, others_cpu, user_mem, others_mem = self.get_system_usage()
        self.current_time += 1
        
        # Get current time for alerts
        current_time = datetime.now().strftime('%H:%M')
        
        # Calculate memory in GB (convert percentage to actual bytes, then to GB)
        memory_gb = (user_mem / 100.0) * self.total_memory / (1024 * 1024 * 1024)
        # Round to nearest GB
        rounded_gb = round(memory_gb)
        
        # Check thresholds and set status messages with time
        if memory_gb >= settings.MEMORY_HIGH_THRESHOLD:
            self.set_status_message(strings.STATUS_MEM_HIGH.format(current_time, rounded_gb), "red")
        elif memory_gb >= settings.MEMORY_MEDIUM_THRESHOLD:
            self.set_status_message(strings.STATUS_MEM_MEDIUM.format(current_time, rounded_gb), "orange")
        
        if user_cpu >= settings.CPU_HIGH_THRESHOLD:
            self.set_status_message(strings.STATUS_CPU_HIGH.format(current_time), "red")
        elif user_cpu >= settings.CPU_MEDIUM_THRESHOLD:
            self.set_status_message(strings.STATUS_CPU_MEDIUM.format(current_time), "orange")
       
        # Update data
        self.times.append(self.current_time)
        self.user_cpu_data.append(user_cpu)
        self.others_cpu_data.append(others_cpu)
        self.user_mem_data.append(user_mem)
        self.others_mem_data.append(others_mem)
        
        # Update labels with current usage based on view mode
        is_compact = self.toggle_button.isChecked()
        if is_compact:
            self.cpu_label.setText(self.cpu_compact_text.format(user_cpu))
            self.mem_label.setText(self.mem_compact_text.format(user_mem))
        else:
            self.cpu_label.setText(self.cpu_full_text.format(user_cpu))
            self.mem_label.setText(self.mem_full_text.format(user_mem, self.max_memory_percent))
        
        # Create reversed time array from 60 to 1
        fixed_times = list(range(self.max_points, 0, -1))
        
        # Update both plots
        self.update_plot_data(self.cpu_plot, 
                            list(reversed(self.user_cpu_data)),  # Reverse data to match reversed time axis
                            list(reversed(self.others_cpu_data)),
                            fixed_times)
        
        self.update_plot_data(self.mem_plot,
                            list(reversed(self.user_mem_data)),
                            list(reversed(self.others_mem_data)),
                            fixed_times)
        
        # Keep x-axis fixed from 60 to 1
        self.cpu_plot['widget'].setXRange(self.max_points, 1)
        self.mem_plot['widget'].setXRange(self.max_points, 1)
        
        # Always set y-axis from 0 to 100%
        self.cpu_plot['widget'].setYRange(0, 100)
        self.mem_plot['widget'].setYRange(0, 100)

    def toggle_legend(self):
        # Toggle visibility of legend section
        is_visible = not self.toggle_button.isChecked()
        self.guidelines_label.setVisible(is_visible)
        self.legend_label.setVisible(is_visible)
        
        # Update labels to show compact or full text
        current_cpu = float(self.cpu_label.text().split('%')[0].split(': ')[1])
        current_mem = float(self.mem_label.text().split('%')[0].split(': ')[1])
        
        if is_visible:
            self.cpu_label.setText(self.cpu_full_text.format(current_cpu))
            self.mem_label.setText(self.mem_full_text.format(current_mem, self.max_memory_percent))
        else:
            self.cpu_label.setText(self.cpu_compact_text.format(current_cpu))
            self.mem_label.setText(self.mem_compact_text.format(current_mem))
        
        # Save the new settings
        self.save_settings()

    def toggle_minimal(self):
        is_minimal = self.minimal_button.isChecked()
        
        # Enable/disable legend toggle button
        self.toggle_button.setEnabled(not is_minimal)
        
        # Hide/show chart labels and axes
        for plot in [self.cpu_plot, self.mem_plot]:
            # Toggle axis labels and grid
            plot['widget'].showAxis('left', not is_minimal)
            plot['widget'].showAxis('bottom', not is_minimal)
            plot['widget'].showGrid(not is_minimal, not is_minimal)
            # Toggle title and legend
            if is_minimal:
                plot['widget'].setTitle('')
                if plot['widget'].plotItem.legend is not None:
                    plot['widget'].plotItem.legend.setVisible(False)
            else:
                # Restore title and legend
                if plot == self.cpu_plot:
                    plot['widget'].setTitle(strings.CPU_PLOT_TITLE)
                else:
                    plot['widget'].setTitle(strings.MEM_PLOT_TITLE)
                if plot['widget'].plotItem.legend is not None:
                    plot['widget'].plotItem.legend.setVisible(True)
        
        # Hide chart labels and legend if in minimal mode
        if is_minimal:
            self.cpu_label.setVisible(False)
            self.mem_label.setVisible(False)
            self.guidelines_label.setVisible(False)
            self.legend_label.setVisible(False)
            # Force legend button to unchecked state
            self.toggle_button.setChecked(True)
        else:
            # Restore previous legend state
            is_legend_visible = not self.toggle_button.isChecked()
            self.cpu_label.setVisible(True)
            self.mem_label.setVisible(True)
            self.guidelines_label.setVisible(is_legend_visible)
            self.legend_label.setVisible(is_legend_visible)
        
        # Save settings
        self.save_settings()

    def restore_settings(self):
        # Restore window geometry
        geometry = self.settings.value('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Use default geometry if no saved settings
            self.setGeometry(100, 100, self.window_width, self.window_height)
        
        # Restore and apply compact state
        is_compact = self.settings.value('compact_view', False, type=bool)
        if is_compact:
            # Hide legend elements if we're in compact mode
            self.guidelines_label.setVisible(False)
            self.legend_label.setVisible(False)
            # Update button state
            self.toggle_button.setChecked(True)
        
        # Restore minimal state
        is_minimal = self.settings.value('minimal_view', False, type=bool)
        if is_minimal:
            self.minimal_button.setChecked(True)
            self.toggle_minimal()  # Apply minimal mode settings

    def save_settings(self):
        # Save window geometry and view states
        self.settings.setValue('window_geometry', self.saveGeometry())
        self.settings.setValue('compact_view', self.toggle_button.isChecked())
        self.settings.setValue('minimal_view', self.minimal_button.isChecked())

    def closeEvent(self, event):
        # Save settings when window is closed
        self.save_settings()
        super().closeEvent(event)

    def set_status_message(self, message, color="black"):
        """Set a status message with specified color. Empty message hides the label."""
        if not message:
            self.status_message.setVisible(False)
            return
            
        # Get available width for text
        available_width = self.width() - 40  # Subtract some padding
        
        # Check if text needs to be truncated
        font_metrics = QFontMetrics(self.status_message.font())
        elided_text = font_metrics.elidedText(message, Qt.ElideRight, available_width)
        
        # Set text and color
        self.status_message.setText(elided_text)
        self.status_message.setStyleSheet(f"font-size: 14px; font-weight: bold; padding: 5px; color: {color};")
        self.status_message.setVisible(True)
        
        # Update tray icon color to match alert color
        self.set_tray_icon_color(color)

    def clear_status_message(self):
        """Clear the status message and hide the label."""
        self.status_message.setVisible(False)
        
        # Reset tray icon to green
        self.set_tray_icon_color("green")

    def resizeEvent(self, event):
        """Handle window resize to update message truncation if needed."""
        super().resizeEvent(event)
        
        # If message is visible, update its truncation
        if self.status_message.isVisible():
            current_text = self.status_message.text()
            # If text ends with ellipsis, we need to recalculate with original text
            if current_text.endswith('...'):
                # This is a simplification - in a real app you might want to store the original text
                self.set_status_message(current_text.rstrip('...') + "...", 
                                      self.status_message.styleSheet().split('color: ')[1].split(';')[0])

    def show_feedback_dialog(self):
        """Show dialog for sending feedback"""
        dialog = FeedbackDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            feedback_text = dialog.feedback_text.toPlainText().strip()
            attach_app = dialog.app_screenshot_checkbox.isChecked()
            attach_screen = dialog.screen_screenshot_checkbox.isChecked()
            
            if feedback_text:
                self.send_feedback_email(feedback_text, attach_app, attach_screen)
                self.set_status_message(strings.FEEDBACK_SUCCESS, "green")
            else:
                self.set_status_message(strings.FEEDBACK_EMPTY, "orange")
    
    def send_feedback_email(self, message, attach_app=False, attach_screen=False):
        """Send feedback email using system mail command"""
        try:
            # Get username for the email subject
            username = os.environ.get('USER', 'unknown_user')
            hostname = subprocess.check_output(['hostname'], text=True).strip()
            
            # Create email content
            subject = strings.FEEDBACK_EMAIL_SUBJECT.format(username, hostname)
            email_content = strings.FEEDBACK_EMAIL_CONTENT.format(username, hostname, message)
            
            # Use mail command to send email (similar to SendEmail.sh)
            # Get user's email from .forward file if it exists
            forward_file = Path.home() / '.forward'
            from_email = None
            if forward_file.exists():
                with open(forward_file, 'r') as f:
                    from_email = f.read().strip()
            
            # Prepare mail command
            mail_cmd = ['mail']
            if from_email:
                mail_cmd.extend(['-r', from_email])
            
            # Capture screenshots if requested
            screenshot_paths = []
            screen = QApplication.primaryScreen()
            
            if attach_app:
                try:
                    app_path = tempfile.mkstemp(suffix='_app.png')[1]
                    screenshot = screen.grabWindow(self.winId())
                    screenshot.save(app_path, 'PNG')
                    screenshot_paths.append(app_path)
                    email_content += strings.FEEDBACK_APP_SCREENSHOT_MSG
                except Exception as e:
                    print(f"Error capturing app screenshot: {e}")
            
            if attach_screen:
                try:
                    screen_path = tempfile.mkstemp(suffix='_screen.png')[1]
                    screenshot = screen.grabWindow(0)  # 0 captures entire screen
                    screenshot.save(screen_path, 'PNG')
                    screenshot_paths.append(screen_path)
                    email_content += strings.FEEDBACK_SCREEN_SCREENSHOT_MSG
                except Exception as e:
                    print(f"Error capturing screen screenshot: {e}")
            
            # Add attachments to mail command
            for path in screenshot_paths:
                mail_cmd.extend(['-a', path])
            
            mail_cmd.extend(['-s', subject, settings.FEEDBACK_EMAIL]) # Use externalized email from settings
            
            # Execute mail command
            process = subprocess.Popen(mail_cmd, stdin=subprocess.PIPE, text=True)
            process.communicate(input=email_content)
            
            # Clean up temporary files
            for path in screenshot_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    print(f"Error removing temporary file {path}: {e}")
            
        except Exception as e:
            error_msg = f"Error sending feedback: {e}"
            print(error_msg)
            self.set_status_message(strings.FEEDBACK_ERROR, "red")

def main():
    # Set white background and black foreground
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
