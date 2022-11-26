import os
from src.config import ServerCnf
import socket
import selectors
import sys

CONNECTION_KEY = sys.argv[1] if len(sys.argv) >= 2 else "0000"
# pyinstaller Server.py --onefile -n SnakeServer

# HOST = "localhost"
# PORT = 9090
HOST = ServerCnf.HOST
PORT = ServerCnf.PORT
DEBUG = ServerCnf.DEBUG

MAX_CONNECTIONS = 8
SIZE_DATA = 1024 * 32
STR_LEN = SIZE_DATA // 8

names = ["cyan", "orange", "amber", "yellow", "lime", "green", "emerald", "teal"]
colors = ["#06B6D4", "#F97316", "#F59E0B", "#FACC15", "#84CC16", "#22C55E", "#10B981", "#14B8A6"]
connections_names = {}
name_color = {name: color for name, color in zip(names, colors)}
players = {}
map_size = "0"
# apple = "-1,-1"
apples = set()
main_apple = set()
stones = set()
portals = set()

sel = selectors.DefaultSelector()


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def get_free_name():
    # busy_name = {player[0] for player in players.values()}
    _busy_names = set(connections_names.values())
    for name in names:
        if name not in _busy_names:
            return name
    return "noname"


def accept(sock, mask):
    conn, addr = sock.accept()
    print("accepted", conn, "addr", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def get_data_map():
    debug_print(list(players.values()))
    return f"{get_data_apples()};" + "|".join(
        [f"{name},{color},{poses}" for name, color, poses in players.values()]) + ";"


def get_data_apples():
    return "|".join([xy for xy in apples])


def get_data_static_map():
    return map_size + ';' + "|".join([xy for xy in stones]) + ";"+"|".join([xy for xy in portals])


def read(conn, mask):
    global apples, main_apple, map_size, stones, portals
    try:
        data = conn.recv(SIZE_DATA)
    except ConnectionResetError or ConnectionAbortedError:
        data = b""
    if data:

        st = data.decode()
        code = st.split(";")[0]
        if code == "start":
            print("PLayer start dataget: " + st)
            app_key = st.split(";")[1]
            if app_key != CONNECTION_KEY:
                conn.send(b"error403;Incorrect application key;")
                close_connection_player(conn)
                return
            # name, color, 'x/y'
            player = (get_free_name(), name_color[get_free_name()], str(len(players) * 2) + "/" + str(0))
            out = ("connected;" + ";".join(player) + ";" + get_data_static_map() + ";" + get_data_map()).encode()
            debug_print("Player start. out:", out)
            conn.send(out)
            connections_names[conn] = player[0]
            players[conn] = player
        elif code == "map":
            ar = st.split(";")
            map_size, _stones, _portals = ar[1], ar[2], ar[3]
            stones = set(_stones.split("|"))
            portals = set(_portals.split("|"))
        elif code == "update":
            debug_print("Player", main_apple, st.split(";"))
            code, name, color, alive, apple_add, apple_eated, poses = st.split(";")[:7]
            if connections_names.get(conn, None) != name:
                print("error403;Incorrect name player;", players)
                conn.send(b"error403;Incorrect name player;")
                close_connection_player(conn)
                return
            if apple_eated != "0":
                apples.remove(apple_eated)
            if apple_add != "0":
                if "|" in apple_add:
                    for apple in apple_add.split("|"):
                        main_apple.add(apple)
                        apples.add(apple)
                elif "!" in apple_add:
                    for apple in apple_add.split("!"):
                        apples.add(apple)
                elif apple_eated in main_apple or main_apple == set():
                    if apple_eated in main_apple:
                        main_apple.remove(apple_eated)
                    main_apple.add(apple_add)
                    apples.add(apple_add)
                elif apple_eated == "0":
                    apples.add(apple_add)
            players[conn] = (name, color, poses)
            if not int(alive):
                players.pop(conn)
            out = ("update;" + get_data_map() + "end").encode()
            conn.send(out)
            debug_print(out)
            # for conn, player in players.items():
            #     # if player[0] != name:
            #     conn.send(out)

    else:
        close_connection_player(conn)


def close_connection_player(conn):
    print("Close conn", conn)
    if conn in players:
        players.pop(conn)
    if conn in connections_names:
        connections_names.pop(conn)
    sel.unregister(conn)
    conn.close()


sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(MAX_CONNECTIONS)
sock.setblocking(False)
print("Start listening")
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
