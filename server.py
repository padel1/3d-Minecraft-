import socket
import pickle
import threading
import random
from cube import Cube
from player import Player
import numpy as np
# Define server address and port
SERVER_ADDRESS = ("localhost", 5555)
BUFFER_SIZE = 4096 * 4

# Dictionary to store player information (position, color, score)


# List to store small squares (position)
cubes = []

position = [[0, -2, -10], [0, -2, 10], [5, -2, 30]]
players = [Player(position[0]), Player(position[1]), Player(position[2])]
# Lock to ensure thread-safe access to player information and small squares
lock = threading.Lock()


# Function to handle individual clients
# def handle_client(client_socket, player_id):
#     global players, cubes

#     # send cubes and players to client
   
#     client_socket.sendall(
#         pickle.dumps({"player_id": player_id, "players": players, "cubes": cubes})
#     )

#     while True:
#         try:
#             # Receive player input
#             data = client_socket.recv(BUFFER_SIZE)
            
#             if not data:
#                 break
#             # Unpickle the received data
#             data = pickle.loads(data)
#             print("----------------------------------")
#             print(cubes)
#             print(data["player_id"])
#             p_id = data["player_id"]
#             ps = data["players"]
#             cbs = data["cubes"]
#             # print(f"Received data from player {p_id}")
#             # print(f"Player {p_id} position: {ps[p_id].position}")
#             # print(cbs)

#             # Update player position
#             with lock:
#                 players[0].position = ps[0].position
#                 players[1].position = ps[1].position
#                 players[2].position = ps[2].position

#             # Check for collision with small squares
#             with lock:
#                 for cube in cbs:
#                     for c in cubes:
#                         if not np.array_equal(cube.center,c.center):

#                             cubes.append(cube)

#             # Send updated player information and small squares to all clients
#             with lock:
#                 client_socket.sendall(
#                     pickle.dumps(
#                         {"player_id": player_id, "players": players, "cubes": cubes}
#                     )
#                 )

#         except Exception as e:
#             print(f"Error handling client {player_id}: {e}")
#             break

#     print(f"Player {player_id} disconnected.")
#     # Remove the player from the dictionary upon disconnection
#     with lock:
#         del players[player_id]
#     client_socket.close()

def handle_client(client_socket, player_id):
    global players, cubes

    # send cubes and players to client
    client_socket.sendall(
        pickle.dumps({"player_id": player_id, "players": players, "cubes": cubes})
    )

    while True:
        try:
            # Receive player input
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

            # Check for collision with small squares
            with lock:
                for cube in cbs:
                    if not any(np.array_equal(cube.center, c.center) for c in cubes):
                        cubes.append(cube)

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

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(10)  # Allow up to 3 connections
    print("Server is listening for connections...")

    player_id = 0

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with   {client_address}")
        print(f"Player {player_id} connected.")

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

        # Increment player ID for the next client
        player_id += 1


if __name__ == "__main__":
    main()
