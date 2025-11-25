"""
Peter Kyle 2024
peter@pkcubed.net
5094339382

This is the audio portion of the J2B Timekeeping system.
This plays a background audio track as well as audio cues when triggered by GET requests from the timekeeping controller.
"""
import pygame
import threading
from flask import Flask
import time

app = Flask(__name__)

pygame.init()

# Initialize mixer for audio
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("background.wav")  # Replace with your music file
pygame.mixer.music.play(-1)  # Play on loop

# Load sound effects
sound_effect1 = pygame.mixer.Sound("303030.wav")  # Replace with your sound effect
sound_effect2 = pygame.mixer.Sound("GOGOGO.wav")  # Replace with your sound effect

sound_effect1.set_volume(0.8)
sound_effect2.set_volume(1.3) # Was set to 0.9 before, increased to 1.3 for 2025 to be a little louder

trigger1 = False
trigger2 = False
background_play = None

@app.route('/303030')
def play_sound_effect1():
    global trigger1
    print("303030 Received")
    trigger1 = True
    return "Success"

@app.route('/GOGOGO')
def play_sound_effect2():
    global trigger2
    print("GOGOGO Received")
    trigger2 = True
    return "Success"

@app.route('/STOP')
def stop_background():
    global background_play
    print("STOP Received")
    background_play = False
    return "Success"

@app.route('/START')
def start_background():
    global background_play
    print("START Received")
    background_play = True
    return "Success"

def run_flask_app():
    app.run(host='0.0.0.0')

# Start the Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.start()

# Main loop
while True:
	if trigger1:
		sound_effect1.play()
		trigger1 = False
	if trigger2:
		sound_effect2.play()
		trigger2 = False

	if background_play == True:
		background_play = None
		pygame.mixer.music.play(-1)
	elif background_play == False:
		background_play = None
		pygame.mixer.music.stop()
	
	
	# Check for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()