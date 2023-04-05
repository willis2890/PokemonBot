import websocket
import json
import threading
import time
import pyautogui
import asyncio
import random
import pygame
import re
import argparse
from constants import channel_id, token, positions, xValue, yValue, caught, failed, ran, ball_map, counter, fishOffSet
from art import *

width = 64
text = text2art("Poke - slave", font="ogre")
print("\033[95m" + text + "\033[0m")

#argument parser
parser = argparse.ArgumentParser(description='PokeSlave')
parser.add_argument('-f', '--fish', nargs='?', type=int, default=999, help='Number of encounters before fishing')

args = parser.parse_args()
fishNumber = args.fish

if fishNumber != 999:
    print(f"Will catch fish after every {fishNumber} Pokemon encounters".center(width, ' '))
else:
    print("------Did not specify number of encounters before fishing-------\n-------------Default: will fish after 999 encounters------------")


###WEBSOCKET###
def send_json_request(ws, request):
    ws.send(json.dumps(request))

def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)
    else:
        return None

def heartbeat(interval, ws):
    print('\n')
    print(f"{'| WE ALIVE! |'.center(width, '=')}")
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": None
        }
        send_json_request(ws, heartbeatJSON)
        print("\033[91mHeartbeat sent!\033[0m")
 
ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / 1000
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

payload = {
    'op': 2,
    "d": {
        "token": token,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": 'pc'
        },
        "channel_id": channel_id,
    }
}
send_json_request(ws, payload)


###LOAD MUSIC###
pygame.mixer.init()
pygame.mixer.music.load("battle.mp3")

###HASHSET FOR MESSAGE IDS###
seen_message_ids = set()
max_message_ids = 100

###DEFINITIONS###
def captchaCheck(message):
    title = message[0]['description']
    if "captcha" in title.lower():
        a = text2art("Captcha!","ogre")
        print("\033[31m" + a + "\033[0m")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()
        start_time = time.time()
        while time.time() - start_time < 10:
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        return True
    else:
        return False


def pb_reader(message):
    ballRegx = message[0]['footer']['text']
    pb = int(re.search(r"Pokeballs : (\d{1,3}(,\d{3})*|\d+)", ballRegx).group(1).replace(',', ''))
    gb = int(re.search(r"Greatballs: (\d{1,3}(,\d{3})*|\d+)", ballRegx).group(1).replace(',', ''))
    ub = int(re.search(r"Ultraballs: (\d{1,3}(,\d{3})*|\d+)", ballRegx).group(1).replace(',', ''))
    mb = int(re.search(r"Masterballs: (\d{1,3}(,\d{3})*|\d+)", ballRegx).group(1).replace(',', ''))
    namePrint = 'Balls Left! PB: {} GB: {} UB: {} MB: {}'.format(pb, gb, ub, mb)
    namePrint = namePrint.center(width, ' ')
    print(namePrint)

    if pb < 10:
        return 0
    if gb < 10:
        return 1
    if ub < 5:
        return 2
    if mb < 2:
        return 3
    else:
        return 69

def checkSuccess(message):
    global caught, failed, ran, counter
    if message[0] == 'Y':
        print('CAUGHT!'.center(width, ' '))
        caught += 1
    elif message[0] == '<':
        print('FAILED!'.center(width, ' '))
        failed += 1
    elif message[0] == '*':
        print('| L CODE NIGGA RAN! |'.center(width, '-'))
        ran += 1
    total = caught + failed
    try:
        catch_rate = caught/total
        catch_rate = "{:.2%}".format(catch_rate)
    except ZeroDivisionError:
        if failed == 0:
            catch_rate = "100.00%"
    #s = 'Caught:'+str(caught)+' Failed:'+str(failed)
    c = 'Total: ' + str(total)
    e = 'Catch Rate: ' +str(catch_rate)
    
    #print(s.center(width, ' '))
    print(c.center(width, ' '))
    print(e.center(width, ' '))
    counter += 1
    #print('Fishing Counter:', counter)

def poke_name(message):
    poke = message[0]['description'].split('**')[-2]
    if "rod" in poke:
        print(f"\033[94m{'!!BLUB BLUB FISHING!!'.center(width, '>')}\033[0m".center(width, '<'))
    else:
        s = 'POKEMON: ' + poke
        print(s.center(width, ' '))
    
