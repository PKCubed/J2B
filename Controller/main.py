"""
Written by Peter Kyle 2024 for Journey to Bethlehem Timekeeping
Wenatchee WA Seventh Day Adventist Church
Any questions or comments, please contact me at
peter@pkcubed.net
(***) ***-****
These contacts may not work in the future, but please try to reach out to me however possible.

Feel free to leave your name below to let others know that you've been here and what you did:
- Peter Kyle 2024
	If your seeing this, you're either really curious or something is not working... Good luck to you!
	This was a lot of fun to create and I hope it continues to be used in the distant future. J2B is a blessing to a lot of people.

	Description of this program:
	This is designed to run on a Raspberry Pi 4b with 2 buttons attached, each with an led, and a 20x4 character LCD.
	It's purpose is to control candles in the J2B village as well as audio cues to tell the groups to move on after 4 minutes.
	Traditionally this has been done by FRS radio with a timekeeper speaking into the radio "30 30 30" and "GO GO GO" when 30 seconds were left on the clock and when the 4 minutes had elapsed respectively.
	Hopefully this will prove to be a better solution, both easier to use, and more effective. I've heard that the radios were very much not reliable.
	This also sends the timekeeping time, or rather makes it available for other things to see. Primarily the computer in the balcony responsible for projection which has a program running on it for displaying the group number and the performers on stage.
	That program then has a web interface that allows users to modify the group number, change the performer, and show them the timekeeping time. This way they know when to call the next group of people from the sanctuary.
	This program sends GET requests to another raspberry pi which is responsible for playing the audio cues. It is connected to a speaker amp and a bunch of speakers.


"""

start_text="J2B Timekeeper Panel"
running_text = "J2B Timekeeper Panel"

message = ""
last_message = ""

audio_player_ip_address = "10.12.2.1"

from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import time
start_time = time.time()
import math
import datetime
from flask import Flask
import threading
import requests

candles_1_pin = 22
candles_2_pin = 27

mode_button_pin = 24
mode_led_pin = 5
trigger_button_pin = 23
trigger_led_pin = 6

button_debounce_time = 0.100

total_duration = 4 *60 # 4 Minutes
timer_duration = 30 # 30 Seconds
go_duration = 10 # 10 Seconds

mode = "Manual"

trigger_timer = 0

trigger_button_state = 0
trigger_button_last_state = 0
trigger_button_debounce_timer = 0

mode_button_state = 0
mode_button_last_state = 0
mode_button_debounce_timer = 0
cycles = 0
cycles_pre_go = 0
last_count = total_duration + 1
last_status = ""

def send_message(text):
	global message
	tstamp = time.time()
	print(tstamp)
	message = (str(datetime.datetime.fromtimestamp(tstamp).strftime("%-H:%M:%S"))+"-"+text)[0:20]
	print(datetime.datetime.fromtimestamp(tstamp))
	

app = Flask(__name__)

@app.route('/')
def time_page():
	if trigger_timer:
		return str(time.time()-trigger_timer)
	else:
		return "-1"

