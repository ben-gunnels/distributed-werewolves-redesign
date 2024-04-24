#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Virtual Werewolves
#Collaborators: Roya Ensafi, Jed Crandall
#De-bugged, tested and edited: Tim C'de Baca and John Montoya 7/2014
#server.py is the automated moderator for Virtual Werewolves

#Copyright (c) 2012 Mike Jacobi, Xu Zhang, Roya Ensafi, Jed Crandall
#This file is part of Virtual Werewolf Game.

#Virtual werewolf is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#Virtual werewolf is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Virtual werewolf.  If not, see <http://www.gnu.org/licenses/>.

import traceback
import datetime
import sys
import os
import time
import random
import signal
import threading
import asyncio
import communicationNew as c 
import socket

i = {}
with open('config', 'r') as inputVars:
    for var in inputVars:
        var = var.strip('\n').split('=')
        key = var[0]
        try:
            value = var[1]
        except IndexError:
            continue
        i[key] = value

logFile = ''

# Time parameters
timeTillStart = int(i['timeTillStart'])
wolftalktime = int(i['wolfTalkTime'])
wolfvotetime = int(i['wolfVoteTime'])
townvotetime = int(i['townVoteTime'])
towntalktime = int(i['townTalkTime'])
witchvotetime = int(i['witchVoteTime'])
deathspeechtime = int(i['deathSpeechTime'])

test = int(i['test'])
giveDeathSpeech = int(i['deathSpeech'])
numWolves = int(i['numWolves'])

# Moderator assignment global vars
wolfChoose = int(i['wolfChoose'])
moderatorAssignment = 0
moderatorAssignmentContinue = 0
moderatorAssignmentList = []

# Group people by roles
all_players = {}
wolves = {}
townspeople = {}
witches = {}

potions = [int(i['kill']), int(i['heal'])]  # [kill, heal]
round_number = 1

# Function to remove a player from the game
def removePlayer(player):
    global all_players, wolves, witches
    isTownsperson = 1

    new_all_players = {key: value for key, value in all_players.items() if key != player}
    new_wolves = {key: value for key, value in wolves.items() if key != player}
    if player in witches.keys():
        witches = {}
        isTownsperson = 0
    if isTownsperson:
        c.log('%s-townsperson killed' % player, 1, 0, 1)
    all_players = new_all_players
    wolves = new_wolves
    # Handle broadcasting death message, death speech, etc.

gameNumber = 9999
winner = 'No winner'

# Function to quit the game
def quitGame(signal, frame):
    global all_players, winner
    c.broadcast('close', all_players)
    c.log('\nGAME FORCE QUIT BY MODERATOR', 1, 1, 1)
    os.chmod(moderatorLogName, 0o744)
    for t in threading.enumerate():
        try:
            t._Thread__stop()
        except:
            pass
    sys.exit()

# Signal handler for SIGINT
signal.signal(signal.SIGINT, quitGame)

# Function to assign roles to players
def assign():
    global all_players, wolves, witches
    numPlayers = len(all_players)

    if not wolfChoose:  # Randomly assign roles
        config = ['W']
        for _ in range(numWolves):
            config.append('w')
        for _ in range(numPlayers - numWolves - 1):
            config.append('t')

        # Randomize roles
        random.shuffle(config)

        # Assign roles and inform players
        for i, player in enumerate(all_players.keys()):
            if config[i] == 'w':
                wolves[player] = all_players[player]
                role = 'wolf'
            elif config[i] == 'W':
                witches[player] = all_players[player]
                townspeople[player] = all_players[player]
                role = 'witch'
            else:
                townspeople[player] = all_players[player]
                role = 'townsperson'
            c.send('~~~~~ YOU ARE A %s ~~~~~' % role, all_players[player][1])

    else:  # Moderator chooses roles
        # Implement moderator-assigned roles logic
        pass

# Function for the standard turn of the game
def standardTurn():
    global all_players, witches, potions, towntalktime, wolftalktime
    wolfkill = 0
    witchkill = 0

    # Implement the game logic for each turn

# Function for the listener thread
def listenerThread():
    global round_number, all_players, moderatorAssignment, moderatorAssignmentContinue, moderatorAssignmentList
    while True:
        try:
            i = input().strip('\n')
        except EOFError:
            break
        if i == '':
            pass
        elif moderatorAssignment == 1:
            # Handle moderator assignment logic
            pass
        elif i == 'help':
            # Handle displaying help information
            pass
        elif i == 'status':
            # Handle displaying game status
            pass
        elif i.startswith('kill'):
            # Handle removing a player from the game
            pass
        elif i == 'skip':
            # Handle skipping the current section
            pass
        else:
            # Handle moderator messages to players
            pass
        time.sleep(.1)

publicLogName = ''
moderatorLogName = ''

# Main function to run the game
def main():
    global all_players, round_number, winner

    # Initialize sockets for communication
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = 'localhost'  # Change this to the desired host
    server_port = 12345  # Change this to the desired port
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print("Server is listening for incoming connections...")

    # Accept incoming connections from clients
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Handle each client connection in a separate thread or asynchronously
        # Example: threading.Thread(target=handle_client, args=(client_socket,)).start()

    # Implement the rest of the game logic within this loop

if __name__ == '__main__':
    main()