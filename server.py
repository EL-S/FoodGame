import socket
from _thread import *
import pickle
import sys
from game import Game
from config_loader import server_settings

def threaded_client(conn, player_id, game_id):
    global players

    # Send the player_id to the newly connected client
    conn.send(str.encode(str(player_id)))
    # self.client.send(str.encode(data))
    try:

        # Establish the players name
        # TODO: Establish the players screen resolution too?

        player_data = conn.recv(4096).decode()
        # TODO: Make the protocol use JSON or something
        key,data = player_data.split("=")
        if (key == "name"):
            player_name = data
        print(f"Player {player_id}: {player_name}")

        if game_id in games:
            game = games[game_id]

            # store the player name
            game.create_player(player_id, player_name)

            # think of a response
            if game.p1_name_went and player_id != 0:
                conn.send(pickle.dumps("ready"))
            else:
                conn.send(pickle.dumps("wait"))

        # Play the game

        max_retries = 10 # If a connection fails, retry 10 times
        retries = 0

        while True:
            try:
                data = conn.recv(4096).decode()

                if game_id in games:
                    game = games[game_id]

                    if not data: # No data was received from the client
                        if retries >= max_retries:
                            print("Too many retries, closing connection")
                            break
                        else:
                            retries += 1
                            continue
                        break
                    else: # Data was received from the client
                        if data == "get":
                            # Send the game to the client
                            conn.sendall(pickle.dumps(game))
                        elif data.split()[0] == "move":
                            # Get the players move and try to apply it
                            try:
                                game.play(player_id, int(data.split()[1]))
                            except Exception as e:
                                print(e)
                            finally:
                                conn.send(pickle.dumps("ack"))
                        elif data == "reset":
                            # Reset the game because a player requested it
                            game.reset()
                            conn.send(pickle.dumps("ack"))
                        else:
                            conn.send(pickle.dumps("invalid"))
                else:
                    print("Game doesn't exist anymore?")
                    break
            except Exception as e:
                print("General error",e)
                break
    except:
        print("No player name sent!")

    print("Lost connection")
    try:
        game.destroy_player(player_id)
        if int(server_settings['max_players']) != 0: # Only close game if the game is not MMO style
            if game.player_count < 2:
                del games[game_id]
                print("Closing Game", game_id)
            else:
                print("Keeping game open")
    except Exception as e:
        print(e)
    players -= 1
    conn.close()

def setup():
    global server, port, s, connected, games, players, max_players, game_mode
    server = server_settings['server_ip']
    port = int(server_settings['server_port'])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.settimeout(1.0)

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
    players = 0
    max_players = int(server_settings['max_players'])
    game_mode = int(server_settings['game_mode'])

if __name__ == "__main__":
    setup()

    # TODO: Score board
    # TODO: Handle player disconnects on servers with more than 2 online players
    # TODO: Maybe check for currently running servers with free spots, and join new players there, or maybe just move everyone over
    # TODO: Maybe a serverlist? or a gamelist

    player_id = 0

    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit()
        except socket.error as e:
            continue
        print("Connected to:", addr)
        if max_players == 0: # Need to be on one server
            players += 1
            game_id = 0
            #player_id = players-1 # The player id for this specific game
            print(game_mode, game_id, player_id, players, max_players)
            if player_id == 0 or len(games) == 0: # If the game somehow breaks, or this is the first player, create the game
                games[game_id] = Game(game_id,max_players,game_mode) # Maybe add max_players to the game constructor
                games[game_id].ready = True # The game is instantly ready on MMO mode
                print("Creating a new game...")
            else:
                print("Joining a game...")
        elif players < max_players: # TODO: Currently kinda broken, need to handle player_id seperately?
            players += 1
            game_id = (players - 1)//max_players
            #player_id = players % max_players # The player id for this specific game
            print(game_mode, game_id, player_id, players, max_players)
            if player_id == 0:
                games[game_id] = Game(game_id,max_players,game_mode)
                print("Creating a new game...")
            else:
                games[game_id].ready = True
                print("Joining a game...")
        else:
            print("Server is full!")
            continue
        start_new_thread(threaded_client, (conn, player_id, game_id))
        player_id += 1
