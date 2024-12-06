import os
import base64
import socket
import io
import qrcode
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, redirect, url_for, flash, session, abort, Response, stream_with_context, request, url_for
from flask import make_response
from flask import jsonify, request, send_from_directory
import requests
from collections import deque
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
import onetimepass
import pyqrcode
import time
from flask_socketio import SocketIO, emit
from datetime import datetime
from queue import Queue
from threading import Thread
from collections import defaultdict
from flask_cors import CORS



# Create the application instance
app = Flask(__name__, static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object('config')

# Initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Test to see if the PIL library works
img = Image.new('RGB', (60, 30), color='red')
img.save('test_image.png')

# Homepage route (displays the QR code)

poll_released = False  # Initialize poll release state


# Function to fetch the Ngrok URL
def get_ngrok_url():
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        return tunnels[0]['public_url']  # Get the public Ngrok HTTPS URL
    except:
        return None

NGROK_URL = get_ngrok_url()


@app.route('/')
def index():
    user_ip = request.remote_addr
    qr_code_url = url_for('generate_qr_code', url=NGROK_URL)
    print(f"url: {qr_code_url}")
    return render_template('index.html', qr_code_url=qr_code_url, user_ip=user_ip)

# @app.route('/')
# def index():
#     try:
#         # Get the machine's network IP address
#         hostname = socket.gethostname()
#         local_ip = socket.gethostbyname_ex(hostname)[2][-1]  # Get the last valid IP from the list
#     except socket.gaierror:
#         # Fallback to localhost if IP cannot be retrieved
#         local_ip = '127.0.0.1'

#     # Generate the QR code URL for the network IP
#     qr_code_url = url_for('generate_qr_code', url=f'http://{local_ip}:5000')
#     return render_template('index.html', qr_code_url=qr_code_url)

image = []

# # QR code generation route
# @app.route('/generate_qr', methods=['GET'])
# def generate_qr_code():
#     global image

#     # Retrieve the URL for which to generate the QR code
#     url = request.args.get('url', 'http://localhost:5000')

#     # Use qrcode.QRCode to create a larger QR code for better visibility
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=15,  # Increased size for easier scanning
#         border=4,
#     )
#     qr.add_data(url)
#     qr.make(fit=True)

#     # Create an image from the QR Code instance
#     img = qr.make_image(fill='black', back_color='white')

#     # Save the image to a buffer
#     buffer = io.BytesIO()
#     img.save(buffer, format='PNG')
#     buffer.seek(0)

#     # Store the image in the global variable
#     image.append(buffer.getvalue())

#     # Serve the image inline
#     response = make_response(buffer.getvalue())
#     response.headers['Content-Disposition'] = 'inline; filename=QRcode.png'
#     response.mimetype = 'image/png'
#     return response

@app.route('/generate_qr', methods=['GET'])
def generate_qr_code():
    url = request.args.get('url', NGROK_URL)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    buffer = io.BytesIO()
    qr.make_image(fill='black', back_color='white').save(buffer, format='PNG')
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'inline; filename=QRcode.png'
    response.mimetype = 'image/png'
    return response



# Additional function to access the global image if needed
@app.route('/get_qr_image')
def get_qr_image():
    global image
    if image:
        # Return the last stored image
        response = make_response(image[-1])
        response.headers['Content-Disposition'] = 'inline; filename=QRcode.png'
        response.mimetype = 'image/png'
        return response
    else:
        return "No QR code generated yet", 404




































@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'microphone.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/talk_with_us')
def talk_with_us():
    # Get the user's IP address, considering if they are behind a proxy (like Ngrok)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # If accessing from localhost, show the local view
    if user_ip == '127.0.0.1' or user_ip == '::1':
        qr_code_url = url_for('generate_qr_code', url=NGROK_URL)
        return render_template('local_talk.html', qr_code_url=qr_code_url, ip=user_ip)
    
    # For remote users, show the network user view with the Ngrok URL
    qr_code_url = url_for('generate_qr_code', url=NGROK_URL)
    return render_template('network_talk.html', qr_code_url=qr_code_url, ngrok_url=NGROK_URL)


# WebSockets for chat messages
message_queue = Queue()

# A dictionary to map IPs to "Speaker" IDs
ip_to_speaker = {}
messages = []  # Mock database to track messages
def get_speaker_id(ip):
    if ip not in ip_to_speaker:
        ip_to_speaker[ip] = f"Speaker {len(ip_to_speaker) + 1}"
    return ip_to_speaker[ip]



# Initialize speaker_order globally
speaker_order = 0

def get_speakers_order(order):
    """Generate a unique speaker ID based on the current order."""
    return f"Speaker {order + 1}"

