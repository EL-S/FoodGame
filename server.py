import socket
from _thread import *
import pickle
from game import Game
from config_loader import server_settings

def threaded_client(conn, p, game_id):
    global id_count
    conn.send(str.encode(str(p)))
    # self.client.send(str.encode(data))
    try:

        # Establish the players name

        player_data = conn.recv(4096).decode()
        key,data = player_data.split("=")
        if (key == "name"):
            player_name = data
        print(f"Player {p}: {player_name}")

        if game_id in games:
            game = games[game_id]

            # store the player name
            game.create_player(p, player_name)

            # think of a response
            if game.p1_name_went and p != 0:
                conn.send(pickle.dumps("ready"))
            else:
                conn.send(pickle.dumps("wait"))

        # Play the game

        while True:
            try:
                data = conn.recv(4096).decode()

                if game_id in games:
                    game = games[game_id]

                    if not data:
                        break
                    else:
                        if data == "reset":
                            game.reset()
                        elif data.split()[0] == "move":
                            try:
                                game.play(p, int(data.split()[1]))
                            except Exception as e:
                                print(e)

                        conn.sendall(pickle.dumps(game))
                else:
                    break
            except:
                break
    except:
        print("No player name sent!")

    print("Lost connection")
    try:
        del games[game_id]
        print("Closing Game", game_id)
    except:
        pass
    id_count -= 1
    conn.close()

def setup():
    global server, port, s, connected, games, id_count
    server = server_settings['server_ip']
    port = int(server_settings['server_port'])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_ip = socket.gethostbyname(server)
        print(server, server_ip)
        s.bind((server_ip, port))
    except socket.error as e:
        print(e)

    s.listen(2)
    print("Waiting for a connection, Server Started")

    connected = set()
    games = {}
    id_count = 0

if __name__ == "__main__":
    setup()

    while True:
        conn, addr = s.accept()
        print("Connected to:", addr)

        id_count += 1
        p = 0
        game_id = (id_count - 1)//2
        if id_count % 2 == 1:
            games[game_id] = Game(game_id)
            print("Creating a new game...")
        else:
            games[game_id].ready = True
            p = 1
            print("Joining a game...")


        start_new_thread(threaded_client, (conn, p, game_id))
