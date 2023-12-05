import socket
import pickle
import threading
import random
from cube import Cube
from player import Player

# Define server address and port
SERVER_ADDRESS = ("localhost", 5555)
BUFFER_SIZE = 4096

# Dictionary to store player information (position, color, score)


# List to store small squares (position)
cubes = []

position = [[0, -2, -10], [0, -2, 10], [5, -2, 30]]
players = [Player(position[0]), Player(position[1]), Player(position[2])]
# Lock to ensure thread-safe access to player information and small squares
lock = threading.Lock()


# Function to handle individual clients
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
            print(f"Received data from player {p_id}")
            print(f"Player {p_id} position: {ps[p_id].position}")
            print(cbs)

            # Update player position
            with lock:
                if player_id == 0:
                    players[1].position = ps[1].position
                    players[2].position = ps[2].position
                elif player_id == 1:
                    players[0].position = ps[0].position
                    players[2].position = ps[2].position
                elif player_id == 2:
                    players[0].position = ps[0].position
                    players[1].position = ps[1].position

            # Check for collision with small squares
            with lock:
                cubes = cbs

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
    # Remove the player from the dictionary upon disconnection
    with lock:
        del players[player_id]
    client_socket.close()


# Main server loop
def main():
    global cubes
    global players

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(3)  # Allow up to 3 connections
    print("Server is listening for connections...")

    player_id = 0

    while player_id <= 3:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

        # Increment player ID for the next client
        player_id += 1


if __name__ == "__main__":
    main()
