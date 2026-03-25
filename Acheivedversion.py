"""
Lucky 7s Casino Slot Machine - Pygame Edition
Requirements: pip install pygame
Run: python slot_machine.py
"""

import pygame
import random
import math
import sys

# ── Init ─────────────────────────────────────────────────────────────────────
pygame.init()
pygame.display.set_caption("Lucky 7s – Casino Slot Machine")
SCREEN_W, SCREEN_H = 520, 680
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
FPS = 60

# ── Colours ───────────────────────────────────────────────────────────────────
C_BG         = (18, 8, 3)
C_MAHOGANY   = (42, 26, 14)
C_GOLD       = (201, 147, 58)
C_GOLD_LT    = (245, 200, 66)
C_REEL_BG    = (255, 255, 255)
C_DARK       = (13, 7, 5)
C_GREEN_WIN  = (80, 255, 136)
C_RED_LOSE   = (255, 80, 80)
C_RED_KNOB   = (200, 16, 16)
C_WHITE      = (255, 255, 255)
C_GRAY       = (160, 160, 160)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    try:
        return pygame.font.SysFont("Georgia", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

def load_mono(size, bold=False):
    try:
        return pygame.font.SysFont("Courier New", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

font_title = load_font(34, bold=True)
font_sub   = load_mono(13)
font_big   = load_mono(20, bold=True)
font_med   = load_mono(15)
font_sm    = load_mono(12)

# ── Game constants ─────────────────────────────────────────────────────────────
BET       = 5
START_BAL = 50

# Symbol indices
SYM_LABELS  = ["7", "♦", "♥", "♣", "★", "●", "◆"]
SYM_COLORS  = [
    (255, 60,  60),    # 7   – red
    (120, 220, 255),   # ♦   – cyan
    (255, 100, 100),   # ♥   – pink
    (240, 220, 80),    # ♣   – yellow
    (255, 230, 80),    # ★   – gold
    (255, 160, 50),    # ●   – orange
    (180, 100, 255),   # ◆   – purple
]
NUM_SYMS = len(SYM_LABELS)

PAYOUTS = {
    (0, 0, 0): 100,
    (1, 1, 1): 50,
    (2, 2, 2): 20,
    (3, 3, 3): 15,
    (4, 4, 4): 10,
}
PAIR_SYMS = {2, 4}   # ♥ and ★ pay $5 for a pair

REEL_W   = 90
REEL_H   = 110
REEL_GAP = 10
REEL_Y   = 180
REEL_X0  = (SCREEN_W - (3 * REEL_W + 2 * REEL_GAP)) // 2
SPIN_DELAYS = [0.0, 0.22, 0.44]

# ── Helpers ──────────────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def draw_text_center(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def lerp(a, b, t):
    return a + (b - a) * t

# ── Coin particle ─────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, x, y):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 200)
        self.x  = float(x)
        self.y  = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(60, 120)
        self.life = 1.0
        self.r  = random.randint(5, 9)

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 400 * dt
        self.life -= dt * 1.8

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = max(0, int(self.life * 255))
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (245, 200, 66, alpha), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x - self.r), int(self.y - self.r)))

