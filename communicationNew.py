#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Thanks to Jeff Knockel, Geoff Reedy, Matthew Hall, and Geoff Alexander for
#suggesting fixes to communication.py
#De-bugged, tested and edited: Tim C'de Baca and John Montoya 7/2014
#Virtual Werewolves
#Collaborators: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This script has generic helper functions used by the Mafia server and clients

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

import os
import time
import threading
import random
from threading import Thread
import select
import queue
import socket
import json
from datetime import datetime, timedelta

all = {}

pipeRoot = '/home/moderator/pipes/'
logName = ''
mLogName = ''
conns = {}
allowed = {}
logChat = 0
currentTime = 0

readVulnerability = 0
readVulnerability_2 = 0
imposterMode = 1
isSilent = 1
def setVars(passedReadVulnerability, passedReadVulnerability_2,passedImposterMode, publicLogName, moderatorLogName):
    #descriptions of these variables can be seen in the config file
    global readVulnerability, readVulnerability_2, imposterMode, logName, mLogName
    readVulnerability = int(passedReadVulnerability)
    readVulnerability_2 = int(passedReadVulnerability_2)
    imposterMode = int(passedImposterMode)
    logName = publicLogName
    mLogName = moderatorLogName


#returns all elements in y that are not in x
def complement(x, y):
    z = {}
    for element in y.keys():
        if element not in x.keys(): z[element] = y[element]
    return z

#resets all variables
def skip():
    global currentTime, deathspeech, deadGuy, voters, targets
    currentTime = 0
    deathspeech = 0
    deadGuy = ""
    voters = {}
    targets = {}

def sleep(duration):
    global currentTime
    currentTime = time.time()
    while time.time() < currentTime + duration:
        time.sleep(1)

def setLogChat(n):
    global logChat
    logChat = n

def obscure():
    pass
    #while 1:
        #os.system('ls '+pipeRoot+'* > /dev/null 2> /dev/null')
        #time.sleep(.1)

def allow(players):
    global allowed
    allowed = players

isHandlingConnections = 1
def handleConnections(timeTillStart, randomize):
    global isHandlingConnections, all

    f = open('names.txt', 'r').read().split('\n')[:-1]
    if randomize: random.shuffle(f)

    for conn in range(len(f)):
        if randomize:
            name = f[conn]
        else:
            name = 'player%s' % str(conn)
        t = Thread(target=connect, args=[str(conn), str(name)])
        t.setDaemon(True)
        t.start()

    time.sleep(int(timeTillStart))
    isHandlingConnections = 0
    return all

def handleConnectionUsingEpoll(timeTillStart):
    global isHandlingConnections, all
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888)) #change this port to whatever we need (hostname)
    server_socket.listen(16)  # Listen for up to 16 connections

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)

    conns = {}
    q = queue.Queue()
    startTime = datetime.now() + timedelta(seconds=timeTillStart)

    try:
        while isHandlingConnections:
            events = epoll.poll(1)  # Wait for 1 second for events
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    client_socket, addr = server_socket.accept()
                    client_socket.setblocking(0)
                    epoll.register(client_socket.fileno(), select.EPOLLIN)
                    conns[client_socket.fileno()] = client_socket
                    q.put(client_socket.fileno())
                else:
                    client_socket = conns[fileno]
                    try:
                        data = client_socket.recv(1024).decode()
                        if data == 'connect':
                            q.put(fileno)
                    except:
                        pass

            while not q.empty():
                fileno = q.get()
                client_socket = conns[fileno]
                if isHandlingConnections:
                    log('Player connected', 1, 0, 1)
                    client_socket.send(b'Hello. You are connected. Please wait for the game to start.')
                elif not isHandlingConnections:
                    client_socket.send(b'Game already started. Please wait for next game.')
                    client_socket.close()
                    epoll.unregister(fileno)
                    del conns[fileno]

            if datetime.now() >= startTime:
                isHandlingConnections = 0
    finally:
        for fileno, client_socket in conns.items():
            epoll.unregister(fileno)
            client_socket.close()
        epoll.unregister(server_socket.fileno())
        server_socket.close()
        epoll.close()

    return conns

def connect(num, name):
    global isHandlingConnections

    server_address = ('localhost', 8888) #change localhost and port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(1) 

    connected = False
    try:
        client_socket.connect(server_address)
        connected = True
    except socket.error as e:
        print(f"Error: {e}")

    if connected:
        try:
            client_socket.send(b'connect')
            response = client_socket.recv(1024).decode()
            print(response)
        except socket.error as e:
            print(f"Error: {e}")

    client_socket.close()

def broadcast(msg, players):
    global logChat
    log(msg, 1, logChat, 1)

    for player in players.keys():
        try:
            send(msg, players[player][0])
        except Exception as e:
            print("Broadcast error:", e)

def send(msg, sock):
    try:
        sock.sendall(msg.encode())
    except Exception as e:
        print("Send error:", e)

def recv(sock):
    global readVulnerability, imposterMode
    try:
        data = sock.recv(1024)  # Receive data from the socket
        if not data:
            return None
        
        # Decode the received data (assuming it's in JSON format)
        message = json.loads(data.decode())

        sender = message.get('sender', '')
        message_content = message.get('message', '')

        out = sock.getsockname()[1]  # Get the local port of the socket

        if readVulnerability == 0 or sender == out or imposterMode == 1:
            return [sender, message_content]

    except Exception as p:
        log('receive error:%s' % p, 0, 0, 0)
        pass

    return None

