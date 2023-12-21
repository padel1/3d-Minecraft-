import socket
import pickle
import threading
import random
from cube import Cube
from player import Player
import numpy as np
import random
# Define server address and port
SERVER_ADDRESS = ("192.168.93.46", 5555)
BUFFER_SIZE = 4096 * 16

player_id = 0
cubes = []


players = []
lock = threading.Lock()


def handle_client(client_socket, player_id):
    global players, cubes
    players.append(
        Player(([random.randint(0, 10), -5, random.randint(0, 10)]), 90, 90))
    client_socket.sendall(
        pickle.dumps(
            {"player_id": player_id, "players": players, "cubes": cubes})
    )

    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break

            # Unpickle the received data
            data = pickle.loads(data)

            p_id = data["player_id"]
            ps = data["players"]
            cbs = data["cubes"]

            # Update player position
            with lock:
                players[p_id].position = ps[p_id].position
                players[p_id].rotation_h = ps[p_id].rotation_h
                players[p_id].rotation_v = ps[p_id].rotation_v

            # Check for collision with small squares
            with lock:
                for cube in cbs:
                    if not any(np.array_equal(cube.center, c.center) for c in cubes):
                        cubes.append(cube)

                for c in cubes:
                    if not any(np.array_equal(cube.center, c.center) for cube in cbs):
                        cubes.remove(c)
             

            # Send updated player information and small squares to all clients
            with lock:
                client_socket.sendall(
                    pickle.dumps(
                        {"player_id": player_id, "players": players, "cubes": cubes}
                    )
                )

        except Exception as e:
            print(f"Error handling client {player_id}: {e}")
            break

    print(f"Player {player_id} disconnected.")
    # Remove the player from the list upon disconnection
    with lock:
        del players[player_id]

    client_socket.close()

# Main server loop


def main():

    global cubes
    global players
    global player_id

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen()  # Allow up to 3 connections
    print("Server is listening for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with   {client_address}")
        print(f"Player {player_id} connected.")

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(
            client_socket, player_id)).start()

        # Increment player ID for the next client
        player_id += 1


if __name__ == "__main__":
    main()