# WebSocket for handling text messages
@socketio.on('send_message')
def handle_message(data):
    global speaker_order  # Use the global speaker_order variable
    speaker_id = get_speakers_order(speaker_order)  # Generate speaker_id based on the current order
    speaker_order += 1  # Increment the speaker order for the next client

    name = data.get('name', 'Unknown')     # Default to 'Unknown' if name is not provided
    major = data.get('major', 'Unknown')   # Default to 'Unknown' if major is not provided
    message = data.get('message', '')      # Default to an empty message if not provided
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

    # Prepare the message data
    message_data = {
        'id': len(messages) + 1,       # Unique ID for the message
        'speaker_id': speaker_id,      # Speaker ID
        'name': name,                  # User's name
        'major': major,                # User's background
        'message': message,            # Message content
        'timestamp': timestamp         # Timestamp of the message
    }

    # Add the message to the storage
    messages.append(message_data)

    # Broadcast the message to all connected clients
    socketio.emit('broadcast_message', message_data)

    # Optionally broadcast the speakers' order
    socketio.emit('speakers_order', {'order': speaker_order})



@socketio.on('delete_message')
def handle_delete_message(data):
    message_id = data.get('id')
    message_to_delete = next((msg for msg in messages if msg['id'] == message_id), None)

    if message_to_delete:
        messages.remove(message_to_delete)
        socketio.emit('delete_message', {'id': message_id})


# # WebSocket for deleting messages
# @socketio.on('delete_message')
# def handle_delete_message(data):
#     message_id = data.get('id')
#     message_to_delete = next((msg for msg in messages if msg['id'] == message_id), None)
#     if message_to_delete:
#         messages.remove(message_to_delete)
#         socketio.emit('delete_message', {'id': message_id})  # Broadcast delete event to all clients


# Message queue processing
def process_message_queue():
    while True:
        if not message_queue.empty():
            message_data = message_queue.get()
            socketio.emit('broadcast_message', message_data)
        time.sleep(1)















#########----- Call ----#################################

@socketio.on('call_started')
def handle_call_started(data):
    # Broadcast the event to all connected clients
    emit('call_started', data, broadcast=True)

@socketio.on('call_received')
def handle_call_started(data):
    print(f"call received from: {data['name']} ({data['major']})")

    # Broadcast the event to all connected clients
    emit('call_received', data, broadcast=True)




# WebSocket for handling connection requests
@socketio.on('request_to_connect')
def handle_request_to_connect(data):
    global speaker_order  # Use the global speaker_order variable
    speaker_id = get_speakers_order(speaker_order)  # Generate speaker_id based on the current order
    speaker_order += 1  # Increment the speaker order for the next client

    client_ip = request.remote_addr  # Get the client's IP address

    data.update({
        'speaker_id': speaker_id,
        'name': data.get('name', 'Unknown'),
        'major': data.get('major', 'Unknown'),
        'sender_ip': client_ip  # Include sender's IP
    })

    # Broadcast the acknowledgment with speaker ID
    socketio.emit('request_to_connect_ack', data)

    # Optionally broadcast the speakers' order
    socketio.emit('speakers_order', {'order': speaker_order})


# Optional handler to fetch the current speakers' order
@socketio.on('get_speakers_order')
def handle_get_speakers_order():
    socketio.emit('speakers_order', {'order': speaker_order})
    
       
@socketio.on('call_enabled')
def handle_call_enabled():
    # Broadcast the event to all clients, enabling the call button on the network user’s side
    print(f"call enabled")
    emit('call_enabled', broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    emit('user_left', {'message': 'A user has disconnected.'}, broadcast=True)

@socketio.on('hangup')
def handle_hangup(data):
    emit('hangup', {'id': data['id']}, broadcast=True)

# WebRTC signaling and speaker management
speakers = {}


@socketio.on('connect')
def test_connect():
    print("Client connected")


# WebRTC signaling
@socketio.on('offer')
def handle_offer(data):
    user_ip = request.remote_addr
    if user_ip not in ip_to_speaker:
        ip_to_speaker[user_ip] = f"Speaker {len(ip_to_speaker) + 1}"
    
    speaker_ip = request.remote_addr
    speaker_id = f'Speaker {len(speakers) + 1}'

    # Ensure that the 'offer' key exists in the data
    if 'offer' in data:
        speakers[speaker_id] = {'ip': speaker_ip, 'connection': data['offer']}
        emit('offer', {'offer': data['offer'], 'speaker_id': speaker_id}, broadcast=True)
    else:
        print("Error: No 'offer' key in the data")

    
@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, broadcast=True)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    emit('ice-candidate', data, broadcast=True)