import json

def log(msg, printBool, publicLogBool, moderatorLogBool, public_sock=None, moderator_sock=None):
    global logName, mLogName

    if printBool:
        print(msg)

    msg = '(%s) - %s\n' % (str(int(time.time())), msg)
    if publicLogBool:
        send_message(public_sock, msg)
    if moderatorLogBool:
        send_message(moderator_sock, msg)

def clear(socks):
    for sock in socks:
        for i in range(10):
            t = Thread(target=recv, args=[sock])
            t.setDaemon(True)
            t.start()

def send_message(sock, message):
    try:
        if sock:
            sock.sendall(json.dumps({'message': message}).encode())
    except Exception as e:
        print(f"Error sending message: {e}")


deathspeech = 0
deadGuy = ""

def create_epoll(addresses):
    sock_map = {}
    epoll = select.epoll()
    for addr in addresses:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(addr)
        server_socket.listen(5)
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        sock_map[server_socket.fileno()] = server_socket
    return epoll, sock_map

def recv_chat(client_socket):  # Like recv but refactored to work with signalHandler
    output = client_socket.recv(1024).decode()
    if output != '':
        output = output.split('\n')
        for i in range(len(output)):
            if len(output[i]):
                if len(output[i]):
                    return output[i].split(':')

def signal_handler():
    addresses = [("localhost", 8000 + i) for i in range(16)]
    q = queue.Queue()
    epoll, sock_map = create_epoll(addresses)
    while 1:
        events = epoll.poll()  # Get alerted for new I/O
        for fileno, event in events:
            if fileno in sock_map:
                client_socket, _ = sock_map[fileno].accept()
                player = get_player_from_socket(client_socket) 
                q.put([player, msg])
        while not q.empty():
            client_socket, msg = q.get()
            if msg == None:
                continue
            #if someone's giving a death speech
            if deathspeech and player == deadGuy:
                broadcast('%s-%s'%(player, msg[2]), mod_players(player, all))

            #if we're voting
            elif votetime and player in voters.keys():
                vote(player, msg[2])

            #if it's group chat
            elif player in allowed:
                broadcast('%s-%s'%(player, msg[2]), mod_players(player, allowed))

            #otherwise prevent spam
            else:
                time.sleep(1)

def get_player_from_socket(client_socket):
    player = None
    address = client_socket.getpeername()

    player_number = address[1] - 8000 
    player = f"player{player_number}"
    return player

def multi_recv(player, players):
    global allowed, voters, targets, deathspeech, deadGuy, all

    while 1:
        client_socket = all[player][0].accept()[0]
        msg = recv_chat(client_socket)
        if msg == None:
            continue

        #if someone's giving a death speech
        if deathspeech and player == deadGuy:
            broadcast('%s-%s'%(player, msg[2]), mod_players(player, all))

        #if we're voting
        elif votetime and player in voters.keys():
            vote(player, msg[2])

        #if it's group chat
        elif player in allowed:
            broadcast('%s-%s'%(player, msg[2]), mod_players(player, allowed))

        #otherwise prevent spam
        else:
            time.sleep(1)

def group_chat(players):
    signal_handler()

def mod_players(player, players):
    newPlayers = {}
    for p in players.keys():
        if p != player:
            newPlayers[p] = players[p]
    return newPlayers

#voteAllowDict is a dictionary of booleans that forces only one group to vote at a time.
votetime = 0
voteAllowDict = {'w':0, 'W':0, 't':0}
votes = {}
votesReceived = 0
voters = {}
targets = []
character = ""

# Global dictionary to determine if user has voted
voter_targets = {}

def vote(voter, target):
    global votes, votesReceived, voters, character, isSilent, voter_targets

    # Code Updated on 7/20 by Tim
    if voter_targets.get(voter, None) == None:  # Added line

        if target in targets:
            try:
                votes[target] += 1  #changed from += 1 to just 1
            except:
                votes[target] = 1
            #message[0] is sent to who[0]; message[1] sent to who[1]; etc.
            messages = []
            who = []

            log(voter + " voted for " + target, 1, 0, 1)

            if character == "witch":
                messages.append("Witch voted")
                who.append(all)
            elif character == "wolf":
                if isSilent:
                    messages.append('%s voted.'%voter)
                else:
                    messages.append('%s voted for %s'%(voter, target))
                who.append(voters)

                messages.append("Wolf vote received.")
                comp = complement(voters, all)
                who.append(comp)
            else:#townsperson vote
                if isSilent:
                    messages.append('%s voted.'%voter)
                else:
                    messages.append('%s voted for %s'%(voter, target))
                who.append(all)

            for i in range(len(messages)):
                broadcast(messages[i], who[i])

            votesReceived += 1
            voter_targets[voter] = target  

            if votesReceived == len(voters):
                skip()

        else:
            send('invalid vote: %s'%target, voters[voter][1])

    # Added by Tim    
    else:
        send('You already voted: %s'%target, voters[voter][1])

def spawn_death_speech(player, endtime):
    global deathspeech, deadGuy
    deathspeech = 1
    deadGuy = player

    sleep(endtime)

    deathspeech = 0
    deadGuy = ""
