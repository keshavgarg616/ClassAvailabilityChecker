# ClassAvailabilityChecker

Automates logging into UMass SPIRE to check enrollment availability for specified classes.
Currently supports fetching enrollment totals, capacity, and open seats for one class, with upcoming features for email alerts and multi-class monitoring.

## Features

-   ✅ Works on Windows and macOS
-   ✅ Uses your existing Chrome profile (avoids repeated logins/MFA)
-   ✅ Automatically switches into SPIRE’s hidden iframe to interact with elements
-   ✅ Reads .env variables for login credentials & class ID
-   🛠 Coming Soon:
    -   Email notifications when a class has open seats
    -   Support for checking multiple classes in one run

## Requirements

-   Python 3.8+
-   Google Chrome
-   ChromeDriver (matching your Chrome version)

## Setup

1. **Clone this repository** or download the files.
2. **Install dependencies:**
    ```bash
    pip install selenium python-dotenv
    ```
3. **Set up `.env` file** in the project root:
    ```env
    email=your_email@umass.edu
    passwd=your_password
    class_id=12345
    ```
4. ChromeDriver

-   Windows: download [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/#stable)
    and place chromedriver.exe in the project folder
-   macOS:
    ```bash
    brew install chromedriver
    ```

5. **Run the script:**
    ```bash
    python class_checker.py
    ```

## Cross-Platform Support

This script works on both **Windows** and **Mac** — the code automatically detects your OS and sets the ChromeDriver binary accordingly.

## 🛠 Notes

-   Mac users: If ChromeDriver isn’t found, update driver_binary in the script to match your system path (default brew path: /opt/homebrew/bin/chromedriver).
-   Windows users: Keep chromedriver.exe in the same folder as the script unless you add it to PATH.
-   SPIRE’s HTML changes sometimes — if the script breaks, you may need to update element IDs.
