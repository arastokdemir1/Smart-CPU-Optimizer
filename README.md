# 💻 Smart Optimize: Smart Mac CPU Priority Manager

[![ Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)

[![ Scikit-learn](https://img.shields.io/badge/Machine%20Learning-Scikit--learn-orange)](https://scikit-learn.org/)

[![ Platform](https://img.shields.io/badge/Platform-macOS%20Only-lightgrey)](https://www.apple.com/macos)

## ✨ About the Project

**Smart Optimize** is an artificial intelligence-powered tool that automatically detects the application and context you are actively using on your macOS system and dynamically adjusts the CPU priority accordingly.

Its purpose is to reduce hangs and optimize overall performance by allocating system resources to the relevant application in high priority tasks (Coding, Meeting).

## How Does 🧠 Work? (AI Core)

The project operates in three main stages:

1. **Information Collection:** Using `osascript` (AppleScript) and `psutil` libraries, the name and window title of the current application are constantly collected.

2. **Context Classification (ML Model):**

* The collected text data is analyzed by a pre-trained **TF-IDF Vectorization** and **Multinomial Naive Bayes (MNB)** classifier.

* The application automatically assigns the context to one of these categories: `CODING`, `MEETING`, `ENTERTAINMENT`, `SYSTEM`, `OTHER`.

3. **Dynamic Optimization (renice):**

* According to the classification result, the command `sudo renice` is applied to the PID (Process ID) of the active application.

* Priority Levels:

* `CODING` and `MEETING`: **High Priority** (`-10`)

* `ENTERTAINMENT` and `WEB BROWSING`: **Normal Priority** (`0`)

* `SYSTEM` and `OTHER`: **Low Priority** (`+10`)

## 🛠️ Setup and Run

### Prerequisites

* macOS (This script only works on macOS.)

* Python 3.x

### Step by Step Installation

1. **Clone the Warehouse:**

```bash

Git clone [https://github.com/](https://github.com/)[YOUR USER-NAME]/Smart-Optimize.git

Cd Smart-Optimimize

```

2. **Set Up the Required Libraries:**

```bash

Pip install -r requirements.txt

# or separately:

# pip install pandas scikit-learn psutil

```

3. **Run:**

⚠️ **CAUTION:** This script uses the command `sudo renice` to change the priority of system processes and therefore requires a **administrator password** when running.

```bash

Python main.py

```

*After the script is running, the terminal will ask you for your password and then it will start optimizing continuously in the background. *

## ⚙️ Requirements (`requirements.txt`)
