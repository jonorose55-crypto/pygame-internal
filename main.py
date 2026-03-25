"""
Lucky 7s – DGT Edition  |  Pygame Slot Machine
-----------------------------------------------
Requirements : pip install pygame
Run          : python slot_machine.py

All reel symbols are drawn with pure pygame primitives (circles, polygons,
lines) – no font rendering or Unicode required, works on every platform.

"""

import pygame
import random
import math
import sys
import json
import os

# ─────────────────────────────────────────────────────────────────────────────
#  Bootstrap
# ─────────────────────────────────────────────────────────────────────────────
pygame.init()
SCREEN_W, SCREEN_H = 520, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Lucky 7s – DGT Edition")
clock = pygame.time.Clock()
FPS   = 60

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slot_save.json")

# ─────────────────────────────────────────────────────────────────────────────
#  Palette
# ─────────────────────────────────────────────────────────────────────────────
C_BG        = (18,  8,   3)
C_MAHOGANY  = (42,  26,  14)
C_PANEL     = (30,  18,  8)
C_GOLD      = (201, 147, 58)
C_GOLD_LT   = (245, 200, 66)
C_DARK      = (13,  7,   5)
C_WHITE     = (255, 255, 255)
C_GRAY      = (160, 160, 160)
C_GREEN_WIN = (80,  255, 136)
C_RED_LOSE  = (255, 80,  80)
C_RED_KNOB  = (200, 16,  16)
C_REEL_BG   = (245, 240, 228)

# ─────────────────────────────────────────────────────────────────────────────
#  Fonts  (UI only – NOT used for reel symbols)
# ─────────────────────────────────────────────────────────────────────────────
def _font(name, size, bold=False):
    try:    return pygame.font.SysFont(name, size, bold=bold)
    except: return pygame.font.Font(None, size)

F_TITLE = _font("Georgia",    34, bold=True)
F_SUB   = _font("Courier New",13)
F_BIG   = _font("Courier New",20, bold=True)
F_MED   = _font("Courier New",15)
F_SM    = _font("Courier New",12)
F_7     = _font("Georgia",    34, bold=True)   # only for the "7" numeral

# ─────────────────────────────────────────────────────────────────────────────
#  Symbol definitions
#  Each symbol is an index 0-6.  The actual drawing is all pygame primitives.
# ─────────────────────────────────────────────────────────────────────────────
#  0 = Seven    (red)
#  1 = Diamond  (cyan)
#  2 = Cherry   (red/green)
#  3 = Lemon    (yellow)
#  4 = Star     (gold)
#  5 = Bell     (orange)
#  6 = Grape    (purple)

NUM_SYMS = 7

# Background circle colour per symbol
SYM_BG = [
    (200, 40,  40),   # 0 Seven
    (50,  160, 220),  # 1 Diamond
    (200, 50,  60),   # 2 Cherry
    (210, 185, 40),   # 3 Lemon
    (210, 185, 40),   # 4 Star
    (210, 120, 30),   # 5 Bell
    (130, 60,  210),  # 6 Grape
]

# Payout table
PAYOUTS   = {(0,0,0):100, (1,1,1):50, (2,2,2):20, (3,3,3):15, (4,4,4):10}
PAIR_SYMS = {2, 4}   # Cherry pair or Star pair → $5

# Payout display rows  (label, payout string)
PAYOUT_ROWS = [
    ("7  7  7",    "+$100  JACKPOT"),
    ("Di Di Di",   "+$50"),
    ("Ch Ch Ch",   "+$20"),
    ("Le Le Le",   "+$15"),
    ("St St St",   "+$10"),
    ("Ch-Ch/St-St", "+$5  pair"),
]

# Reel geometry
REEL_W      = 90
REEL_H      = 110
REEL_GAP    = 10
REEL_Y      = 185
REEL_X0     = (SCREEN_W - (3*REEL_W + 2*REEL_GAP)) // 2
SPIN_DELAYS = [0.0, 0.22, 0.44]

BET       = 5
START_BAL = 50