def rarity_poke_clicker(message):
    ball_text = message[0]['footer']['text']  
    rarity = ball_text.split()[0]
    s = 'Rarity: ' + rarity
    if rarity == 'Common':
        print("\033[34m" + s.center(width, ' ') + "\033[0m")
    elif rarity == 'Uncommon':
        print("\033[94m" + s.center(width, ' ') + "\033[0m")
    elif rarity == 'Rare':
        print("\033[33m" + s.center(width, ' ') + "\033[0m")
    elif rarity == 'Super':
        print("\033[33m\033[1m" + s.center(width, ' ') + "\033[0m")
    elif rarity == 'Legendary':
        print("\033[35m" + s.center(width, ' ') + "\033[0m")
    elif rarity == 'Shiny':
        print("\033[95m" + s.center(width, ' ') + "\033[0m")
    if rarity in ball_map:
        position_index = ball_map[rarity]
        x, y = positions[position_index]
        pyautogui.click(x, y, duration=1)
    else:
        print("I COULDNT READ RARITY IM A DUMBASS.")

def buyBalls(numbuh):
    # click the ball shop button
    pyautogui.click(xValue,yValue)

    # enter the command to buy balls
    if numbuh == 69:
        pass
    if numbuh == 0:
        pyautogui.typewrite(';s b 1 40\n', interval=0.2)
    elif numbuh == 1:
        pyautogui.typewrite(';s b 2 20\n', interval=0.2)
    elif numbuh == 2:
        pyautogui.typewrite(';s b 3 10\n', interval=0.2)
    elif numbuh == 3:
        pyautogui.typewrite(';s b 4 1\n', interval=0.2)
def daSummoning(a, b):
    random_milliseconds = random.randint(a, b)
    time.sleep(random_milliseconds / 1000.0)
    pyautogui.click(xValue,yValue)
    pyautogui.typewrite(';p\n', interval=0)
def daFish():
    time.sleep(1)
    pyautogui.click(xValue, yValue)
    pyautogui.typewrite('/fis', interval=0.2)
    pyautogui.press('tab')
    pyautogui.press('enter')
def clickFishPart1():
    time.sleep(0.5)
    x,y = positions[0]
    pyautogui.click(x,y)
def clickFishPart2():
    time.sleep(1.5)
    x,y = positions[5]
    pyautogui.click(x,y)
    
def fishName(message):
    fish = message.split('**')[-2]
    s = 'Fishy: ' + fish
    print(s.center(width, ' '))

last_message_time = time.time()

while True:
    event = recieve_json_response(ws)

    try:
        if event['d']['channel_id'] == channel_id and event['d']['author']['username'] == 'PokéMeow':
            #DUP MESSAGE CHECKER AND FISH CHECKER
            message_id = event['d']['id']
            last_message_time = time.time()
            if message_id in seen_message_ids:
                message = event['d']['embeds'][0]['description']
                if "bite" in message:
                    clickFishPart1()
                    fishOffSet = 0
                    continue
                if "nibble" in message:
                    print(f"{'yo rod sucks no fish'.center(width, ' ')}")
                    
                    daSummoning(2000,2200)
                    continue
                if fishOffSet == 0:
                    fishName(message)
                    clickFishPart2()
                    fishOffSet = 1
                    counter = -1
                    continue
                checkSuccess(message)
                print(f"{'| END |'.center(width, '-')}")
                if counter >= fishNumber:
                    print('Pokemon until fishing counter!:', counter)
                    counter = 0
                    print('Counter reset!', counter)
                    daFish()
                    continue
                daSummoning(8500, 10000)
                continue

            
            seen_message_ids.add(message_id)
            rngPrint = random.randint(0,2)
            if rngPrint == 1:
                print("\033[95m" + text + "\033[0m")
            print(f"{'| START |'.center(width, '-')}")
            #print("=====EVENT=====\n", event)

            #EVENT MESSAGE DECLARATION
            event_message = event['d']['embeds']    

            #CAPTCHA
            if captchaCheck(event_message):
                print(f"{'END'.center(width, '-')}")
                continue
            
            #Print POKEMON NAME, CLICK POKEMON, PRINT POKEBALLS, BUY POKEBALLS
            poke_name(event_message)
            rarity_poke_clicker(event_message)
            pbCount = pb_reader(event_message)      
            buyBalls(pbCount)
            

            #CLEAR MESSAGE Q
            if len(seen_message_ids) > max_message_ids:
                seen_message_ids.clear()
                print("DELETED MESSAGES")
            else:
                pass
        if time.time() - last_message_time >= 15:
            print('testing point!')
        op_code = event('op')
        if op_code == 11:
            print('heartbeat received')
    except:
        pass


'''fish_message = event_message[0]['description']
            print(fish_message)
            if "bite" in fish_message:
                print("bite NIGGGA")
                pyautogui.click(-1501, 1130, duration = 0.5)
                random_milliseconds = random.randint(1000, 2000)
                time.sleep(random_milliseconds / 1000.0)
                pyautogui.click(-1437, 1090, duration = 1)

                        random_milliseconds = random.randint(8500, 11000)
        time.sleep(random_milliseconds / 1000.0)
        pyautogui.click(-1484,1200)
        pyautogui.typewrite(';p\n', interval=0)
'''

        
