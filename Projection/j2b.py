call_duration = 2 # Seconds



import threading
from flask import Flask, request, jsonify
import pygame
import sys
import time
import requests

timekeeper_ip = "10.12.0.1"

app = Flask(__name__)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((1900, 1080), pygame.NOFRAME)
pygame.display.set_caption("Pygame with Web GUI")
num_font = pygame.font.Font("font.ttf", 400)
now_calling_font = pygame.font.Font("font.ttf", 100)
current_group_font = pygame.font.Font("font.ttf", 40)
performer_font = pygame.font.Font("font.ttf", 40)
current_group_num = 0
call_timer = 0
performer_text = ''

def update_group_num():
    global current_group_num
    global call_timer
    while True:
        # Check for new text received from the server
        data = request.get_json()
        if data and 'new_group_num' in data:
            current_group_num = data['new_group_num']
            call_timer = time.time()
            break  # Exit the loop after receiving new text

def update_performer_text():
    global performer_text
    while True:
        # Check for new text received from the server
        data = request.get_json()
        if data and 'new_performer_text' in data:
            performer_text = data['new_performer_text']
            break  # Exit the loop after receiving new text

@app.route('/update_group_num', methods=['POST'])
def update_group_num_route():
    update_group_num()
    return jsonify({'status': 'success'})

