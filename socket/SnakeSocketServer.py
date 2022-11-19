colors = ["#84CC16", "#10B981", "#0EA5E9", "#3B82F6", "#6366F1", "#8B5CF6", "#D946EF"]
max_players = len(colors)
map_size = (24, 16)
apple = ()
players = []

# https://docs.python.org/3/library/selectors.html
import selectors
import socket

sel = selectors.DefaultSelector()


def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def get_map_data():
    st = f"{apple[0]},{apple[1]};"
    for player in players:
        st += f"{player[0]}*" + "|".join([f"{pos[0]},{pos[1]}|" for pos in player[1]])+"!"
    st += ";"
    return st


def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        st = repr(data)
        print('echoing', st, 'to', conn)
        if st == "start":
            if len(players) < max_players:
                out = f"{colors[len(players)]};"+get_map_data()
                conn.send(out)  # Hope it won't block
            else:
                conn.send("players limit")
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind(('localhost', 9090))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