def update_status():
	global cycles
	global last_count
	global last_status
	global cycles_pre_go
	global trigger_timer
	global message
	global last_message
	
	if mode == "Manual":
	
		if time.time() <= trigger_timer + timer_duration:
			status = "30 30 30!"
			if status != last_status:
				print(status)
				candle_burnout_1()
				audio_303030()
				last_status = status
				lcd.home()
				lcd.write_string(status+(" "*(9-len(status))))
		
			countdown = math.ceil(timer_duration+trigger_timer-time.time())
			if countdown != last_count:
				last_count = countdown
				lcd.cursor_pos = (1,0) # 2nd Line
				lcd.write_string(str(datetime.datetime.fromtimestamp(countdown).strftime("%-M:%S"))+(" "*(8-len(str(datetime.timedelta(seconds=countdown))))))
			led_value = math.ceil((timer_duration+trigger_timer-time.time()) % 0.5 * 4 - 1)
			GPIO.output(trigger_led_pin, led_value)
		elif time.time() <= trigger_timer + timer_duration + go_duration:
			status = "Go Go Go!"
			if status != last_status:
				print(status)
				candle_burnout_2()
				audio_GOGOGO()
				last_status = status
				lcd.home()
				lcd.write_string(status+(" "*(9-len(status))))
				lcd.cursor_pos = (1,0) # 2nd Line
				lcd.write_string(" "*9)
			
			GPIO.output(trigger_led_pin, 1)
		else:
			status = "Idle"
			if status != last_status:
				print(status)
				reset_candles()
				trigger_timer = 0
				last_status = status
				lcd.home()
				lcd.write_string(status+(" "*(9-len(status))))
				lcd.cursor_pos = (1,0) # 2nd Line
				lcd.write_string(" "*9)
			GPIO.output(trigger_led_pin, 0)
			
	elif mode == "Automatic":
		if trigger_timer:
			mode_led_value = math.ceil((trigger_timer-time.time()) % 0.5 * 4 - 1)
			GPIO.output(mode_led_pin, mode_led_value)
		
			if time.time() <= trigger_timer + timer_duration + ((total_duration) * (cycles)) and time.time() >= trigger_timer + (total_duration * cycles): # Countdown
				status = "30 30 30!"
				if status != last_status:
					print(status)
					candle_burnout_1()
					audio_303030()
					last_status = status
					lcd.home()
					lcd.write_string(status+(" "*(9-len(status))))
			
				countdown = math.ceil(timer_duration + ((total_duration) * (cycles))+trigger_timer-time.time())
				if countdown != last_count:
					last_count = countdown
					lcd.cursor_pos = (1,0) # 2nd Line
					lcd.write_string(str(datetime.datetime.fromtimestamp(countdown).strftime("%-M:%S"))+(" "*(8-len(str(datetime.timedelta(seconds=countdown))))))
					#print(str(countdown))
				led_value = math.ceil((timer_duration + ((total_duration) * (cycles))+trigger_timer-time.time()) % 0.5 * 4 - 1)
				GPIO.output(trigger_led_pin, led_value)
	
	
				
			elif time.time() <= trigger_timer + timer_duration + go_duration + ((total_duration) * (cycles)) and time.time() >= trigger_timer + timer_duration + (total_duration * (cycles)): # GO GO GO
			
				status = "Go Go Go!"
				if status != last_status:
					print(status)
					candle_burnout_2()
					audio_GOGOGO()
					last_status = status
					lcd.home()
					lcd.write_string(status+(" "*(9-len(status))))
					cycles_pre_go += 1
					if cycles_pre_go >= 100:	
						lcd.cursor_pos = (1,9) # 2nd Line
						lcd.write_string("  Cycles: " + str(cycles_pre_go) + (" "*(10-len("Cycles: "+str(cycles_pre_go)))))
					elif cycles_pre_go >= 10:	
						lcd.cursor_pos = (1,10) # 2nd Line
						lcd.write_string(" Cycles: " + str(cycles_pre_go) + (" "*(10-len("Cycles: "+str(cycles_pre_go)))))
					else:
						lcd.cursor_pos = (1,11) # 2nd Line
						lcd.write_string("Cycles: " + str(cycles_pre_go) + (" "*(10-len("Cycles: "+str(cycles_pre_go)))))
					
					print("Cycles: " + str(cycles_pre_go) + (" "*(10-len("Cycles: "+str(cycles_pre_go)))))
					
				countdown = math.ceil(timer_duration + ((total_duration) * (cycles+1))+trigger_timer-time.time())
				if countdown != last_count:
					last_count = countdown
					lcd.cursor_pos = (1,0) # 2nd Line
					lcd.write_string(str(datetime.datetime.fromtimestamp(countdown).strftime("%-M:%S"))+(" "*(8-len(str(datetime.timedelta(seconds=countdown))))))
					#print(str(countdown))
					
				GPIO.output(trigger_led_pin, 1)
	
				
			elif time.time() >= trigger_timer + timer_duration + go_duration + (total_duration * (cycles)):
				if trigger_timer:
					cycles += 1
	
	
					
			else:
				GPIO.output(trigger_led_pin, 0)
				
				status = "Running"
				if status != last_status:
					print(status)
					reset_candles()
					last_status = status
					lcd.home()
					lcd.write_string(status+(" "*(10-len(status))))
				
				countdown = math.ceil(timer_duration + ((total_duration) * (cycles))+trigger_timer-time.time())
				if countdown == timer_duration:
					lcd.cursor_pos = (1,0) # 2nd Line
					lcd.write_string(" "*10)
				else:
					if countdown != last_count:
						last_count = countdown
						lcd.cursor_pos = (1,0) # 2nd Line
						lcd.write_string(str(datetime.datetime.fromtimestamp(countdown).strftime("%-M:%S"))+(" "*(8-len(str(datetime.timedelta(seconds=countdown))))))
						#print(str(countdown))
		else:
			status = "Idle"
			if status != last_status:
				print(status)
				reset_candles()
				last_status = status
				lcd.home()
				lcd.write_string(status+(" "*(9-len(status))))
				lcd.cursor_pos = (1,0) # 2nd Line
				lcd.write_string(" "*9)
			GPIO.output(trigger_led_pin, 0)

	if message != last_message:
		lcd.cursor_pos = (2,0)
		lcd.write_string(message(" "*(20-len(status)))
		last_message = message

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4, dotsize=8)
lcd.clear()

