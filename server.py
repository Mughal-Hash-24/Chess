import socket
from _thread import *
import sys

server = "127.0.0.1"  # Update this with your server IP address
port = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(2)
print("Waiting")

connections = []
players = ["white", "black"]  # Assign colors to players

def threaded_client(conn, player):
    conn.send(players[player].encode())  # Send player color to the client
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")

            if not data:
                print("disconnected")
                break
            else:
                print("Received: ", reply)
                # Forward the move to the other client
                for c in connections:
                    if c != conn:
                        c.sendall(data)

        except socket.error as e:
            print(e)
            break

    print("lost connection")
    conn.close()

current_player = 0
while True:
    conn, addr = s.accept()
    print("connected to: ", addr)

    connections.append(conn)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1
