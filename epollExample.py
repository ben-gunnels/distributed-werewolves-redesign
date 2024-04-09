import select
import os
import sys

pipe_path = "pipes/1tosD/1tos"

pipe1 = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)
epoll = select.epoll()

epoll.register(pipe1, select.EPOLLIN)

try:
    while True:
        events = epoll.poll()
        for event in events:
            if event[0] == pipe1:
                data = os.read(pipe_path, 1024)

                print(data.decode())
                sys.exit()
finally:
    # Close the pipe and epoll object
    epoll.unregister(pipe1)
    epoll.close()