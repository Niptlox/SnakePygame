import os

import pygame as pg
import random
import socket

# HOST = "192.168.1.11"
# PORT = 9090
with open(os.getcwd() + "\settings", "r") as f:
    HOST = f.readline().replace("\n", "")
    server_host = f.readline().replace("\n", "")
    PORT = int(f.readline())
    wsize = tuple(map(int, f.readline().split(",")))
    flags = f.readline()
# HOST = "localhost"
SIZE_DATA = 1024 * 32


# SnakeSocketClient.py
# pyinstaller socket\SnakeSocketClient.py --noconsole --onefile -n SnakeOnline

def randxy():
    return random.randint(0, MSIZE[0] - 1), random.randint(0, MSIZE[1] - 1)


def send_my_data():
    global apple_eated, apple_add
    poses = "*".join([f"{x}/{y}" for x, y in snake])
    out = f"{name};{color};{int(alive)};{apple_add};{apple_eated};{poses};".encode()
    # print("SEND", out)
    sock.send(out)
    apple_eated = "0"
    apple_add = "0"


INFINITY_MAP = True
TSIDE = 30
WSIZE = wsize
MSIZE = WSIZE[0] // TSIDE, WSIZE[1] // TSIDE
print(MSIZE)
direction = 0
set_direction = direction
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
start_pos = MSIZE[0] // 2, MSIZE[1] // 2
snake = [start_pos]
alive = True
immortal = "i" in flags
start_length = 20 if "l" in flags else 1
# apple = randxy()

main_apples_count = 5
apple_eated = "0"
apple_add = "0"
last_step_tick = 0
start_tick = 50 if "s" in flags else 250
step_tick = start_tick
pg.init()
screen = pg.display.set_mode(WSIZE)
clock = pg.time.Clock()
fps = 4

font_end = pg.font.SysFont("Arial", 50)
font_2 = pg.font.SysFont("Arial", 20)
font_score = pg.font.SysFont("Arial", 25)
font_board = pg.font.SysFont("Arial", 18)
font_myboard = pg.font.SysFont("Arial", 18, bold=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(b"start")
    data = sock.recv(SIZE_DATA)
    data_lst = data.decode().split(";")[:-1]
    print("init", data_lst)
    _, name, color, xy, _apples, _players = data_lst
    if _apples:
        apples = _apples.split("|")
    else:
        apple_add = "|".join([",".join(map(str, randxy())) for i in range(main_apples_count)])
        apples = []
    start_pos = tuple(map(int, xy.split("/")))
    snake = [start_pos] * start_length
    pg.display.set_caption("Client: " + name + f" ({color})")
    print("sanke", snake)
    send_my_data()

    data = sock.recv(SIZE_DATA).decode()
    players = []
    running = True
    while running:
        screen.fill("black")
        # clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if alive:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT and direction != 2:
                        set_direction = 0
                    if event.key == pg.K_DOWN and direction != 3:
                        set_direction = 1
                    if event.key == pg.K_LEFT and direction != 0:
                        set_direction = 2
                    if event.key == pg.K_UP and direction != 1:
                        set_direction = 3
            else:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        direction = 0
                        snake = [(MSIZE[0] // 2, MSIZE[1] // 2)]
                        # apple = randxy()
                        alive = True
                        fps = 4
                        step_tick = start_tick
        print(apples)
        for apple in apples:
            ax, ay = map(int, apple.split(","))
            pg.draw.rect(screen, "red", (ax * TSIDE, ay * TSIDE, TSIDE, TSIDE))
        [pg.draw.rect(screen, color, (x * TSIDE, y * TSIDE, TSIDE - 1, TSIDE - 1)) for x, y in snake]
        # print("players", players)
        all_poses = []

        scores = []
        for player in players:
            player_poses = [tuple(map(int, p.split("/"))) for p in player[2].split("*")]
            scores.append((len(player_poses), player[0], player[1]))
            if player[0] == name:
                continue
            all_poses += player_poses
            [pg.draw.rect(screen, player[1], (int(x) * TSIDE, int(y) * TSIDE, TSIDE - 1, TSIDE - 1)) for x, y in
             player_poses]
        tx, ty = WSIZE[0] - 150, 5
        screen.blit(font_2.render(f"Dashboard", True, "white"), (tx, ty))
        ty += 22
        for pscore, pname, pcolor in sorted(scores, reverse=True):
            tfont = font_board
            if pname == name:
                tfont = font_myboard
            screen.blit(tfont.render(f"{pname}: {pscore}", True, pcolor), (tx, ty))
            ty += 20
        if alive:
            # print(pg.time.get_ticks())
            if last_step_tick + step_tick < pg.time.get_ticks():
                direction = set_direction
                last_step_tick = pg.time.get_ticks()
                new_pos = snake[0][0] + directions[direction][0], snake[0][1] + directions[direction][1]
                if pg.key.get_pressed()[pg.K_r]:
                    new_pos = randxy()
                if INFINITY_MAP:
                    if new_pos[0] >= MSIZE[0]: new_pos = (0, new_pos[1])
                    if new_pos[1] >= MSIZE[1]: new_pos = (new_pos[0], 0)
                    if new_pos[0] < 0: new_pos = (MSIZE[0] - 1, new_pos[1])
                    if new_pos[1] < 0: new_pos = (new_pos[0], MSIZE[1] - 1)

                if new_pos in snake or new_pos in all_poses or \
                        not (0 <= new_pos[0] < MSIZE[0] and 0 <= new_pos[1] < MSIZE[1]):
                    if not immortal:
                        alive = False
                        apple_add = ",".join(map(str, new_pos))
                else:
                    st_pos = ",".join(map(str, new_pos))
                    print("apples", apples)
                    if st_pos in apples:
                        snake.append((0, 0))
                        apple_eated = st_pos
                        apple_add = ",".join(map(str, randxy()))
                        fps += 1
                        step_tick = max(50, step_tick - 10)
                    snake.insert(0, new_pos)
                    snake.pop(-1)
        else:
            text = font_end.render("GAME OVER", True, "white")
            screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 - 40))
            text = font_2.render("Press SPACE for restart", True, "white")
            screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 + 20))
        text = font_score.render("Score: " + str(len(snake)), True, "yellow")
        screen.blit(text, (5, 5))
        pg.display.flip()

        send_my_data()
        data = sock.recv(SIZE_DATA).decode()
        if not data:
            print("ERROR NOT DATA")
            continue
        i = data.find("update")
        i2 = data.find("end")
        ar_data = data[i:i2].split(";")
        print("update:", ar_data, "****")
        apples = ar_data[1].split("|") if ar_data[1] else []
        if ar_data[2]:
            players = [pl.split(",") for pl in ar_data[2].split("|")]
        else:
            players = []
