# Mic Drop Project

## Overview
The **Mic Drop** project is an interactive web application that enables dynamic communication and real-time engagement for local and network users. Built with Flask, WebRTC, and Socket.IO, the platform combines text messaging, audio streaming, live polling, and result visualization to create a seamless and user-friendly experience.

---

## Features
### 1. Text and Audio Interaction
- **Local Users**:
  - Send text messages and initiate/manage audio calls using WebRTC.
  - Messages are handled in a queue for organization and priority.
- **Network Users**:
  - Join discussions through text or audio using mobile-friendly interfaces.
  - Real-time updates via Socket.IO ensure synchronized communication.

### 2. Polling System
- **Poll Creation**: Local users create dynamic polls with multiple questions and options.
- **Voting**: Network users vote dynamically; voting is enabled based on a timer.
- **Result Visualization**: Poll results are displayed as bar charts using Chart.js.

### 3. QR Code Integration
- A dynamically generated QR code allows network users to access the application easily.

### 4. Audio Visualization
- Real-time audio levels are visualized with Canvas for an interactive experience.

---

## Architecture
The Mic Drop project is structured into modular components:
1. **Frontend**:
   - Built with Jinja2 templates, Bootstrap, and custom CSS.
   - Dynamic updates via JavaScript and Socket.IO.
2. **Backend**:
   - Flask application managing APIs and event-driven communication.
3. **WebRTC**:
   - Real-time peer-to-peer audio communication with ICE candidate handling.

4. **Database**:
   - Uses SQLAlchemy with SQLite for managing poll data and relationships between questions and options.

---

## Installation

### Prerequisites
- Python 3.7+
- Node.js and npm (for frontend dependencies)
- Flask and Socket.IO packages
- NGROK installation for HTTPS usage instead of HTTP (ensuring security when using phone interfaces)

### Steps for Running the App
1. Clone the repository:
   ```bash
   git clone https://github.com/Parky10young/MicDrop.git
   cd MicDrop

2. Install dependencies:
   ```bash
    pip install -r requirements.txt
    npm install

3. Set up database:
   ```bash
   flask db upgrade

5. Run flask app
   ```cmd
   ngrok http 5000

   ```bash
   python3 app.py
or
    ```bash
    flask run


   