@app.route('/update_performer_text', methods=['POST'])
def update_performer_text_route():
    update_performer_text()
    return jsonify({'status': 'success'})

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Screen Control Panel</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&family=SUSE:wght@100..800&display=swap');
        body {
            background-color: black;
            color: white;
            font-family: "Nunito", sans-serif;
            font-size: 40px;
            text-align: center;
        }
        .btn {
            border: none;
            text-decoration: none;
            background-color: #222;
            color: white;
            padding: 30px 50px;
            width: 80%;
            margin: 10px;
            border-radius: 20px;
            font-size: 80px;
            cursor: pointer;
            display: inline-block;
        }
        .btn:hover {background: #eee;}
        </style>
    </head>
    <body>
        <a class="btn" href="/groups">Call Groups</a><br>
        <a class="btn" href="/performers">Change Performers</a>
    </body>
    </html>
    '''

@app.route('/groups')
def groups():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Group Control Panel</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&family=SUSE:wght@100..800&display=swap');
        body {
            background-color: black;
            color: white;
            font-family: "Nunito", sans-serif;
            font-size: 100px;
            text-align: center;
            line-spacing
        }
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {  

           opacity: 1;

        }
        .number {
            width: 90%;
            font-size: 150px;
            text-align: center;
            border-radius: 20px;
        }
        .master-clock {
            border-style: solid;
            border-radius: 20px;
            width: 90%;
            border-width: 2px;
            border-color: white;
            margin: auto;
            margin-top: 40px;
        }
        .btn {
            font-family: "Nunito", sans-serif;
            border: none;
            text-decoration: none;
            background-color: #222;
            color: white;
            padding-top: 50px;
            padding-bottom: 50px;
            width: 90%;
            margin: 0;
            margin-top: 40px;
            border-radius: 20px;
            font-size: 100px;
            cursor: pointer;
            display: inline-block;
        }
        p {
            margin: 0;
        }
        h4 {
            margin: 0;
        }
        .btn:hover {background: #aaa;}
        .btn:active {background: #ddd;}
        </style>
    </head>
    <body>
        <div class="callgroup">
        <input class="number" type="number" id="group_num_input" value="'''+ str(int(current_group_num)+1) +'''">
        <br>
        <button class="btn" onclick="callGroup()">Call Group</button>
        </div>
        <div class="master-clock">
            <h4>Master Clock: </h4>
            <p id="mclock"></p>
            <p id="countdown-clock"></p>
            <p id="status"></p>
        </div>
        <a class="btn" href="/">Home</a>
    </body>
    <script>
        var trigger_timer;
        const mclock = document.getElementById("mclock");
        const countdown_clock = document.getElementById("countdown-clock");
        const status_element = document.getElementById("status");
        function callGroup() {
            const group_num_input = document.getElementById("group_num_input");
            const newGroupNum = group_num_input.value;
            group_num_input.value = parseInt(newGroupNum) + 1;
            fetch('/update_group_num', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({new_group_num: newGroupNum})
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error(error);
            });
        }
        function pad(num, size) {
            num = num.toString();
            while (num.length < size) num = "0" + num;
            return num;
        }
        function getTime() {
            fetch("/time")
            .then(response => response.json())
            .then(data => {
                trigger_timer = Math.floor(parseFloat(data));
            });
            //console.log(trigger_timer);
            if (trigger_timer != -1) {
                var hours = pad(Math.floor((trigger_timer-30) / (60*60)),2);
                var minutes = pad((Math.floor((trigger_timer-30) / 60) % 60),2);
                var seconds = pad(((trigger_timer-30) % (60)),2);
                var cd_minutes = 3-(minutes % 4);
                var cd_seconds = 60-(seconds % (4*60));
                if (seconds < 0) {
                    hours = 0;
                    minutes = 0;
                }
                mclock.innerHTML = hours.toString() + ":" + minutes.toString() + ":" + seconds.toString();
                countdown_clock.innerHTML = pad(cd_minutes.toString(), 1) + ":" + pad(cd_seconds.toString(), 2);
                if (cd_minutes == 0 && cd_seconds <= 30) {
                    status_element.innerHTML = "30 30 30";
                } else if (cd_minutes == 3 && cd_seconds >= 50) {
                    status_element.innerHTML = "GO GO GO";
                } else {
                    status_element.innerHTML = "Running";
                }
            } else {
                mclock.innerHTML = "";
                countdown_clock.innerHTML = "";
                status_element.innerHTML = "Idle";
            }
        }
        setInterval(getTime, 250);
    </script>
    </html>
    '''

@app.route('/performers')
def performers():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performers Control Panel</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&family=SUSE:wght@100..800&display=swap');
        body {
            background-color: black;
            color: white;
            font-family: "Nunito", sans-serif;
            font-size: 100px;
            text-align: center;
            line-spacing
        }
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {  

           opacity: 1;

        }
        .number {
            width: 90%;
            font-size: 150px;
            text-align: center;
            border-radius: 20px;
        }
        .master-clock {
            border-style: solid;
            border-radius: 20px;
            width: 90%;
            border-width: 2px;
            border-color: white;
            margin: auto;
        }
        .btn {
            font-family: "Nunito", sans-serif;
            border: none;
            text-decoration: none;
            background-color: #222;
            color: white;
            padding-top: 50px;
            padding-bottom: 50px;
            width: 90%;
            margin: 0;
            margin-top: 40px;
            border-radius: 20px;
            font-size: 100px;
            cursor: pointer;
            display: inline-block;
        }
        p {
            margin: 0;
        }
        h4 {
            margin: 0;
        }
        .btn:hover {background: #aaa;}
        .btn:active {background: #ddd;}
        </style>
    </head>
    <body>
        <input class="number" type="text" id="performer_text_input" value="'''+ str(performer_text) +'''">
        <button class="btn" onclick="submitText()">Submit Text</button>
        <a class="btn" href="/">Home</a>
    </body>
    <script>
        function submitText() {
            const newPerformerText = document.getElementById("performer_text_input").value;
            fetch('/update_performer_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({new_performer_text: newPerformerText})
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error(error);
            });
        }
    </script>
    </html>
    '''

@app.route('/time')
def timekeeper():
    data = requests.get("http://"+timekeeper_ip+":5000").content.decode("utf-8")
    trigger_time = float(data)
    return str(trigger_time)

def pygame_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        if call_timer + call_duration > time.time():
            text1_surface = now_calling_font.render("Now calling group", True, (255,255,255))
            screen.blit(text1_surface, (screen.get_size()[0]/2-text1_surface.get_size()[0]/2,screen.get_size()[1]/2-text1_surface.get_size()[1]/2-300))
            groupnum_text_surface = num_font.render(str(current_group_num), True, (255, 255, 255))
            screen.blit(groupnum_text_surface, (screen.get_size()[0]/2-groupnum_text_surface.get_size()[0]/2,screen.get_size()[1]/2-groupnum_text_surface.get_size()[1]/2))
        else:
            if not current_group_num == 0:
                text2_surface = current_group_font.render("Current group: " + str(current_group_num), True, (255,255,255))
                screen.blit(text2_surface, (screen.get_size()[0]-text2_surface.get_size()[0]-100,screen.get_size()[1]-text2_surface.get_size()[1]-40))
            if performer_text:
                performer_text_surface = current_group_font.render("Now performing: " + str(performer_text), True, (255,255,255))
                screen.blit(performer_text_surface, (100,screen.get_size()[1]-performer_text_surface.get_size()[1]-40))
        pygame.display.flip()

if __name__ == '__main__':
    # Start Flask server in a separate thread
    def run_server():
        app.run(host='0.0.0.0', port=80)

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Run Pygame loop in the main thread
    pygame_loop()
    server_thread.stop()
