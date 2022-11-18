import pygame as pg
import random


def randxy():
    return random.randint(0, MSIZE[0] - 1), random.randint(0, MSIZE[1] - 1)


TSIDE = 30
WSIZE = (720, 480)
MSIZE = WSIZE[0] // TSIDE, WSIZE[1] // TSIDE

direction = 0
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
start_pos = MSIZE[0] // 2, MSIZE[1] // 2
snake = [start_pos]
alive = True
apple = randxy()

pg.init()
screen = pg.display.set_mode(WSIZE)
clock = pg.time.Clock()
fps = 4

font_end = pg.font.SysFont("Arial", 50)
font_2 = pg.font.SysFont("Arial", 20)
font_score = pg.font.SysFont("Arial", 25)


running = True
while running:
    screen.fill("black")
    clock.tick(fps)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if alive:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT and direction != 2:
                    direction = 0
                if event.key == pg.K_DOWN and direction != 3:
                    direction = 1
                if event.key == pg.K_LEFT and direction != 0:
                    direction = 2
                if event.key == pg.K_UP and direction != 1:
                    direction = 3
        else:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    direction = 0
                    snake = [(MSIZE[0] // 2, MSIZE[1] // 2)]
                    apple = randxy()
                    alive = True
                    fps = 4
    [pg.draw.rect(screen, "green", (x * TSIDE, y * TSIDE, TSIDE - 1, TSIDE - 1)) for x, y in snake]
    pg.draw.rect(screen, "red", (apple[0] * TSIDE, apple[1] * TSIDE, TSIDE, TSIDE))

    if alive:
        new_pos = snake[0][0] + directions[direction][0], snake[0][1] + directions[direction][1]
        if new_pos in snake:
            alive = False
        elif not (0 <= new_pos[0] < MSIZE[0] and 0 <= new_pos[1] < MSIZE[1]):
            alive = False
        else:
            if new_pos == apple:
                snake.append((0, 0))
                apple = randxy()
                fps += 1
            snake.insert(0, new_pos)
            snake.pop(-1)
    else:
        text = font_end.render("GAME OVER", True, "white")
        screen.blit(text, (WSIZE[0] // 2 - text.get_width()//2, WSIZE[1] // 2 - 40))
        text = font_2.render("Press SPACE for restart", True, "white")
        screen.blit(text, (WSIZE[0] // 2 - text.get_width() // 2, WSIZE[1] // 2 + 20))
    text = font_score.render("Score: " + str(len(snake)), True, "yellow")
    screen.blit(text, (5, 5))
    pg.display.flip()