# ── Reel ──────────────────────────────────────────────────────────────────────
class Reel:
    STRIP_LEN = 20

    def __init__(self, col_idx):
        self.col_idx  = col_idx
        self.x        = REEL_X0 + col_idx * (REEL_W + REEL_GAP)
        self.symbols  = [random.randint(0, NUM_SYMS - 1) for _ in range(self.STRIP_LEN)]
        self.offset   = 0.0      # pixels scrolled (each cell = REEL_H px)
        self.vel      = 0.0
        self.braking  = False
        self.done     = False
        self.spinning = False
        self.target   = 0        # target symbol to show
        self._sym_font = load_font(28, bold=True)

    def start(self, result_sym):
        self.symbols[2] = result_sym
        self.target   = result_sym
        self.offset   = 0.0
        self.vel      = 2200.0
        self.braking  = False
        self.done     = False
        self.spinning = True
        self._target_offset = 2 * REEL_H

    def update(self, dt):
        if not self.spinning:
            return
        if not self.braking:
            self.offset += self.vel * dt
            # start braking once we've done most of the scroll
            if self.offset >= self.STRIP_LEN * REEL_H * 0.55:
                self.braking = True
                self._brake_elapsed = 0.0
                self._brake_start   = self.offset
        else:
            self._brake_elapsed += dt
            t    = min(self._brake_elapsed / 0.42, 1.0)
            ease = 1 - (1 - t) ** 3
            # target: land on _target_offset within current full cycle
            full = self.STRIP_LEN * REEL_H
            cycles = int(self._brake_start / full)
            final  = cycles * full + self._target_offset
            if final < self._brake_start:
                final += full
            self.offset = lerp(self._brake_start, final, ease)
            if t >= 1.0:
                self.offset  = final % (self.STRIP_LEN * REEL_H)
                self.vel     = 0
                self.spinning = False
                self.done    = True

    def visible_sym(self):
        idx = int(round(self.offset / REEL_H)) % self.STRIP_LEN
        return self.symbols[idx]

    def draw(self, surf):
        rect = pygame.Rect(self.x, REEL_Y, REEL_W, REEL_H)
        draw_rounded_rect(surf, C_REEL_BG, rect, 6, 2, C_GOLD)

        center_idx = self.offset / REEL_H
        for di in range(-1, 3):
            raw_idx = int(center_idx) + di
            sym_idx = raw_idx % self.STRIP_LEN
            sym     = self.symbols[sym_idx]
            frac    = center_idx - int(center_idx)
            py      = REEL_Y + int(di * REEL_H - frac * REEL_H) + REEL_H // 2
            if REEL_Y <= py <= REEL_Y + REEL_H:
                self._draw_symbol(surf, sym, self.x + REEL_W // 2, py)

        # fade top/bottom
        for shade_y, flip in [(REEL_Y, False), (REEL_Y + REEL_H - 30, True)]:
            s = pygame.Surface((REEL_W, 30), pygame.SRCALPHA)
            for i in range(30):
                a = int(210 * (1 - i / 30)) if not flip else int(210 * (i / 30))
                pygame.draw.line(s, (13, 7, 5, a), (0, i), (REEL_W, i))
            surf.blit(s, (self.x, shade_y))

    def _draw_symbol(self, surf, sym, cx, cy):
        color = SYM_COLORS[sym]
        r = 30
        pygame.draw.circle(surf, color, (cx, cy), r)
        pygame.draw.circle(surf, C_DARK, (cx, cy), r, 2)
        label = SYM_LABELS[sym]
        f = load_font(30, bold=True) if sym == 0 else load_font(22, bold=True)
        txt_color = C_GOLD_LT if sym == 0 else C_WHITE
        img = f.render(label, True, txt_color)
        surf.blit(img, img.get_rect(center=(cx, cy)))

# ── Lever ─────────────────────────────────────────────────────────────────────
class Lever:
    TX = SCREEN_W - 66
    TY = REEL_Y - 18
    TW = 18
    TH = 140
    KR = 14

    def __init__(self):
        self.pull_t    = 0.0
        self.pulling   = False
        self.returning = False
        self.done      = False

    @property
    def cx(self):
        return self.TX + self.TW // 2

    @property
    def knob_y(self):
        ease = self.pull_t * self.pull_t * (3 - 2 * self.pull_t)
        top  = self.TY + self.KR + 4
        bot  = self.TY + self.TH - self.KR - 4
        return int(top + (bot - top) * ease)

    def pull(self):
        self.pulling   = True
        self.returning = False
        self.done      = False

    def update(self, dt):
        if self.pulling:
            self.pull_t += dt * 3.5
            if self.pull_t >= 1.0:
                self.pull_t    = 1.0
                self.pulling   = False
                self.returning = True
        elif self.returning:
            self.pull_t -= dt * 2.5
            if self.pull_t <= 0.0:
                self.pull_t    = 0.0
                self.returning = False
                self.done      = True

    def hit_test(self, pos):
        return math.hypot(pos[0] - self.cx, pos[1] - self.knob_y) <= self.KR + 10

    def draw(self, surf):
        track = pygame.Rect(self.TX, self.TY, self.TW, self.TH)
        draw_rounded_rect(surf, C_MAHOGANY, track, 9, 2, C_GOLD)
        ky  = self.knob_y
        bot = self.TY + self.TH
        pygame.draw.line(surf, C_GOLD, (self.cx, ky + self.KR), (self.cx, bot), 4)
        pygame.draw.circle(surf, C_RED_KNOB, (self.cx, ky), self.KR)
        pygame.draw.circle(surf, C_GOLD, (self.cx, ky), self.KR, 2)
        pygame.draw.circle(surf, (230, 80, 80), (self.cx - 4, ky - 4), 4)
        base = pygame.Rect(self.TX - 9, bot, self.TW + 18, 12)
        draw_rounded_rect(surf, C_GOLD, base, 4)
        lbl = font_sm.render("PULL", True, C_GOLD)
        surf.blit(lbl, lbl.get_rect(center=(self.cx, bot + 22)))

# ── Button ────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, text, cx, cy, w=160, h=38):
        self.text    = text
        self.rect    = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.hovered = False

    def draw(self, surf):
        col = C_GOLD_LT if self.hovered else C_GOLD
        draw_rounded_rect(surf, col, self.rect, 8)
        img = font_med.render(self.text, True, C_DARK)
        surf.blit(img, img.get_rect(center=self.rect.center))

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ── Main game ─────────────────────────────────────────────────────────────────
class SlotGame:
    # states: idle | lever | spin_delay | spinning | idle | gameover
    def __init__(self):
        self.balance      = START_BAL
        self.reels        = [Reel(i) for i in range(3)]
        self.lever        = Lever()
        self.coins        = []
        self.msg          = "Click the lever to spin!"
        self.msg_color    = C_GOLD_LT
        self.win_line     = False
        self.state        = "idle"
        self.outcome      = []
        self._delay_timers  = [0.0, 0.0, 0.0]
        self._reels_started = [False, False, False]
        self.restart_btn  = Button("PLAY AGAIN", SCREEN_W // 2, SCREEN_H - 68)

    # ── Spin ──────────────────────────────────────────────────────────────────
    def _pick_outcome(self):
        r = random.random()
        if r < 0.03:  return [0, 0, 0]
        if r < 0.07:  return [1, 1, 1]
        if r < 0.13:  return [2, 2, 2]
        if r < 0.18:  return [3, 3, 3]
        if r < 0.24:  return [4, 4, 4]
        if r < 0.34:
            sym = random.choice(list(PAIR_SYMS))
            res = [sym, sym, sym]
            pos = random.randint(0, 2)
            res[pos] = random.choice([s for s in range(NUM_SYMS) if s != sym])
            return res
        while True:
            syms = [random.randint(0, NUM_SYMS - 1) for _ in range(3)]
            if len(set(syms)) == 3:
                return syms

    def _calc_win(self):
        key = tuple(self.outcome)
        if key in PAYOUTS:
            return PAYOUTS[key]
        counts = {}
        for s in self.outcome:
            counts[s] = counts.get(s, 0) + 1
        for s in PAIR_SYMS:
            if counts.get(s, 0) >= 2:
                return 5
        return 0

    def do_spin(self):
        if self.state != "idle":
            return
        if self.balance < BET:
            self.msg, self.msg_color = "Out of money!", C_RED_LOSE
            return
        self.balance -= BET
        self.outcome    = self._pick_outcome()
        self.win_line   = False
        self.msg        = ""
        self.state      = "lever"
        self.lever.pull()
        self._delay_timers  = [0.0, 0.0, 0.0]
        self._reels_started = [False, False, False]

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        self.lever.update(dt)
        for c in self.coins[:]:
            c.update(dt)
            if c.life <= 0:
                self.coins.remove(c)

        if self.state == "lever":
            if self.lever.pull_t >= 0.5:
                self.state = "spin_delay"

        if self.state == "spin_delay":
            all_started = True
            for i in range(3):
                if not self._reels_started[i]:
                    self._delay_timers[i] += dt
                    if self._delay_timers[i] >= SPIN_DELAYS[i]:
                        self.reels[i].start(self.outcome[i])
                        self._reels_started[i] = True
                    else:
                        all_started = False
            if all_started:
                self.state = "spinning"

        if self.state == "spinning":
            for r in self.reels:
                r.update(dt)
            if all(r.done for r in self.reels):
                self._resolve()

    def _resolve(self):
        win = self._calc_win()
        self.balance += win
        if win > 0:
            self.win_line = True
            n = 24 if win >= 50 else (12 if win >= 20 else 6)
            cx, cy = SCREEN_W // 2, REEL_Y + REEL_H // 2
            self.coins = [Coin(cx + random.randint(-80, 80), cy) for _ in range(n)]
            if win == 100:
                self.msg = f"JACKPOT!  +${win}"
            elif win >= 20:
                self.msg = f"BIG WIN!  +${win}"
            else:
                self.msg = f"You won ${win}!"
            self.msg_color = C_GREEN_WIN
        else:
            self.msg       = "No luck this time."
            self.msg_color = C_RED_LOSE

        self.state = "gameover" if self.balance < BET else "idle"

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self):
        screen.fill(C_BG)
        # machine body
        body = pygame.Rect(30, 58, SCREEN_W - 96, SCREEN_H - 128)
        draw_rounded_rect(screen, C_MAHOGANY, body, 18, 3, C_GOLD)
        draw_rounded_rect(screen, (30, 18, 8), body.inflate(-10, -10), 14)

        # header
        draw_text_center(screen, "LUCKY  7s", font_title, C_GOLD_LT, SCREEN_W // 2 - 28, 94)
        draw_text_center(screen, "V E G A S   E D I T I O N", font_sub, C_GOLD, SCREEN_W // 2 - 28, 120)

        # reels
        for r in self.reels:
            r.draw(screen)

        # win line
        if self.win_line:
            my = REEL_Y + REEL_H // 2
            s  = pygame.Surface((3 * REEL_W + 2 * REEL_GAP + 8, 3), pygame.SRCALPHA)
            s.fill((255, 60, 60, 200))
            screen.blit(s, (REEL_X0 - 4, my - 1))

        # HUD
        hud_y = REEL_Y + REEL_H + 16
        for rect, lbl, val, vcol in [
            (pygame.Rect(REEL_X0, hud_y, 130, 52),       "BALANCE",    f"${self.balance}", C_GOLD_LT),
            (pygame.Rect(REEL_X0 + 140, hud_y, 130, 52), "COST/PULL",  f"${BET}",          C_GRAY),
        ]:
            draw_rounded_rect(screen, C_DARK, rect, 8, 1, C_GOLD)
            draw_text_center(screen, lbl, font_sm,  C_GOLD,  rect.centerx, hud_y + 14)
            draw_text_center(screen, val, font_big, vcol,    rect.centerx, hud_y + 36)

        # message
        if self.msg:
            draw_text_center(screen, self.msg, font_med, self.msg_color,
                             SCREEN_W // 2 - 28, REEL_Y + REEL_H + 84)

        # lever
        self.lever.draw(screen)

        # coins
        for c in self.coins:
            c.draw(screen)

        # payout table
        self._draw_payouts()

        # game over overlay
        if self.state == "gameover":
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))
            draw_text_center(screen, "GAME  OVER",    font_title, C_RED_LOSE,  SCREEN_W // 2, SCREEN_H // 2 - 44)
            draw_text_center(screen, "Out of money!", font_med,   C_GRAY,      SCREEN_W // 2, SCREEN_H // 2)
            self.restart_btn.draw(screen)

        pygame.display.flip()

    def _draw_payouts(self):
        py = REEL_Y + REEL_H + 110
        draw_text_center(screen, "─── PAYOUTS ───", font_sm, C_GOLD, SCREEN_W // 2 - 28, py)
        rows = [
            ("7  7  7",  "+$100  JACKPOT"),
            ("♦  ♦  ♦",  "+$50"),
            ("♥  ♥  ♥",  "+$20"),
            ("♣  ♣  ♣",  "+$15"),
            ("★  ★  ★",  "+$10"),
            ("♥♥ / ★★",  "+$5   pair"),
        ]
        for i, (syms, payout) in enumerate(rows):
            ry = py + 18 + i * 17
            s_img = font_sm.render(syms,   True, C_GOLD_LT)
            p_img = font_sm.render(payout, True, C_GOLD)
            screen.blit(s_img, s_img.get_rect(midleft=(REEL_X0,       ry)))
            screen.blit(p_img, p_img.get_rect(midright=(REEL_X0 + 265, ry)))

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "gameover":
                if self.restart_btn.clicked(event.pos):
                    self.__init__()
            elif self.state == "idle":
                if self.lever.hit_test(event.pos):
                    self.do_spin()
        elif event.type == pygame.MOUSEMOTION:
            if self.state == "gameover":
                self.restart_btn.update_hover(event.pos)

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    game = SlotGame()
    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update(dt)
        game.draw()

if __name__ == "__main__":
    main()