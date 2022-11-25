import os

import pygame as pg
import random
import socket

# HOST = "192.168.1.11"
# PORT = 9090
with open(os.getcwd() + "\settings.txt", "r") as f:
    HOST = f.readline().replace("\n", "").split()[1]
    server_host = f.readline().replace("\n", "").split()[1]
    PORT = int(f.readline().split()[1])
    wsize = tuple(map(int, f.readline().split()[1].split(",")))
    flags = f.readline().split()[1]

# HOST = "localhost"
SIZE_DATA = 1024 * 32

# SnakeSocketClient-old.py
# pyinstaller SnakeMultiplayerSocket\SnakeClient.py --noconsole --onefile -n SnakeClient

pg.init()
WSIZE = wsize
screen = pg.display.set_mode(WSIZE)
clock = pg.time.Clock()

background_color = "#27272A"
font_end = pg.font.SysFont("Arial", 50)
font_2 = pg.font.SysFont("Arial", 20)
font_score = pg.font.SysFont("Arial", 24, bold=True)
font_board = pg.font.SysFont("Arial", 18)
font_myboard = pg.font.SysFont("Arial", 18, bold=True)

font_start = pg.font.SysFont("Arial", 85)
font_data = pg.font.SysFont("Arial", 19)


def start_menu_loop():
    global running
    running = True
    screen.fill(background_color)
    draw_help()
    text = font_data.render(f"Server: {HOST}:{PORT}", True, "white")
    screen.blit(text, (10, 5))
    text = font_start.render("SNAKE online", True, "#16A34A")
    screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 - text.get_height() // 2))
    text = font_2.render("Press any key for start", True, "white")
    screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 + 50))
    pg.display.flip()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                running = False


def randxy_st(toint=False):
    pos = f"{random.randint(0, MSIZE[0] - 1)},{random.randint(0, MSIZE[1] - 1)}"
    cx, cy = MSIZE[0] // 2, MSIZE[1] // 2
    ceneters = ((cx, cy),)
    while pos in apples or pos in stones or pos in ceneters:
        pos = f"{random.randint(0, MSIZE[0] - 1)},{random.randint(0, MSIZE[1] - 1)}"
    if toint:
        return tuple(map(int, pos.split(",")))
    return pos


def send_my_data():
    global apple_eated, apple_add, stone_add
    poses = "*".join([f"{x}/{y}" for x, y in snake])
    out = f"{name};{color};{int(alive)};{apple_add};{apple_eated};{stone_add};{poses};".encode()
    # print("SEND", out)
    sock.send(out)
    apple_eated = "0"
    apple_add = "0"
    stone_add = "0"


def draw_help():
    x, y = 7, WSIZE[1] - 100
    pg.draw.rect(screen, "red", (1 + x, y + 1, TSIDE - 4, TSIDE - 4))
    screen.blit(font_data.render("- Apple", True, "white"), (x + TSIDE + 5, y + 0))
    y += TSIDE + 2
    pg.draw.rect(screen, "purple", (1 + x, 1 + y, TSIDE - 4, TSIDE - 4))
    screen.blit(font_data.render("- Teleport", True, "white"), (x + TSIDE + 5, y + 0))
    y += TSIDE + 2
    pg.draw.rect(screen, "gray", (1 + x, 1 + y, TSIDE - 4, TSIDE - 4))
    screen.blit(font_data.render("- Stone", True, "white"), (x + TSIDE + 5, y + 0))


SMOOTH_CAMERA = True
INFINITY_MAP = True
snake_teleported = False
TSIDE = 30

direction = 0
set_direction = direction
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
alive = True
immortal = "i" in flags
start_length = 20 if "l" in flags else 1
# apple = randxy_st()
scroll = [0, 0]

main_apples_count = 15
stones_count = 45
teleports_count = 10

apple_eated = "0"
apple_add = "0"
stone_add = "0"
stones = []
apples = []
teleports = []

last_step_tick = 0
start_tick = 50 if "s" in flags else 220
step_tick = start_tick

