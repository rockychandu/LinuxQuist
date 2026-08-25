# LinuxQuest — Gamified Linux Learning & Terminal Platform

LinuxQuest is a complete, modern, production-grade interactive web application built with Python (Flask) and SQLite. It teaches users Linux command-line concepts from beginner to advanced level across 20 structured levels with quests, lessons, quizzes, achievements, and an in-browser virtual terminal simulator.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Build](#build)
- [Run Instructions](#run-instructions)
- [Usage & Demo Accounts](#usage--demo-accounts)
- [Testing](#testing)

---

## Overview

LinuxQuest offers a gamified learning curve featuring 20 levels of curriculum, 10 core Learn lessons, 20 written command test quests, 10 quiz levels (5 questions per level, daily shuffled), performance analytics, friends network, and an official completion certificate locked until Level 20.

---

## Features

- **20 Curriculum Levels**: From Linux Basics to Kernel Tuning, Containerization, and SysAdmin Hardening.
- **In-Memory Virtual File System (VFS)**: Realistic terminal shell supporting `pwd`, `ls`, `cd`, `mkdir`, `touch`, `rm`, `cat`, `grep`, `chmod`, `sudo`, `ps`, `top`, `kill`, `ping`, `curl`, etc.
- **10 Learn Lessons**: Comprehensive tutorials covering core terminal concepts.
- **10 Quiz Levels**: 50 total questions shuffled daily based on date seed.
- **Friends & Performance Systems**: Track accuracy metrics and compare rankings with friends.
- **Level 20 Certificate Lock**: Unlock official printable certificate upon completing all levels.

---

## Tech Stack

- **Backend**: Python 3.12, Flask, Werkzeug, SQLite3
- **Frontend**: HTML5, CSS3 (Bright Neon Sunset Theme), JavaScript (ES6+)
- **Audio Synthesizer**: Web Audio API

---

## Dependencies

Required Python packages:
- `Flask>=3.0.0`
- `Werkzeug>=3.0.0`
- `Jinja2>=3.1.2`

---

## Installation

### 1. Clone or Download Repository
```bash
cd c:\Users\HP\OneDrive\Desktop\Project4
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Build

To initialize and seed the SQLite database:

```bash
python seed_data.py
```

---

## Run Instructions

Start the application web server:

```bash
python app.py
```

Access the application in your browser at:
**http://127.0.0.1:5000** (or **http://localhost:5000**)

---

## Usage & Demo Accounts

### Demo Login Credentials:

| Role | Username | Password | Features |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin123` | Level 20 Certified Architect & Admin Panel |
| **Demo Player** | `hero` | `hero123` | Level 5 Explorer with pre-added friends |
| **New Player** | *Self-Register* | *Your choice* | Starts at Level 1 with +50 XP welcome bonus |

---

## Testing

Run the automated test suite:

```bash
python -m unittest discover tests
```