# ─────────────────────────────────────────────────────────────────────────────
#  Symbol renderer  – pure pygame, zero fonts (except the "7")
# ─────────────────────────────────────────────────────────────────────────────
def draw_symbol(surf, sym, cx, cy, radius=28):
    """Draw symbol `sym` centred at (cx,cy) on `surf`. radius = circle bg size."""
    bg = SYM_BG[sym]
    # ── coloured background circle ──
    pygame.draw.circle(surf, bg,    (cx, cy), radius)
    pygame.draw.circle(surf, C_DARK,(cx, cy), radius, 2)

    if sym == 0:
        # ── SEVEN – bold red "7" rendered with font ──
        img = F_7.render("7", True, C_GOLD_LT)
        surf.blit(img, img.get_rect(center=(cx, cy)))

    elif sym == 1:
        # ── DIAMOND – four-point rotated square ──
        s = 18
        pts = [(cx, cy-s), (cx+s, cy), (cx, cy+s), (cx-s, cy)]
        pygame.draw.polygon(surf, C_WHITE, pts)
        pygame.draw.polygon(surf, C_DARK,  pts, 2)
        # inner highlight
        s2 = 8
        pygame.draw.polygon(surf, (180,230,255),
                             [(cx,cy-s2),(cx+s2,cy),(cx,cy+s2),(cx-s2,cy)])

    elif sym == 2:
        # ── CHERRY – two circles + stalks ──
        # left cherry
        pygame.draw.circle(surf, (210,30,30), (cx-8, cy+6), 9)
        pygame.draw.circle(surf, C_DARK,      (cx-8, cy+6), 9, 1)
        # right cherry
        pygame.draw.circle(surf, (240,50,50), (cx+8, cy+6), 9)
        pygame.draw.circle(surf, C_DARK,      (cx+8, cy+6), 9, 1)
        # stalks
        pygame.draw.line(surf, (60,150,40), (cx-8, cy-3), (cx,   cy-14), 2)
        pygame.draw.line(surf, (60,150,40), (cx+8, cy-3), (cx,   cy-14), 2)
        pygame.draw.line(surf, (60,150,40), (cx,   cy-14),(cx+4, cy-20), 2)

    elif sym == 3:
        # ── LEMON – ellipse + nub ──
        r = pygame.Rect(cx-13, cy-18, 26, 34)
        pygame.draw.ellipse(surf, (250,230,40), r)
        pygame.draw.ellipse(surf, C_DARK, r, 2)
        # nub top
        pygame.draw.circle(surf, (200,170,30), (cx, cy-18), 4)
        # highlight
        pygame.draw.ellipse(surf, (255,250,180), pygame.Rect(cx-6, cy-14, 8, 12))

    elif sym == 4:
        # ── STAR – 5-pointed ──
        pts = []
        for i in range(5):
            angle_out = math.radians(-90 + i*72)
            angle_in  = math.radians(-90 + i*72 + 36)
            pts.append((cx + 20*math.cos(angle_out), cy + 20*math.sin(angle_out)))
            pts.append((cx +  8*math.cos(angle_in),  cy +  8*math.sin(angle_in)))
        pygame.draw.polygon(surf, C_GOLD_LT, pts)
        pygame.draw.polygon(surf, C_DARK,    pts, 2)

    elif sym == 5:
        # ── BELL – dome + clapper ──
        # dome (top half circle + rect base)
        pygame.draw.circle(surf, (240,160,30), (cx, cy-4), 16)
        pygame.draw.rect(surf,   (240,160,30), pygame.Rect(cx-16, cy-4, 32, 12))
        pygame.draw.rect(surf,   C_DARK,       pygame.Rect(cx-16, cy-4, 32, 12), 1)
        pygame.draw.circle(surf, C_DARK, (cx, cy-4), 16, 2)
        # rim
        pygame.draw.rect(surf, (180,110,20), pygame.Rect(cx-18, cy+6, 36, 5),
                         border_radius=2)
        # clapper
        pygame.draw.circle(surf, C_DARK, (cx, cy+14), 4)

    elif sym == 6:
        # ── GRAPE – cluster of small circles ──
        grape_col = (170, 80, 255)
        dark_grape= (110, 40, 180)
        positions = [
            (cx,   cy-12),
            (cx-9, cy-4),
            (cx+9, cy-4),
            (cx-5, cy+6),
            (cx+5, cy+6),
            (cx,   cy+14),
        ]
        for gx,gy in positions:
            pygame.draw.circle(surf, grape_col, (gx,gy), 7)
            pygame.draw.circle(surf, dark_grape,(gx,gy), 7, 1)
            # highlight
            pygame.draw.circle(surf, (210,150,255),(gx-2,gy-2), 2)
        # stem
        pygame.draw.line(surf, (80,140,40),(cx, cy-19),(cx+5, cy-25), 2)