lcd.write_string(start_text)
lcd.cursor_pos = (3,0) # Bottom Line
lcd.write_string('Starting...')

GPIO.setmode(GPIO.BCM)
GPIO.setup(mode_led_pin, GPIO.OUT)
GPIO.setup(trigger_led_pin, GPIO.OUT)
GPIO.setup(mode_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(trigger_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(candles_1_pin, GPIO.OUT)
GPIO.setup(candles_2_pin, GPIO.OUT)

GPIO.output(mode_led_pin, 1)
GPIO.output(trigger_led_pin, 1)

def reset_candles():
	GPIO.output(candles_1_pin, 1)
	GPIO.output(candles_2_pin, 1)

def candle_burnout_1():
	GPIO.output(candles_1_pin, 0)
	GPIO.output(candles_2_pin, 1)

def candle_burnout_2():
	GPIO.output(candles_1_pin, 0)
	GPIO.output(candles_2_pin, 0)


def get_303030():
	try:
		response = requests.get("http://"+audio_player_ip_address+":5000/303030", timeout=2) # Timeout after 2 seconds
		if response.status_code != 200:
			send_message("Audio Conn Err")
			print("Status code error")
	except Exception as err:
		send_message("Audio Error")
		print("Error while sending GET request to play audio 303030: ")
		print(err)
		print()
	
def get_GOGOGO():
	try:
		response = requests.get("http://"+audio_player_ip_address+":5000/GOGOGO", timeout=2) # Timeout after 2 seconds
		if response.status_code != 200:
			send_message("Audio Conn Err")
			print("Status code error")
	except Exception as err:
		send_message("Audio Error")
		print("Error while sending GET request to play audio GOGOGO: ")
		print(err)
		print()
	

def audio_303030():
	request_thread = threading.Thread(target=get_303030)
	request_thread.start()
	
def audio_GOGOGO():
	request_thread = threading.Thread(target=get_GOGOGO)
	request_thread.start()
	

reset_candles()

def run_server():
	app.run(host='0.0.0.0')

server_thread = threading.Thread(target=run_server)
server_thread.start()


while time.time() <= start_time + 1:
	continue

lcd.clear()
lcd.cursor_pos = (3,0)
lcd.write_string(start_text)

lcd.cursor_pos = (0, 20-len(mode))
lcd.write_string(mode)

GPIO.output(mode_led_pin, 0)
GPIO.output(trigger_led_pin, 0)

while True:
	if not GPIO.input(mode_button_pin):
		mode_button_debounce_timer = time.time()
		mode_button_state = 1
	elif mode_button_debounce_timer + button_debounce_time < time.time():
		mode_button_state = 0

	if not GPIO.input(trigger_button_pin):
		trigger_button_debounce_timer = time.time()
		trigger_button_state = 1
	elif trigger_button_debounce_timer + button_debounce_time < time.time():
		trigger_button_state = 0
	
	if trigger_button_state:
		if not trigger_button_last_state: # Trigger Button Rising Edge
			#print("Rising Edge Trigger")
			if trigger_timer:#time.time() <= trigger_timer + timer_duration: # Cancel the current que
				#print("Trigger timer")
				if (time.time() - trigger_timer) < timer_duration and mode == "Manual":
					#print("during 30 30 30")
					trigger_timer = time.time()-timer_duration
					#print("GO Time")
				else:
					trigger_timer = 0
					cycles = 0
					cycles_pre_go = 0
					lcd.cursor_pos = (1,10) # 2nd Line
					lcd.write_string((" "*10))
					if mode == "Manual":
						GPIO.output(mode_led_pin, 0)
					elif mode == "Automatic":
						GPIO.output(mode_led_pin, 1)
			else:
				trigger_timer = time.time()
		else: # Trigger Button Falling Edge
			pass
	trigger_button_last_state = trigger_button_state
	if mode_button_state:
		if not mode_button_last_state: # Trigger Button Rising Edge
			if mode == "Manual":
				mode = "Automatic"
				cycles = 0
				cycles_pre_go = 0
				lcd.cursor_pos = (1,10) # 2nd Line
				lcd.write_string((" "*10))
				trigger_timer = 0
				reset_candles()
				GPIO.output(mode_led_pin, 1)
			elif mode == "Automatic":
				mode = "Manual"
				cycles = 0
				cycles_pre_go = 0
				lcd.cursor_pos = (1,10) # 2nd Line
				lcd.write_string((" "*10))
				trigger_timer = 0
				reset_candles()
				GPIO.output(mode_led_pin, 0)
				
			lcd.cursor_pos = (0, 10)
			lcd.write_string((" "*(10-len(mode)))+mode)
		else: # Trigger Button Falling Edge
			pass
	mode_button_last_state = mode_button_state

	update_status()

		
GPIO.cleanup()
