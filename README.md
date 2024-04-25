Copyright (c)  2012 Mike Jacobi, Xu Zhang, Roya Ensafi, Jed Crandall
Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3
or any later version published by the Free Software Foundation;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
A copy of the license is included in the section entitled "GNU
Free Documentation License".

2024 Benjamin Gunnels, Vignesh R S, Vedant Yatin Pimpley

## Update patch using Asynchronous I/O

Feel free to reuse or redistribute this code in any way. 

Clone this github repo https://github.com/miltiades-the-general/distributed-werewolves-redesign on a linux machine or virtual machine if it hasn't already been downloaded.

To play, run ./install.sh and wait for the game to download. The user will be prompted to create a password for the moderator. Ensure that this password is saved. 

The user may have to change the permissions for install.sh, 
```$chmod 777 install.sh``` and
```$chmod 777 mkusr.sh```

### Using Tailscale
If you would like to use tailscale to serve the game follow the brief tutorial.
On Linux, for each virtual machine run:
```curl -fsSL https://tailscale.com/install.sh | sh```

The user will be prompted to log in using an email. Next enter:
```sudo tailscale up --ssh```

The user dashboard can verify that SSH has been enabled.
![Tailscale](/static/Tailscale.png)


### Gameplay
In order for the game to work, at least 3 parties must SSH into the host machine. For best use on a small group set wolfChoose to 1 in the configuration file of the game. This allows the moderator to manually select a werewolf and a witch so that the game can be run for demo purposes. 

Create an SSH server on the host's machine using OpenSSH, Tailscale, etc. Then, one player must SSH as the moderator using ```$ssh moderator@ip-address```, 
and two players must SSH using ```$ssh playerX@ip-address```. Valid players range from 1 to 15.


Once all players, and one moderator, have SSH'd into the host machine, the moderator runs the game via: ```$python3 server.py```
and subsequently the players run: ```$python3 client.py``` on their respective machines.


## How is our approach different?
As opposed to the original version of Werewolves, this version does not use multithreading in the group chat thread, or connection thread, and instead relies on a central signalHandler thread to monitor and handle I/O throughout the game. This reduces the threadspace of the game considerably from n players to just one thread running on the server. Additionally the game has been updated to be compatible with python version 3.0+. 

![Before](/static/BeforeUseCaseDiagram.png)

In our version, we removed the use of multithreading for handling connections and the group chat.
![After](/static/AfterUseCaseDiagram.png)

The groupchat runs as a single thread using a while loop to monitor I/O using epoll. 
Epoll is being used in level triggered mode allowing the handler to update the queue when new I/O events are available to be handled. 

```
while 1:
    events = epoll.poll(1) # Get alerted for new I/O, set wait to 1sec
```   

The client operates the same way in our version of the game. Namely, each client runs a thread to monitor I/O on its incoming pipe and writes to its outgoing pipe when there is input to the command line. This could be refactored to utilize asynchronous programming and this may be a worthwhile endeavor in future versions. 

## New Functions Added:

signalHandler() -> replaced multiRecv()

create_epoll()

close_epoll()

recvChat() -> replaced recv() for the groupchat

connectUsingEpoll() -> replaced handleConnections() and connect()

recvConnection() -> replaced connect()