# ─────────────────────────────────────────────────────────────────────────────
#  Utility helpers
# ─────────────────────────────────────────────────────────────────────────────
def rr(surf, color, rect, radius, border=0, bcol=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and bcol:
        pygame.draw.rect(surf, bcol, rect, border, border_radius=radius)

def tc(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def lerp(a, b, t):
    return a + (b - a) * t

# ─────────────────────────────────────────────────────────────────────────────
#  Save / load
# ─────────────────────────────────────────────────────────────────────────────
def save_balance(bal):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump({"balance": bal}, f)
    except Exception:
        pass

def load_balance():
    try:
        with open(SAVE_PATH) as f:
            return int(json.load(f).get("balance", START_BAL))
    except Exception:
        return START_BAL

def wipe_save():
    try: os.remove(SAVE_PATH)
    except Exception: pass

# ─────────────────────────────────────────────────────────────────────────────
#  Coin particle
# ─────────────────────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, x, y):
        ang = random.uniform(0, math.pi*2)
        spd = random.uniform(90, 210)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(ang)*spd
        self.vy = math.sin(ang)*spd - random.uniform(60,130)
        self.life = 1.0
        self.r = random.randint(5, 9)

    def update(self, dt):
        self.x  += self.vx*dt
        self.y  += self.vy*dt
        self.vy += 420*dt
        self.life -= dt*1.9

    def draw(self, surf):
        if self.life <= 0: return
        a = max(0, int(self.life*255))
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (245,200,66,a), (self.r,self.r), self.r)
        surf.blit(s, (int(self.x-self.r), int(self.y-self.r)))

# ─────────────────────────────────────────────────────────────────────────────
#  Reel  – renders onto its own Surface for perfect clipping
# ─────────────────────────────────────────────────────────────────────────────
class Reel:
    STRIP = 20
    SYM_H = REEL_H

    def __init__(self, col):
        self.col     = col
        self.x       = REEL_X0 + col*(REEL_W + REEL_GAP)
        self.symbols = [random.randint(0, NUM_SYMS-1) for _ in range(self.STRIP)]
        self.scroll   = 0.0
        self.vel      = 0.0
        self.spinning = False
        self.braking  = False
        self.done     = False
        # dedicated surface – exact reel window size
        self.surf     = pygame.Surface((REEL_W, REEL_H))
        self._top_fade = self._make_fade(False)
        self._bot_fade = self._make_fade(True)

    @staticmethod
    def _make_fade(bottom):
        h = 30
        s = pygame.Surface((REEL_W, h), pygame.SRCALPHA)
        for i in range(h):
            a = int(220*(i/h)) if bottom else int(220*(1-i/h))
            pygame.draw.line(s, (C_DARK[0], C_DARK[1], C_DARK[2], a), (0,i),(REEL_W,i))
        return s

    def start(self, result_sym):
        self.symbols[2] = result_sym
        self.scroll     = 0.0
        self.vel        = 2400.0
        self.braking    = False
        self.done       = False
        self.spinning   = True
        self._target    = 2 * self.SYM_H

    def update(self, dt):
        if not self.spinning: return
        full = self.STRIP * self.SYM_H
        if not self.braking:
            self.scroll += self.vel * dt
            if self.scroll >= full * 0.58:
                self.braking      = True
                self._brake_t     = 0.0
                self._brake_start = self.scroll
        else:
            self._brake_t += dt
            t    = min(self._brake_t / 0.40, 1.0)
            ease = 1.0 - (1.0 - t)**3
            cycles = math.ceil(self._brake_start / full)
            final  = cycles * full + self._target
            if final <= self._brake_start: final += full
            self.scroll = lerp(self._brake_start, final, ease)
            if t >= 1.0:
                self.scroll   = final % full
                self.vel      = 0.0
                self.spinning = False
                self.done     = True

    def draw(self, dest):
        s = self.surf
        s.fill(C_REEL_BG)

        full        = self.STRIP * self.SYM_H
        scroll_wrap = self.scroll % full
        idx0        = int(scroll_wrap // self.SYM_H) % self.STRIP
        frac        = (scroll_wrap % self.SYM_H) / self.SYM_H

        # draw 2 adjacent symbols; each centred at its slot position
        for slot in range(2):
            sym = self.symbols[(idx0 + slot) % self.STRIP]
            cy  = int((slot - frac) * self.SYM_H + self.SYM_H // 2)
            if -self.SYM_H < cy < self.SYM_H + self.SYM_H // 2:
                draw_symbol(s, sym, REEL_W//2, cy)

        # fade overlays on top – contained entirely within the surface
        s.blit(self._top_fade, (0, 0))
        s.blit(self._bot_fade, (0, REEL_H - 30))

        # blit reel surface to screen
        dest.blit(s, (self.x, REEL_Y))
        # border drawn on screen so it sits cleanly over the surface edge
        pygame.draw.rect(dest, C_GOLD, (self.x, REEL_Y, REEL_W, REEL_H), 2, border_radius=6)

    def visible_sym(self):
        full = self.STRIP * self.SYM_H
        return self.symbols[int(round(self.scroll % full / self.SYM_H)) % self.STRIP]

# ─────────────────────────────────────────────────────────────────────────────
#  Lever
# ─────────────────────────────────────────────────────────────────────────────
class Lever:
    TX, TY, TW, TH = SCREEN_W-66, REEL_Y-18, 18, 140
    KR = 14

    def __init__(self):
        self.pull_t = 0.0
        self.pulling = self.returning = self.done = False

    @property
    def cx(self): return self.TX + self.TW//2

    @property
    def knob_y(self):
        e = self.pull_t**2 * (3 - 2*self.pull_t)
        return int((self.TY + self.KR + 4) + (self.TH - 2*self.KR - 8)*e)

    def pull(self):
        self.pulling = True; self.returning = self.done = False

    def update(self, dt):
        if self.pulling:
            self.pull_t = min(self.pull_t + dt*3.5, 1.0)
            if self.pull_t >= 1.0: self.pulling = False; self.returning = True
        elif self.returning:
            self.pull_t = max(self.pull_t - dt*2.5, 0.0)
            if self.pull_t <= 0.0: self.returning = False; self.done = True

    def hit_test(self, pos):
        return math.hypot(pos[0]-self.cx, pos[1]-self.knob_y) <= self.KR+10

    def draw(self, surf):
        rr(surf, C_MAHOGANY, pygame.Rect(self.TX, self.TY, self.TW, self.TH), 9, 2, C_GOLD)
        ky = self.knob_y
        bot = self.TY + self.TH
        pygame.draw.line(surf, C_GOLD, (self.cx, ky+self.KR), (self.cx, bot), 4)
        pygame.draw.circle(surf, C_RED_KNOB, (self.cx, ky), self.KR)
        pygame.draw.circle(surf, C_GOLD,     (self.cx, ky), self.KR, 2)
        pygame.draw.circle(surf, (230,80,80),(self.cx-4, ky-4), 4)
        rr(surf, C_GOLD, pygame.Rect(self.TX-9, bot, self.TW+18, 12), 4)
        lbl = F_SM.render("PULL", True, C_GOLD)
        surf.blit(lbl, lbl.get_rect(center=(self.cx, bot+22)))

# ─────────────────────────────────────────────────────────────────────────────
#  Button
# ─────────────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, text, cx, cy, w=155, h=36, danger=False):
        self.text = text; self.danger = danger
        self.rect = pygame.Rect(0,0,w,h); self.rect.center=(cx,cy)
        self.hovered = False

    def draw(self, surf):
        base = (180,40,40) if self.danger else C_GOLD
        col  = (220,70,70) if (self.danger and self.hovered) else \
               (C_GOLD_LT if self.hovered else base)
        rr(surf, col, self.rect, 7)
        surf.blit(F_MED.render(self.text,True,C_DARK),
                  F_MED.render(self.text,True,C_DARK).get_rect(center=self.rect.center))

    def hover(self, pos):   self.hovered = self.rect.collidepoint(pos)
    def clicked(self, pos): return self.rect.collidepoint(pos)

# ─────────────────────────────────────────────────────────────────────────────
#  SlotGame
# ─────────────────────────────────────────────────────────────────────────────
class SlotGame:
    def __init__(self, balance=None):
        self.balance  = load_balance() if balance is None else balance
        self.reels    = [Reel(i) for i in range(3)]
        self.lever    = Lever()
        self.coins    = []
        self.msg      = "Click the lever to spin!"
        self.msg_col  = C_GOLD_LT
        self.win_line = False
        self.state    = "idle"
        self.outcome  = []
        self._dtimers  = [0.0]*3
        self._rstarted = [False]*3
        mid = SCREEN_W//2 - 28
        self.reset_btn   = Button("RESET",      mid-88, SCREEN_H-52, w=140, h=34, danger=True)
        self.restart_btn = Button("PLAY AGAIN", mid+58, SCREEN_H-52, w=150, h=34)

    def _save(self):  save_balance(self.balance)
    def _reset(self): wipe_save(); self.__init__(balance=START_BAL)

    def _pick(self):
        r = random.random()
        if r < 0.03: return [0,0,0]
        if r < 0.07: return [1,1,1]
        if r < 0.13: return [2,2,2]
        if r < 0.18: return [3,3,3]
        if r < 0.24: return [4,4,4]
        if r < 0.34:
            sym = random.choice(list(PAIR_SYMS))
            res = [sym,sym,sym]
            res[random.randint(0,2)] = random.choice([s for s in range(NUM_SYMS) if s!=sym])
            return res
        while True:
            s = [random.randint(0,NUM_SYMS-1) for _ in range(3)]
            if len(set(s))==3: return s

    def _calc_win(self):
        k = tuple(self.outcome)
        if k in PAYOUTS: return PAYOUTS[k]
        c = {}
        for s in self.outcome: c[s]=c.get(s,0)+1
        for s in PAIR_SYMS:
            if c.get(s,0)>=2: return 5
        return 0

    def spin(self):
        if self.state != "idle": return
        if self.balance < BET:
            self.msg, self.msg_col = "Out of money!", C_RED_LOSE; return
        self.balance -= BET
        self.outcome  = self._pick()
        self.win_line = False
        self.msg      = ""
        self.state    = "lever"
        self.lever.pull()
        self._dtimers  = [0.0]*3
        self._rstarted = [False]*3

    def update(self, dt):
        self.lever.update(dt)
        for c in self.coins[:]:
            c.update(dt)
            if c.life <= 0: self.coins.remove(c)

        if self.state == "lever" and self.lever.pull_t >= 0.5:
            self.state = "spin_delay"

        if self.state == "spin_delay":
            all_go = True
            for i in range(3):
                if not self._rstarted[i]:
                    self._dtimers[i] += dt
                    if self._dtimers[i] >= SPIN_DELAYS[i]:
                        self.reels[i].start(self.outcome[i]); self._rstarted[i]=True
                    else: all_go = False
            if all_go: self.state = "spinning"

        if self.state == "spinning":
            for r in self.reels: r.update(dt)
            if all(r.done for r in self.reels): self._resolve()

    def _resolve(self):
        win = self._calc_win()
        self.balance += win
        self._save()
        if win > 0:
            self.win_line = True
            n = 24 if win>=50 else (12 if win>=20 else 6)
            cx,cy = SCREEN_W//2, REEL_Y+REEL_H//2
            self.coins = [Coin(cx+random.randint(-80,80),cy) for _ in range(n)]
            self.msg   = f"JACKPOT!  +${win}" if win==100 else \
                         f"BIG WIN!  +${win}" if win>=20  else f"You won ${win}!"
            self.msg_col = C_GREEN_WIN
        else:
            self.msg, self.msg_col = "No luck this time.", C_RED_LOSE
        self.state = "gameover" if self.balance < BET else "idle"

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        screen.fill(C_BG)
        body = pygame.Rect(30, 60, SCREEN_W-96, SCREEN_H-120)
        rr(screen, C_MAHOGANY, body, 18, 3, C_GOLD)
        rr(screen, C_PANEL, body.inflate(-10,-10), 14)

        tc(screen,"LUCKY  7s",        F_TITLE, C_GOLD_LT, SCREEN_W//2-28, 94)
        tc(screen,"D G T   E D I T I O N", F_SUB, C_GOLD, SCREEN_W//2-28, 120)

        for r in self.reels: r.draw(screen)

        if self.win_line:
            my = REEL_Y + REEL_H//2
            wl = pygame.Surface((3*REEL_W+2*REEL_GAP+8, 3), pygame.SRCALPHA)
            wl.fill((255,60,60,200))
            screen.blit(wl, (REEL_X0-4, my-1))

        hy = REEL_Y + REEL_H + 16
        for rect,lbl,val,vc in [
            (pygame.Rect(REEL_X0,     hy,130,52),"BALANCE",  f"${self.balance}",C_GOLD_LT),
            (pygame.Rect(REEL_X0+140, hy,130,52),"COST/PULL",f"${BET}",         C_GRAY),
        ]:
            rr(screen, C_DARK, rect, 8, 1, C_GOLD)
            tc(screen,lbl,F_SM, C_GOLD,rect.centerx,hy+14)
            tc(screen,val,F_BIG,vc,   rect.centerx,hy+36)

        if self.msg:
            tc(screen, self.msg, F_MED, self.msg_col, SCREEN_W//2-28, REEL_Y+REEL_H+84)

        self.lever.draw(screen)
        for c in self.coins: c.draw(screen)
        self._draw_payouts()
        self.reset_btn.draw(screen)

        if self.state == "gameover":
            ov = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,165)); screen.blit(ov,(0,0))
            tc(screen,"GAME  OVER",    F_TITLE,C_RED_LOSE,SCREEN_W//2,SCREEN_H//2-44)
            tc(screen,"Out of money!", F_MED,  C_GRAY,    SCREEN_W//2,SCREEN_H//2)
            self.restart_btn.draw(screen)

        pygame.display.flip()

    def _draw_payouts(self):
        py = REEL_Y + REEL_H + 108
        tc(screen, "─── PAYOUTS ───", F_SM, C_GOLD, SCREEN_W//2-28, py)
        lx, rx = REEL_X0, REEL_X0+265
        for i,(syms,pay) in enumerate(PAYOUT_ROWS):
            ry = py + 18 + i*17
            screen.blit(F_SM.render(syms,True,C_GOLD_LT),
                        F_SM.render(syms,True,C_GOLD_LT).get_rect(midleft=(lx,ry)))
            screen.blit(F_SM.render(pay, True,C_GOLD),
                        F_SM.render(pay, True,C_GOLD).get_rect(midright=(rx,ry)))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            p = event.pos
            if self.reset_btn.clicked(p): self._reset(); return
            if self.state == "gameover":
                if self.restart_btn.clicked(p):
                    bal = self.balance; self.__init__(balance=bal)
            elif self.state == "idle":
                if self.lever.hit_test(p): self.spin()
        elif event.type == pygame.MOUSEMOTION:
            self.reset_btn.hover(event.pos)
            self.restart_btn.hover(event.pos)

# ─────────────────────────────────────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    game = SlotGame()
    while True:
        dt = min(clock.tick(FPS)/1000.0, 0.05)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            game.handle(ev)
        game.update(dt)
        game.draw()

if __name__ == "__main__":
    main()