def get_speaker_id(ip):
    if ip not in ip_to_speaker:
        ip_to_speaker[ip] = f"Speaker {len(ip_to_speaker) + 1}"
    return ip_to_speaker[ip]

# @socketio.on('hangup')
# def handle_hangup(data):
#     user_ip = request.remote_addr
#     speaker_id = get_speaker_id(user_ip)
#     if speaker_id:
#         emit('hangup', {'speaker_id': speaker_id}, broadcast=True)
#         print("Speaker hung up")
#     else:
#         emit('hangup', data, broadcast=True)
#         print("No speaker_id provided")

@socketio.on('hangup')
def handle_hangup(data):
    # Broadcast the hangup event to all connected clients
    emit('hangup', data, broadcast=True)
    print(f"Hangup event broadcasted by {request.remote_addr} with data: {data}")

@socketio.on('delete_speaking_request')
def handle_delete_speaking_request(data):
    # Broadcast the delete event to all connected clients with the message ID
    emit('delete_speaking_request', data, broadcast=True)



@app.route('/delete_speaker/<speaker_id>', methods=['DELETE'])
def delete_speaker(speaker_id):
    if speaker_id in speakers:
        del speakers[speaker_id]
        return jsonify({'message': f"Speaker {speaker_id} deleted"}), 200
    return jsonify({'message': "Speaker not found"}), 404

@socketio.on('delete_request_message')
def handle_delete_request_message(data):
    emit('delete_request_message', data, broadcast=True)


















#---------- Poll --------------#########################################################

class Poll(db.Model):
    __tablename__ = 'polls'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.relationship('PollOption', backref='poll', cascade="all, delete-orphan")

class PollOption(db.Model):
    __tablename__ = 'poll_options'
    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'))


# Create Poll (Local User Only)
@app.route('/local_create_poll', methods=['GET', 'POST'])
def local_create_poll():
    if request.method == 'GET':
        # Render the poll creation HTML page for local users
        return render_template('local_create_poll.html')

    # Handle POST logic for creating a poll
    try:
        data = request.get_json()
        if not data or 'questions' not in data:
            return jsonify(success=False, message="Invalid data format. 'questions' is missing."), 400

        polls = []
        for item in data['questions']:
            question_text = item.get('question')
            if not question_text.strip():
                return jsonify(success=False, message="Each question must have text."), 400

            poll = Poll(question=question_text.strip())
            for option_text in item.get('options', []):
                if option_text.strip():
                    poll_option = PollOption(option_text=option_text.strip())
                    poll.options.append(poll_option)

            polls.append(poll)

        db.session.add_all(polls)
        db.session.commit()

        created_poll = {
            "id": polls[-1].id,
            "question": polls[-1].question,
            "options": [{"id": option.id, "option_text": option.option_text} for option in polls[-1].options],
        }
        return jsonify(success=True, poll=created_poll)

    except Exception as e:
        db.session.rollback()
        print(f"Error creating poll: {e}")
        return jsonify(success=False, message="An error occurred while creating the poll."), 500


# Fetch Polls for Network Users to Vote
@app.route('/polls', methods=['GET'])
def display_questions():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    is_local = user_ip in ('127.0.0.1', '::1')
    print(f"User IP: {user_ip}, Is Local: {is_local}, Poll Released: {poll_released}")
    
    if is_local or poll_released:
        polls = Poll.query.all()
    else:
        polls = []

    # Format polls data properly
    polls_data = [
        {
            "id": poll.id,
            "question": poll.question,
            "options": [
                {"id": option.id, "option_text": option.option_text, "votes": option.votes}
                for option in poll.options
            ],
        }
        for poll in polls
    ]

    print(f"Polls data sent to client: {polls_data}")
    return jsonify(success=True, polls=polls_data)



@app.route('/network_vote')
def network_vote():
    return render_template('network_vote.html')


# Handle Voting
@app.route('/poll/<int:poll_id>/vote', methods=['POST'])
def vote(poll_id):
    try:
        option_id = request.form.get('option_id')
        option = PollOption.query.get(option_id)
        if option:
            option.votes += 1
            db.session.commit()
            return jsonify(success=True, message="Vote recorded successfully.")
        return jsonify(success=False, message="Option not found"), 404
    except Exception as e:
        print(f"Error processing vote: {e}")
        return jsonify(success=False, message="An error occurred while processing the vote."), 500




