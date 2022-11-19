import os
import socket
import selectors

# pyinstaller socket\server.py --onefile -n ServerSnakeOnline

# HOST = "localhost"
# PORT = 9090
with open(os.getcwd() + "\settings", "r") as f:
    client_host = f.readline().replace("\n", "")
    HOST = f.readline().replace("\n", "")
    PORT = int(f.readline())
    wsize = tuple(map(int, f.readline().split(",")))
    flags = f.readline()
MAX_CONNECTIONS = 8
SIZE_DATA = 1024 * 32
STR_LEN = SIZE_DATA // 8

names = ["cyan", "orange", "amber", "yellow", "lime", "green", "emerald", "teal"]
colors = ["#06B6D4", "#F97316", "#F59E0B", "#FACC15", "#84CC16", "#22C55E", "#10B981", "#14B8A6"]
busy_names = {}
name_color = {name: color for name, color in zip(names, colors)}
players = {}
# apple = "-1,-1"
apples = set()
main_apple = set()

sel = selectors.DefaultSelector()


def get_free_name():
    # busy_name = {player[0] for player in players.values()}
    _busy_names = set(busy_names.values())
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
    print(list(players.values()))
    return f"{get_data_apples()};" + "|".join(
        [f"{name},{color},{poses}" for name, color, poses in players.values()]) + ";"


def get_data_apples():
    return "|".join([xy for xy in apples])


def read(conn, mask):
    global apples, main_apple
    try:
        data = conn.recv(SIZE_DATA)
    except ConnectionResetError or ConnectionAbortedError:
        data = b""
    if data:

        st = data.decode()
        if st == "start":
            # name, color, 'x/y'
            player = (get_free_name(), name_color[get_free_name()], str(len(players) * 2) + "/" + str(0))
            out = ("connected;" + ";".join(player) + ";" + get_data_map()).encode()
            print("Player start. out:", out)
            conn.send(out)
            busy_names[conn] = player[0]
            players[conn] = player
        else:
            print("Player", main_apple, st)
            name, color, alive, apple_add, apple_eated, poses = st.split(";")[:6]
            if apple_eated != "0":
                apples.remove(apple_eated)
            if apple_add != "0":
                if "|" in apple_add:
                    for apple in apple_add.split("|"):
                        main_apple.add(apple)
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
            print(out)
            # for conn, player in players.items():
            #     # if player[0] != name:
            #     conn.send(out)

    else:
        print("Close conn", conn)

        if conn in players:
            players.pop(conn)
        if conn in busy_names:
            busy_names.pop(conn)
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
