from random import randint

import pygame as pg


def kill():
    global alive
    alive = False


def restart():
    global alive, snake, length, direction
    alive = True
    snake = [snake_start, ]
    length = 1
    direction = 0


scale = int(3)
# map size
MSIZE = (72 // scale, 48 // scale)
# tile size
TSIDE = 10 * scale
FPS = 60
WSIZE = (MSIZE[0] * TSIDE, MSIZE[1] * TSIDE)
screen = pg.display.set_mode(WSIZE)

pg.font.init()
font = pg.font.SysFont("", 50)
font_2 = pg.font.SysFont("", 22)
font_score = pg.font.SysFont("", 25)
snake_start = (MSIZE[0] // 2, MSIZE[1] // 2)
snake = [snake_start, ]
length = 1
direction = 0
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

head_img = pg.Surface((TSIDE, TSIDE))
head_img.fill("green")
snake_tile_img = pg.Surface((TSIDE, TSIDE))
snake_tile_img.fill("#00AA00")
running = True
clock = pg.time.Clock()
t = 0
apple_img = pg.Surface((TSIDE, TSIDE))
apple_img.fill("red")
apple = (randint(0, MSIZE[0] - 1), randint(0, MSIZE[1] - 1))
alive = True

while running:
    clock.tick(FPS)
    screen.fill("black")
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if alive:
                if event.key == pg.K_d:
                    direction = 0
                elif event.key == pg.K_s:
                    direction = 1
                elif event.key == pg.K_a:
                    direction = 2
                elif event.key == pg.K_w:
                    direction = 3
            if event.key == pg.K_SPACE and not alive:
                restart()
    i = 0
    for pos in snake:
        if i == 0:
            img = head_img
        else:
            img = snake_tile_img
        screen.blit(img, (pos[0] * TSIDE, pos[1] * TSIDE))
        i += 1
    screen.blit(apple_img, (apple[0] * TSIDE, apple[1] * TSIDE))
    if t % (FPS // 4) == 0 and alive:
        new_pos = (snake[0][0] + directions[direction][0], snake[0][1] + directions[direction][1])
        for pos in snake[1:]:
            if pos[0] == new_pos[0] and pos[1] == new_pos[1]:
                kill()
        if not (0 <= new_pos[0] < MSIZE[0] and 0 <= new_pos[1] < MSIZE[1]):
            kill()
        if alive:
            if apple[0] == snake[0][0] and apple[1] == snake[0][1]:
                apple = (randint(0, MSIZE[0] - 1), randint(0, MSIZE[1] - 1))
                length += 1
                snake.append((0, 0))
            snake.insert(0, new_pos)
            snake.pop(-1)
    if not alive:
        text = font.render("GAME OVER", True, "white")
        screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 - 20))
        text = font_2.render("Press SPACE for restart", True, "white")
        screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 + 20))
    text = font_score.render("Score: " + str(length), True, "white")
    screen.blit(text, (10, 10))
    t += 1
    pg.display.flip()
