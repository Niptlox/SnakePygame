import pygame as pg

from src.ClassUI import SurfaceUI

ACENTER = "center"
ALEFT = "left"


class TextLabel(SurfaceUI):
    def __init__(self, rect, text, font, color, bg_color=(0, 0, 0, 0), text_align=ACENTER):
        super(TextLabel, self).__init__(rect)
        self.convert_alpha()
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.font: pg.font.Font = font
        self.text_align = text_align
        self.text_pos = (0, 0)
        self.render_text()

    def get_text_position(self, img):
        if self.text_align == ACENTER:
            w, h = img.get_size()
            x, y = (self.rect.w - w) // 2, (self.rect.h - h) // 2
        elif self.text_align == ALEFT:
            w, h = img.get_size()
            x, y = 2, (self.rect.h - h) // 2
        else:
            x, y = 0, 0
        return x, y

    def set_text(self, text):
        self.text = text
        self.render_text()

    def render_text(self):
        self.fill(self.bg_color)
        text = self.font.render(self.text, True, self.color)
        self.text_pos = self.get_text_position(text)
        self.blit(text, self.text_pos)


class TextInput(TextLabel):
    def __init__(self, rect, text, font, color, cursor_color=None, cursor_pos=0, cursor_enable=True,
                 active_typing=False, enable_typing=True, on_finish_typing=lambda text: None, input_type=str,
                 **kwargs):
        """InputText(rect, text, font, color, cursor=0, bg_color=(0, 0, 0, 0), text_align=ACENTER)"""
        self.cursor_enable = cursor_enable
        self.cursor_pos = cursor_pos
        self.cursor_xy = (0, 0)
        self.cursor_img = pg.Surface((1, pg.Rect(rect).h - 4))
        self.cursor_img.fill(cursor_color or color)
        self.cursor_timer = 0
        self.cursor_time = 30
        # происходит набор тескта
        self.active_typing = active_typing
        # можно ли набирать текст
        self.enable_typing = enable_typing
        self.on_finish_typing = on_finish_typing
        self.input_type = input_type
        super(TextInput, self).__init__(rect, text, font, color, **kwargs)

    def pg_event(self, event: pg.event.Event):
        if not self.enable_typing:
            self.active_typing = False
        if self.enable_typing:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(*event.pos):
                    self.active_typing = True
                elif self.active_typing:
                    self.finish_typing()
        if event.type == pg.KEYDOWN:
            if self.active_typing:
                if event.key == pg.K_KP_ENTER:
                    self.finish_typing()
                if event.key == pg.K_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pg.K_RIGHT:
                    self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                elif event.key == pg.K_HOME:
                    self.cursor_pos = 0
                elif event.key == pg.K_END:
                    self.cursor_pos = len(self.text)
                elif event.key == pg.K_BACKSPACE and self.cursor_pos != 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pg.K_DELETE and self.cursor_pos != len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                elif len(pg.key.name(event.key)) == 1:
                    self.symbol_keydown(pg.key.name(event.key))
                else:
                    return
                self.cursor_timer = 0
                self.render_text()

    def symbol_keydown(self, keyname):
        if self.input_type is int and keyname not in "0123456789":
            return
        if self.input_type is float and (keyname not in "0123456789." or (keyname == "." and "." in self.text)):
            return
        if bool(pg.key.get_mods() & pg.KMOD_SHIFT) ^ bool(pg.key.get_mods() & pg.KMOD_CAPS):
            keyname = keyname.upper()
        self.text = self.text[:self.cursor_pos] + keyname + self.text[self.cursor_pos:]
        self.cursor_pos = min(len(self.text), self.cursor_pos + 1)

    def draw(self, display):
        surface = self.copy()
        if self.cursor_enable and self.active_typing:
            self.cursor_timer = (self.cursor_timer + 1) % self.cursor_time
            if self.cursor_timer < (self.cursor_time // 2):
                surface.blit(self.cursor_img, self.cursor_xy)
        display.blit(surface, self.rect)

    def finish_typing(self):
        if self.input_type is float:
            if self.text[0] == ".":
                self.text = "0" + self.text
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            if self.text[-1] == ".":
                self.text = self.text + "0"
            self.render_text()
            self.on_finish_typing(float(self.text))
        elif self.input_type is int:
            self.on_finish_typing(int(self.text))
        else:
            self.on_finish_typing(self.text)
        self.active_typing = False

    def render_text(self):
        self.fill(self.bg_color)
        text = self.font.render(self.text, True, self.color)
        self.text_pos = self.get_text_position(text)
        self.blit(text, self.text_pos)
        text = self.font.render(self.text[:self.cursor_pos], True, self.color)
        self.cursor_xy = self.text_pos[0] + text.get_width() - 1, 2


class TextLabelAndInput(SurfaceUI):
    def __init__(self, width, label_text, input_obj: TextInput, text_align=ALEFT, color=None, bg_color=None):
        rect = pg.Rect(input_obj.rect.x, input_obj.rect.y, width, input_obj.rect.h)
        super(TextLabelAndInput, self).__init__(rect)
        self.input_obj = input_obj
        self.input_obj.rect.x = self.rect.right
        self.label = TextLabel(rect, label_text, input_obj.font, color or input_obj.color,
                               bg_color=bg_color or self.input_obj.bg_color,
                               text_align=text_align)

    def pg_event(self, event: pg.event.Event):
        self.input_obj.pg_event(event)

    def draw(self, surface):
        self.input_obj.draw(surface)
        self.label.draw(surface)