start_menu_loop()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(b"start")
    data = sock.recv(SIZE_DATA)
    data_lst = data.decode().split(";")[:-1]
    print("init", data_lst)
    _, name, color, xy, _msize, _apples, _stones, _players = data_lst
    if _msize == "0":
        MSIZE = WSIZE[0] // TSIDE * 2, WSIZE[1] // TSIDE * 2
        sock.send(("MSIZE;" + ",".join(map(str, MSIZE))).encode())
    else:
        MSIZE = tuple(map(int, _msize.split(",")))

    SMSIZE = MSIZE[0] * TSIDE, MSIZE[1] * TSIDE
    if WSIZE[0] > SMSIZE[0]:
        WSIZE = SMSIZE
        screen = pg.display.set_mode(WSIZE)
    print(MSIZE)
    start_pos = MSIZE[0] // 2, MSIZE[1] // 2
    # snake = [randxy_st(toint=True)]

    if _apples:
        apples = _apples.split("|")
    else:
        apples = []
        apple_add = "|".join([randxy_st() for i in range(main_apples_count)])
    if _stones:
        stones = _stones.split("|")
    else:
        stones = []
        stone_add = "|".join([randxy_st() for i in range(stones_count)])
    teleports = [randxy_st() for i in range(teleports_count)]
    # start_pos = tuple(map(int, xy.split("/")))
    snake = [randxy_st(toint=True)] * start_length
    pg.display.set_caption("Snake client: " + name + f" ({color})")
    print("sanke", snake)
    send_my_data()

    data = sock.recv(SIZE_DATA).decode()
    players = []
    running = True
    while running:
        elapsed_time = clock.tick(120)
        screen.fill(background_color)
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
                        snake = [randxy_st(toint=True)]
                        # apple = randxy_st()
                        alive = True
                        step_tick = start_tick
        print(apples)
        sx, sy = snake[0]
        if SMOOTH_CAMERA:
            # if snake_teleported and (sx == 0 or sx == MSIZE[0]-1):
            #     scroll[0] = (sx * TSIDE - WSIZE[0] // 2)
            # if snake_teleported and (sy == 0 or sy == MSIZE[1]-1):
            #     scroll[1] = (sy * TSIDE - WSIZE[1] // 2)
            t_cof = (max(elapsed_time, 1) / 1000)
            scroll[0] += ((sx * TSIDE - WSIZE[0] // 2) - scroll[0]) * t_cof *10
            scroll[1] += (sy * TSIDE - WSIZE[1] // 2 - scroll[1]) * t_cof *10

        else:
            scroll = [(sx * TSIDE - WSIZE[0] // 2), (sy * TSIDE - WSIZE[1] // 2)]
        if not INFINITY_MAP:
            scroll = [min(SMSIZE[0] - WSIZE[0], max(0, scroll[0])),
                      min(SMSIZE[1] - WSIZE[1], max(0, scroll[1]))]
        pg.draw.rect(screen, "purple", (-scroll[0], -scroll[1], SMSIZE[0], SMSIZE[1]), 2)
        for apple in apples:
            if not apple:
                continue
            ax, ay = map(int, apple.split(","))
            pg.draw.rect(screen, "red", (int(ax * TSIDE - scroll[0] + TSIDE) % SMSIZE[0] - TSIDE + 1,
                                         int(ay * TSIDE - scroll[1] + TSIDE) % SMSIZE[1] - TSIDE + 1,
                                         TSIDE - 2, TSIDE - 2))
        for stone in stones:
            if not stone:
                continue
            ax, ay = map(int, stone.split(","))
            pg.draw.rect(screen, "gray", (int(ax * TSIDE - scroll[0] + TSIDE) % SMSIZE[0] - TSIDE + 1,
                                          int(ay * TSIDE - scroll[1] + TSIDE) % SMSIZE[1] - TSIDE + 1,
                                          TSIDE - 2, TSIDE - 2))
        for teleport in teleports:
            if not teleport:
                continue
            ax, ay = map(int, teleport.split(","))
            pg.draw.rect(screen, "purple", (int(ax * TSIDE - scroll[0] + TSIDE) % SMSIZE[0] - TSIDE + 1,
                                            int(ay * TSIDE - scroll[1] + TSIDE) % SMSIZE[1] - TSIDE + 1,
                                            TSIDE - 2, TSIDE - 2))
        [pg.draw.rect(screen, color, (int(x * TSIDE - scroll[0] + TSIDE) % SMSIZE[0] - TSIDE + 1,
                                      int(y * TSIDE - scroll[1] + TSIDE) % SMSIZE[1] - TSIDE + 1,
                                      TSIDE - 2, TSIDE - 2)) for x, y in snake]
        # print("players", players)
        all_poses = []

        scores = []
        for player in players:
            player_poses = [tuple(map(int, p.split("/"))) for p in player[2].split("*")]
            scores.append((len(player_poses), player[0], player[1]))
            if player[0] == name:
                continue
            all_poses += player_poses
            [pg.draw.rect(screen, player[1], (int(x * TSIDE - scroll[0] + TSIDE) % SMSIZE[0] - TSIDE + 1,
                                              int(y * TSIDE - scroll[1] + TSIDE) % SMSIZE[1] - TSIDE + 1,
                                              TSIDE - 2, TSIDE - 2)) for x, y in
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
                    new_pos = random.randint(0, MSIZE[0] - 1), random.randint(0, MSIZE[1] - 1)
                if INFINITY_MAP:
                    snake_teleported = True
                    if new_pos[0] >= MSIZE[0]:
                        new_pos = (0, new_pos[1])
                    elif new_pos[1] >= MSIZE[1]:
                        new_pos = (new_pos[0], 0)
                    elif new_pos[0] < 0:
                        new_pos = (MSIZE[0] - 1, new_pos[1])
                    elif new_pos[1] < 0:
                        new_pos = (new_pos[0], MSIZE[1] - 1)
                    else:
                        snake_teleported = False
                st_pos = ",".join(map(str, new_pos))
                if st_pos in teleports:
                    st_pos = random.choice(teleports)
                    new_pos = tuple(map(int, st_pos.split(",")))
                if new_pos in snake or new_pos in all_poses or st_pos in stones or \
                        not (0 <= new_pos[0] < MSIZE[0] and 0 <= new_pos[1] < MSIZE[1]):
                    if not immortal:
                        alive = False
                        # apple_add = ",".join(map(str, new_pos))
                        apple_add = "!".join([",".join(map(str, snake[i])) for i in range(len(snake)) if i % 2 == 0])
                else:

                    print("apples", apples)
                    if st_pos in apples:
                        snake.append((0, 0))
                        apple_eated = st_pos
                        apple_add = randxy_st()
                        step_tick = max(50, step_tick - step_tick // 25)
                    snake.insert(0, new_pos)
                    snake.pop(-1)
        else:
            text = font_end.render("GAME OVER", True, "white")
            screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 - 40))
            text = font_2.render("Press SPACE for restart", True, "white")
            screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 + 20))
        text = font_score.render("Score: " + str(len(snake)), True, "white")
        screen.blit(text, (10, 7))
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
        stones = ar_data[2].split("|") if ar_data[2] else []
        if ar_data[3]:
            players = [pl.split(",") for pl in ar_data[3].split("|")]
        else:
            players = []
