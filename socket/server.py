import socket
import selectors

HOST, PORT = "localhost", 9090
MAX_CONNECTIONS = 8
SIZE_DATA = 2048
STR_LEN = SIZE_DATA // 8

names = ["cyan", "orange", "amber", "yellow", "lime", "green", "emerald", "teal"]
colors = ["#06B6D4", "#F97316", "#F59E0B", "#FACC15", "#84CC16", "#22C55E", "#10B981", "#14B8A6"]
name_color = {name: color for name, color in zip(names, colors)}
players = {}
apple = "-1,-1"
# apples = []

sel = selectors.DefaultSelector()


def get_free_name():
    busy_name = {player[0] for player in players.values()}
    for name in names:
        if name not in busy_name:
            return name
    return "noname"


def accept(sock, mask):
    conn, addr = sock.accept()
    print("accepted", conn, "addr", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def get_data_players():
    print(list(players.values()))
    return f"{apple};" + "|".join([f"{name},{color},{poses}" for name, color, poses in players.values()]) + ";"


def get_data_apples():
    return "|"


def read(conn, mask):
    global apple
    try:
        data = conn.recv(SIZE_DATA)
    except ConnectionResetError:
        data = b""
    if data:
        print("READ conn", conn, "data", data)
        st = data.decode()
        if st == "start":
            # name, color, x, y, conn
            player = (get_free_name(), name_color[get_free_name()], str(len(players) * 2) + "/" + str(0))
            out = ("connected;" + ";".join(player) + ";" + get_data_players()).encode()
            print("START", out)
            conn.send(out)
            players[conn] = player
        else:
            print(st)
            name, color, alive, _apple, apple_eated, poses = st.split(";")[:6]
            if int(apple_eated):
                apple = _apple
            players[conn] = (name, color, poses)
            if not int(alive):
                players.pop(conn)
            out = ("update;" + get_data_players()).encode()
            print("Player", st)
            conn.send(out)
            print(out)
            # for conn, player in players.items():
            #     # if player[0] != name:
            #     conn.send(out)

    else:
        print("Close conn", conn)
        players.pop(conn)
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
