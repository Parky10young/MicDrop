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
  - 

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

4. Set up NGROK free https url (for Audience)
   ```cmd
   ngrok http 5000

5. Run application
   ```bash
   python3 app.py

---

## Local User's Features Instructions (Stage Speaker/ Host of the Talk)
type in:
```url
localhost:5000/
```

### Handle Message Container
- Direct to the page by clicking "Talk with us" button in the Menu
- Then network users can connect to this page.
- To start the voice communication, click "call" button
- To end the call, click "hang up" button
- To delete que element, click "delete" buttons for both text and voice messages. This is for the case when you are done discussing the message(text or voice)
- When the network user starts speaking, audio level is displayed with dynamic bars so that server could check sound input. If needed, there is a volume control bar that could control the speaker output sound scale.

### Create Polls
- Direct to the page by clicking "Create Poll" in the Menu
- Add question and options by filling in the message boxes, and click "delete" to delete an element
- Then click "create poll" button so that it could be checked that it is saved as existing poll and displayed
- To delete existing poll or option for past poll, click "delete poll" or "delete option"  
- Before clicking "Release Poll" button, network users cannot see the poll questions and options
- To display and enable a poll or more polls, click "release poll"
- Before clicking "start timer" button, network users cannot see the poll results unless they type in the url
- "start timer" button renders of the poll result page on network users screen automatically after certain amount of time(now set as 60 seconds)

---

## Network User's Features Instructions (Audience)
- Scan QR code generated on the shared screen from server
- The url would look something like: xxx-xxx-xxxx-xxx.ngrok-free.app/
- This is uses "HTTPS://" instead of "HTTP://" so that network users can 

### Send Message
- Direct to the page by clicking "Talk with us" button in the Menu
- Put in fields for both name and background to send message
- Choose between typing text message in the box within 20 words or click "request" button
- If you want to send another message between the two options, you should wait for some time
- For resending text message, there would be "register to ~" button appearing. you should wait another amount of time for this feature, additionally.
- If you want to withdraw your text or voice request after they are sent, they can be deleted with the "delete" button
- If you sent a voice request and then see a yellow alert box saying that you can talk now, click "talk" button, and speak. this will let your voice streamed through the server and eventually emitted on the server's speaker.

### Vote for Polls
- Direct to the page by clicking "Polls" in the Menu
- Can vote for each poll and record choice
- Poll results is shown after certain amount of time(now set as 60 seconds)

---

## Upgrade Plans
- Display timer control for the server to set time for the poll easily, without needing to modify number in code
- Reduce voice stream delay
- Add other features such as developer profile
- Enable seperate release buttons for each poll

---  

## Acknowlegement
https://github.com/danidee10/Votr

---

## Reference
'''https://www.instructables.com/Web-Designing-Basics-HTML-and-CSS/ '''