# Poll Results (Charts for Both Local and Network Users)
@app.route('/polls/results', methods=['GET'])
def display_polls_with_charts():
    """
    Render the Poll Results page with dynamically generated data for bar charts.
    This function fetches all polls and their options from the database, organizes the data,
    and passes it to the `poll_results.html` template.
    """
    try:
        # Query all polls and their options from the database
        polls = Poll.query.all()

        # Organize poll data into a format suitable for rendering
        polls_data = [
            {
                "id": poll.id,
                "question": poll.question,
                "options": [
                    {"id": option.id, "option_text": option.option_text, "votes": option.votes}
                    for option in poll.options
                ],
            }
            for poll in polls
        ]

        # Render the poll_results.html template with the polls data
        return render_template('poll_results.html', polls=polls_data)

    except Exception as e:
        # Handle errors gracefully by logging and rendering an empty page
        print(f"Error fetching polls: {e}")
        return render_template('poll_results.html', polls=[])


# Delete All Polls (Admin Utility for Local Users)
@app.route('/delete_all_polls', methods=['DELETE'])
def delete_all_polls():
    try:
        PollOption.query.delete()  # Delete all options first
        Poll.query.delete()       # Delete all polls
        db.session.commit()
        return jsonify(success=True, message="All polls deleted successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting polls: {e}")
        return jsonify(success=False, message="An error occurred while deleting polls."), 500


# Release Polls for Network Users
poll_released = False
poll_timer_expiry = None  # To track when the timer expires


# Release Polls for Network Users
@app.route('/release_poll', methods=['POST'])
def release_poll():
    global poll_released
    try:
        poll_released = not poll_released  # Toggle poll release state
        return jsonify(success=True, released=poll_released)
    except Exception as e:
        print(f"Error toggling poll release state: {e}")
        return jsonify(success=False, message="Failed to toggle poll release state."), 500


# # Get Timer State
# @app.route('/polls/timer', methods=['GET'])
# def get_poll_timer():
#     global poll_timer_expiry
#     try:
#         time_remaining = poll_timer_expiry - time.time() if poll_timer_expiry else None
#         return jsonify(success=True, time_remaining=time_remaining if time_remaining > 0 else 0)
#     except Exception as e:
#         print(f"Error fetching timer state: {e}")
#         return jsonify(success=False, message="Failed to fetch timer state."), 500

@app.route('/start_timer', methods=['POST'])
def start_timer():
    global poll_timer_expiry
    try:
        timer_duration = 60
        poll_timer_expiry = time.time() + 60  # Set timer to 60 seconds
        
        # Emit the startTimer event to all clients
        socketio.emit('startTimer', {'time_remaining': 60})
        def timer_expiry():
            time.sleep(timer_duration)  # Wait for the timer to expire
            socketio.emit('timeUp')  # Notify clients that the timer has ended

        timer_expiry()
        return jsonify(success=True, time_remaining=60)
    except Exception as e:
        print(f"Error starting timer: {e}")
        return jsonify(success=False, message="Failed to start timer.")




@app.route('/get_poll_state', methods=['GET'])
def get_poll_state():
    try:
        return jsonify(success=True, released=poll_released)
    except Exception as e:
        print(f"Error fetching poll state: {e}")
        return jsonify(success=False, message="Failed to fetch poll state."), 500


@app.context_processor
def inject_poll_state():
    try:
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        is_local = user_ip in ('127.0.0.1', '::1')
        return {'is_local': is_local, 'poll_released': poll_released}
    except Exception as e:
        print(f"Error injecting poll state: {e}")
        return {'is_local': False, 'poll_released': poll_released}


# Local user existing polls
@app.route('/poll/<int:poll_id>/delete', methods=['DELETE'])
def delete_poll(poll_id):
    try:
        poll = Poll.query.get(poll_id)
        if poll:
            db.session.delete(poll)
            db.session.commit()
            return jsonify(success=True, message="Poll deleted successfully.")
        else:
            return jsonify(success=False, message="Poll not found.")
    except Exception as e:
        return jsonify(success=False, message=f"Error deleting poll: {e}")

@app.route('/poll/<int:poll_id>/option/<int:option_id>/delete', methods=['DELETE'])
def delete_option(poll_id, option_id):
    try:
        option = PollOption.query.filter_by(id=option_id, poll_id=poll_id).first()
        if option:
            db.session.delete(option)
            db.session.commit()
            return jsonify(success=True, message="Option deleted successfully.")
        else:
            return jsonify(success=False, message="Option not found.")
    except Exception as e:
        return jsonify(success=False, message=f"Error deleting option: {e}")



















# Main ############################################################
# Start the queue processing in a background thread
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    queue_thread = Thread(target=process_message_queue)
    queue_thread.daemon = True  # Ensures it exits when the main program does
    queue_thread.start()

    socketio.run(app, host='0.0.0.0', debug=True)
