# Simple Usage Monitor for HPC Desktops
The goal of this application is to make users aware of their resource consumption (CPU cycles and memory) when running in the shared environment of an HPC Desktop. The application shows a users CPU and memory consumption (in blue) in relation to the resource consumption of all other users (in red) on the same system. The main window of the application can be configured in 3 views, full (see below), without legend and minimal. The application has a system tray widget that changes color from green to orange to red as a users resource consumption increases. A warning message is also shown in the application window.

If sending of email messages via the `mail` command is available on the system, the application allows users to submit feedback or a bug report with the push of a button. Attaching a screenshot of the application or the whole desktop is also supported.
![f8b4b94d-0fdc-44c4-b749-7079c631c060](https://github.com/user-attachments/assets/df74c001-ae7e-4bb1-b909-989b3f04b86c)

The application was build to run on Indiana Universities RED system, and I am in the process of making it more general so it will run on other systems as well. [Contact me](https://github.com/RobertHenschel) if you are interested in testing it out.
