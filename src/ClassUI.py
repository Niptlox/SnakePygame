import pygame as pg


# находит позицию xy чтобы один стоял в центре другого
def center_pos_2lens(len1, big_len):
    return big_len // 2 - len1 // 2


# находит позицию xy чтобы один стоял в центре другого
def center_pos_2rects(rect, big_rect):
    return center_pos_2lens(rect.w, big_rect.w), center_pos_2lens(rect.h, big_rect.h)


class UI:
    def __init__(self, scene) -> None:
        self.scene = scene
        self.screen = scene.screen
        self.display = self.scene.display
        self.rect = pg.Rect((0, 0), self.display.get_size())

    def init_ui(self):
        pass

    def draw(self):
        self.screen.blit(self.display, (0, 0))
        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        pass

    @property
    def onscreenx(self):
        return self.rect.x + self.scene.rect.x

    @property
    def onscreeny(self):
        return self.rect.y + self.scene.rect.y


class GroupUI:
    def __init__(self, components):
        self.components = components

    def add(self, obj):
        self.components.append(obj)

    def add_lst(self, lst_objs):
        for obj in lst_objs:
            self.add(obj)

    def pg_event(self, event):
        for component in self.components:
            component.pg_event(event)

    def draw(self, surface):
        for component in self.components:
            component.draw(surface)


class SurfaceUI(pg.Surface):
    def __init__(self, rect, flags=0, depth=0):
        # self.depth = depth
        self.rect = pg.Rect(rect)
        super().__init__(self.rect.size, flags)

    def draw(self, surface):
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):
        pass

    def set_size(self, size):
        self.rect.size = size
        super().__init__(self.rect.size, self.get_flags())

    def convert_alpha(self):
        """Изменяет саму плоскость"""
        super(SurfaceUI, self).__init__(self.rect.size, pg.SRCALPHA, 32)
        return self

    def set(self, surface):
        super(SurfaceUI, self).__init__(surface.get_size(), surface.get_flags(), 32)
        self.blit(surface, (0, 0))


class ScrollSurface(SurfaceUI):
    """Поле с прокруткой. Только для объектов с методом 'draw(surface)'"""

    def __init__(self, rect, scroll_size, scroll_pos=(0, 0), background="black"):
        super().__init__(rect)
        self.convert_alpha()
        self.scroll_surface = SurfaceUI((scroll_pos, scroll_size)).convert_alpha()
        self.objects = []
        self.background = background
        self.scroll_accel = [0, 0]

    def mouse_scroll(self, dx=0, dy=0):
        self.scroll_accel = [dx, dy]

        self.scroll_surface.rect.x += dx
        if self.scroll_surface.rect.x < 0:
            self.scroll_surface.rect.x = 0
        elif self.scroll_surface.rect.right > self.rect.w:
            self.scroll_surface.rect.right = self.rect.w
        if self.scroll_surface.rect.h > self.rect.h:
            self.scroll_surface.rect.y += dy
            if self.scroll_surface.rect.y > 0:
                self.scroll_surface.rect.y = 0
            elif self.scroll_surface.rect.bottom < self.rect.h:
                self.scroll_surface.rect.bottom = self.rect.h

    def main_scrolling(self):
        self.scroll_accel[0] //= 1.5
        self.scroll_accel[1] //= 1.5
        if 0 > self.scroll_accel[1] >= -3:
            self.scroll_accel[1] = 0
        if 0 > self.scroll_accel[0] >= -3:
            self.scroll_accel[0] = 0
        self.mouse_scroll(*self.scroll_accel)

    def add_objects(self, objects):
        self.objects += objects
        for obj in objects:
            if obj.rect.right > self.rect.w:
                self.set_size((obj.rect.right + 5, self.rect.h))
            if obj.rect.bottom > self.rect.h:
                self.set_size((self.rect.w, obj.rect.bottom + 5))

    def draw(self, surface):
        self.main_scrolling()
        self.scroll_surface.fill((0, 0, 0, 0))
        self.fill(self.background)
        for obj in self.objects:
            obj.draw(self.scroll_surface)
        self.blit(self.scroll_surface, self.scroll_surface.rect)
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):
        if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            mouse_pos = tuple(event.pos)
            if self.rect.collidepoint(mouse_pos):
                event.pos = (mouse_pos[0] - self.scroll_surface.rect.x, mouse_pos[1] - self.scroll_surface.rect.y)
                for obj in self.objects:
                    obj.pg_event(event)
                event.pos = mouse_pos
                return True

    def set_size(self, size):
        self.scroll_surface.set_size(size)
        super(ScrollSurface, self).set_size(size)

