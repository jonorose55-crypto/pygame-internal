"""
Lucky 7s DGT Edition
Jono Rose Year 11 DGT Internal Assessment Casino Slot Machine Game
Casino game that simulates the good of actual slots with a game version.

Current version achieved/!MERIT!/excellence
"""

import pygame, random, math, sys, json, os


# =============================================================================
# Setup code
# =============================================================================

pygame.init()
SW, SH = 520, 700
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Lucky 7s – DGT Edition") # Name of the casion slot machine game
clock  = pygame.time.Clock()
FPS    = 60

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dgt_accounts.json")

BG        = (10, 20, 10)
ATM_BODY  = (20, 35, 20)
ATM_TRIM  = (40, 180, 40)
ATM_DIM   = (20, 100, 20)
SCREEN_BG = (0, 20, 0)
SCREEN_FG = (80, 255, 80)
SCREEN_DIM= (30, 120, 30)
RED_C     = (255, 60, 60)
AMBER     = (255, 180, 30)
WHITE     = (255, 255, 255)
GRAY      = (140, 140, 140)

C_BG      = (18,  8,  3)
C_MAH     = (42, 26, 14)
C_PANEL   = (30, 18,  8)
C_GOLD    = (201,147, 58)
C_GOLD_LT = (245,200, 66)
C_DARK    = (13,  7,  5)
C_REEL_BG = (245,240,228)
C_WIN     = (80, 255,136)
C_LOSE    = (255, 80, 80)
C_KNOB    = (200, 16, 16)

def sf(name, sz, bold=False):
    try:    return pygame.font.SysFont(name, sz, bold=bold)
    except: return pygame.font.Font(None, sz)

F_ATM_TITLE = sf("Courier New", 28, bold=True)
F_ATM_MED   = sf("Courier New", 18, bold=True)
F_ATM_SM    = sf("Courier New", 14)
F_ATM_XS    = sf("Courier New", 11)
F_TITLE     = sf("Georgia",     34, bold=True)
F_SUB       = sf("Courier New", 13)
F_BIG       = sf("Courier New", 20, bold=True)
F_MED       = sf("Courier New", 15)
F_SM        = sf("Courier New", 12)
F_7         = sf("Georgia",     34, bold=True)

SYM_BG = [
    (200,40,40),(50,160,220),(200,50,60),
    (210,185,40),(210,185,40),(210,120,30),(130,60,210),
]
NUM_SYMS = 7

WIN_MULT  = {(0,0,0):20,(1,1,1):10,(2,2,2):4,(3,3,3):3,(4,4,4):2}
PAIR_SYMS = {2, 4}
PAYOUT_ROWS = [
    ("7  7  7",   "x20 bet  JACKPOT"),
    ("Di Di Di",  "x10 bet"),
    ("Ch Ch Ch",  "x4  bet"),
    ("Le Le Le",  "x3  bet"),
    ("St St St",  "x2  bet"),
    ("Ch/St pair","x1  bet"),
]

RW, RH, RG = 90, 110, 10
RY  = 185
RX0 = (SW - (3*RW + 2*RG)) // 2
SPIN_DELAYS = [0.0, 0.22, 0.44]


# =============================================================================
#  Utility
# =============================================================================

def load_accounts():
    try:
        with open(SAVE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def save_accounts(accs):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(accs, f, indent=2)
    except Exception:
        pass

def rr(surf, col, rect, rad, bw=0, bc=None):
    pygame.draw.rect(surf, col, rect, border_radius=rad)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=rad)

def tc(surf, txt, font, col, cx, cy):
    img = font.render(txt, True, col)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def lerp(a, b, t):
    return a + (b - a) * t


# =============================================================================
#  SYMBOL DRAWING  (See below comment)
# =============================================================================

def draw_sym(surf, sym, cx, cy, r=28):
    bg = SYM_BG[sym]
    pygame.draw.circle(surf, bg,    (cx, cy), r)
    pygame.draw.circle(surf, C_DARK,(cx, cy), r, 2)
    if sym == 0:
        img = F_7.render("7", True, C_GOLD_LT)
        surf.blit(img, img.get_rect(center=(cx, cy)))
    elif sym == 1:
        s=18; pts=[(cx,cy-s),(cx+s,cy),(cx,cy+s),(cx-s,cy)]
        pygame.draw.polygon(surf, WHITE, pts)
        pygame.draw.polygon(surf, C_DARK, pts, 2)
        s2=8
        pygame.draw.polygon(surf,(180,230,255),[(cx,cy-s2),(cx+s2,cy),(cx,cy+s2),(cx-s2,cy)])
    elif sym == 2:
        pygame.draw.circle(surf,(210,30,30),(cx-8,cy+6),9)
        pygame.draw.circle(surf,C_DARK,(cx-8,cy+6),9,1)
        pygame.draw.circle(surf,(240,50,50),(cx+8,cy+6),9)
        pygame.draw.circle(surf,C_DARK,(cx+8,cy+6),9,1)
        pygame.draw.line(surf,(60,150,40),(cx-8,cy-3),(cx,cy-14),2)
        pygame.draw.line(surf,(60,150,40),(cx+8,cy-3),(cx,cy-14),2)
        pygame.draw.line(surf,(60,150,40),(cx,cy-14),(cx+4,cy-20),2)
    elif sym == 3:
        er = pygame.Rect(cx-13, cy-18, 26, 34)
        pygame.draw.ellipse(surf,(250,230,40),er)
        pygame.draw.ellipse(surf,C_DARK,er,2)
        pygame.draw.circle(surf,(200,170,30),(cx,cy-18),4)
        pygame.draw.ellipse(surf,(255,250,180),pygame.Rect(cx-6,cy-14,8,12))
    elif sym == 4:
        pts=[]
        for i in range(5):
            ao=math.radians(-90+i*72); ai=math.radians(-90+i*72+36)
            pts.append((cx+20*math.cos(ao), cy+20*math.sin(ao)))
            pts.append((cx+ 8*math.cos(ai), cy+ 8*math.sin(ai)))
        pygame.draw.polygon(surf, C_GOLD_LT, pts)
        pygame.draw.polygon(surf, C_DARK, pts, 2)
    elif sym == 5:
        pygame.draw.circle(surf,(240,160,30),(cx,cy-4),16)
        pygame.draw.rect(surf,(240,160,30),pygame.Rect(cx-16,cy-4,32,12))
        pygame.draw.rect(surf,C_DARK,pygame.Rect(cx-16,cy-4,32,12),1)
        pygame.draw.circle(surf,C_DARK,(cx,cy-4),16,2)
        pygame.draw.rect(surf,(180,110,20),pygame.Rect(cx-18,cy+6,36,5),border_radius=2)
        pygame.draw.circle(surf,C_DARK,(cx,cy+14),4)
    elif sym == 6:
        gc=(170,80,255); dc=(110,40,180)
        for gx,gy in [(cx,cy-12),(cx-9,cy-4),(cx+9,cy-4),(cx-5,cy+6),(cx+5,cy+6),(cx,cy+14)]:
            pygame.draw.circle(surf, gc, (gx,gy), 7)
            pygame.draw.circle(surf, dc, (gx,gy), 7, 1)
            pygame.draw.circle(surf,(210,150,255),(gx-2,gy-2),2)
        pygame.draw.line(surf,(80,140,40),(cx,cy-19),(cx+5,cy-25),2)


# =============================================================================
#  Pygame drawing (Ai assisted becuase we didnt learn how to code pygame drawings)
# =============================================================================

class Coin:
    def __init__(self, x, y):
        a = random.uniform(0, math.pi*2)
        sp = random.uniform(90, 210)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(a)*sp
        self.vy = math.sin(a)*sp - random.uniform(60, 130)
        self.life = 1.0
        self.r = random.randint(5, 9)

    def update(self, dt):
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += 420*dt;    self.life -= dt*1.9

    def draw(self, surf):
        if self.life <= 0: return
        a = max(0, int(self.life*255))
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (245,200,66,a), (self.r,self.r), self.r)
        surf.blit(s, (int(self.x-self.r), int(self.y-self.r)))


class Reel:
    STRIP = 20
    SYM_H = RH

    def __init__(self, col):
        self.col = col
        self.x   = RX0 + col*(RW + RG)
        self.symbols = [random.randint(0, NUM_SYMS-1) for _ in range(self.STRIP)]
        self.scroll = 0.0; self.vel = 0.0
        self.spinning = False; self.braking = False; self.done = False
        self.surf = pygame.Surface((RW, RH))
        self._tf = self._fade(False)
        self._bf = self._fade(True)

    @staticmethod
    def _fade(bot):
        h = 30
        s = pygame.Surface((RW, h), pygame.SRCALPHA)
        for i in range(h):
            a = int(220*(i/h)) if bot else int(220*(1-i/h))
            pygame.draw.line(s, (C_DARK[0],C_DARK[1],C_DARK[2],a), (0,i), (RW,i))
        return s

    def start(self, res):
        self.symbols[2] = res
        self.scroll = 0.0; self.vel = 2400.0
        self.braking = False; self.done = False; self.spinning = True
        self._target = 2 * self.SYM_H

    def update(self, dt):
        if not self.spinning: return
        full = self.STRIP * self.SYM_H
        if not self.braking:
            self.scroll += self.vel * dt
            if self.scroll >= full * 0.58:
                self.braking = True; self._bt = 0.0; self._bs = self.scroll
        else:
            self._bt += dt
            t    = min(self._bt / 0.40, 1.0)
            ease = 1 - (1-t)**3
            cyc  = math.ceil(self._bs / full)
            fin  = cyc * full + self._target
            if fin <= self._bs: fin += full
            self.scroll = lerp(self._bs, fin, ease)
            if t >= 1.0:
                self.scroll   = fin % full
                self.vel      = 0.0
                self.spinning = False
                self.done     = True

    def draw(self, dest):
        s = self.surf; s.fill(C_REEL_BG)
        full = self.STRIP * self.SYM_H
        sw   = self.scroll % full
        i0   = int(sw // self.SYM_H) % self.STRIP
        frac = (sw % self.SYM_H) / self.SYM_H
        for slot in range(2):
            sym = self.symbols[(i0+slot) % self.STRIP]
            cy  = int((slot - frac) * self.SYM_H + self.SYM_H // 2)
            if -self.SYM_H < cy < self.SYM_H + self.SYM_H // 2:
                draw_sym(s, sym, RW//2, cy)
        s.blit(self._tf, (0, 0))
        s.blit(self._bf, (0, RH-30))
        dest.blit(s, (self.x, RY))
        pygame.draw.rect(dest, C_GOLD, (self.x, RY, RW, RH), 2, border_radius=6)

    def visible(self):
        full = self.STRIP * self.SYM_H
        return self.symbols[int(round(self.scroll % full / self.SYM_H)) % self.STRIP]


class Lever:
    TX, TY, TW, TH = SW-66, RY-18, 18, 140
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

    def pull(self): self.pulling = True; self.returning = self.done = False

    def update(self, dt):
        if self.pulling:
            self.pull_t = min(self.pull_t + dt*3.5, 1.0)
            if self.pull_t >= 1.0: self.pulling = False; self.returning = True
        elif self.returning:
            self.pull_t = max(self.pull_t - dt*2.5, 0.0)
            if self.pull_t <= 0.0: self.returning = False; self.done = True

    def hit(self, pos):
        return math.hypot(pos[0]-self.cx, pos[1]-self.knob_y) <= self.KR+10

    def draw(self, surf):
        rr(surf, C_MAH, pygame.Rect(self.TX,self.TY,self.TW,self.TH), 9, 2, C_GOLD)
        ky  = self.knob_y
        bot = self.TY + self.TH
        pygame.draw.line(surf, C_GOLD, (self.cx, ky+self.KR), (self.cx, bot), 4)
        pygame.draw.circle(surf, C_KNOB, (self.cx, ky), self.KR)
        pygame.draw.circle(surf, C_GOLD, (self.cx, ky), self.KR, 2)
        pygame.draw.circle(surf, (230,80,80), (self.cx-4, ky-4), 4)
        rr(surf, C_GOLD, pygame.Rect(self.TX-9, bot, self.TW+18, 12), 4)
        lbl = F_SM.render("PULL", True, C_GOLD)
        surf.blit(lbl, lbl.get_rect(center=(self.cx, bot+22)))


class Btn:
    def __init__(self, text, cx, cy, w=150, h=34, danger=False, gold=False):
        self.text = text; self.danger = danger; self.gold = gold
        self.rect = pygame.Rect(0,0,w,h); self.rect.center = (cx, cy)
        self.hov  = False

    def draw(self, surf):
        if self.danger:
            col = (220,70,70) if self.hov else (180,40,40)
        elif self.gold:
            col = C_GOLD_LT if self.hov else C_GOLD
        else:
            col = (100,100,100) if self.hov else (60,60,60)
        rr(surf, col, self.rect, 7)
        img = F_MED.render(self.text, True, C_DARK)
        surf.blit(img, img.get_rect(center=self.rect.center))

    def hover_check(self, pos): self.hov = self.rect.collidepoint(pos)
    def clicked(self, pos):     return self.rect.collidepoint(pos)


class BetInput:
    def __init__(self, x, y, w=80, h=28):
        self.rect   = pygame.Rect(x, y, w, h)
        self.active = False
        self.buf    = "5"
        self.cur_t  = 0.0

    @property
    def value(self):
        try:    return max(0.01, float(self.buf))
        except: return 1.0

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.buf = self.buf[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.active = False
            elif event.unicode in "0123456789." and len(self.buf) < 8:
                self.buf += event.unicode

    def update(self, dt):
        self.cur_t += dt
        if self.cur_t > 1.0: self.cur_t = 0.0

    def draw(self, surf):
        col  = C_GOLD_LT if self.active else C_GOLD
        rr(surf, C_DARK, self.rect, 5, 1, col)
        blink = self.cur_t < 0.5 and self.active
        disp  = "$" + self.buf + ("|" if blink else "")
        img   = F_SM.render(disp, True, col)
        surf.blit(img, img.get_rect(center=self.rect.center))


# =============================================================================
#  ATM aka the start screen of the game with login features and account saves stuff like that
#  This feature is apart of the atm screen because it is the first thing you see when you start the game. 
#  It is where you login to your account and access the slot machine game.
#  It also has the account saving features so it made sense to put it here.
# =============================================================================

class ATMScreen:
    def __init__(self, accounts):
        self.accounts   = accounts
        self.state      = "welcome"
        self.username   = ""
        self.input_buf  = ""
        self.msg        = ""
        self.msg_t      = 0.0
        self.cur_t      = 0.0
        self.last_co    = None
        self.on_play    = None

    def set_msg(self, m, t=3.0): self.msg = m; self.msg_t = t

    def update(self, dt):
        self.cur_t += dt
        if self.cur_t > 1.0: self.cur_t = 0.0
        if self.msg_t > 0: self.msg_t -= dt

    def handle(self, event):
        if event.type != pygame.KEYDOWN: return
        k = event.key

        if self.state == "welcome":
            if k == pygame.K_RETURN:
                self.state = "username"; self.input_buf = ""
            return

        if self.state == "username":
            if k == pygame.K_RETURN:
                u = self.input_buf.strip().upper()
                if not u: return
                self.username = u
                if u not in self.accounts:
                    self.accounts[u] = {"cash": 50.0}
                    save_accounts(self.accounts)
                    self.state = "newuser"
                else:
                    self.state = "mainmenu"
                self.input_buf = ""
            elif k == pygame.K_BACKSPACE:
                self.input_buf = self.input_buf[:-1]
            elif event.unicode.isprintable() and len(self.input_buf) < 16:
                self.input_buf += event.unicode
            return

        if self.state == "newuser":
            if k == pygame.K_RETURN: self.state = "mainmenu"
            return

        if self.state == "mainmenu":
            acc  = self.accounts.get(self.username, {})
            cash = acc.get("cash", 0.0)
            if k == pygame.K_1:
                if cash <= 0: self.set_msg("NO FUNDS  –  ACCOUNT IS EMPTY"); return
                if self.on_play: self.on_play(self.username, cash)
            elif k == pygame.K_2:
                self.accounts[self.username]["cash"] = 50.0
                save_accounts(self.accounts)
                self.set_msg("ACCOUNT RESET TO $50.00")
            elif k == pygame.K_3:
                self.username = ""; self.state = "username"; self.input_buf = ""
            return

    def cashout(self, username, amount):
        if username in self.accounts:
            self.accounts[username]["cash"] = round(
                self.accounts[username].get("cash", 0) + amount, 2)
            save_accounts(self.accounts)
        self.last_co  = (username, amount)
        self.username = username
        self.state    = "mainmenu"

    def _atm_shell(self):
        screen.fill(BG)
        rr(screen, ATM_BODY, pygame.Rect(20,20,SW-40,SH-40), 16, 3, ATM_TRIM)
        rr(screen, (5,15,5), pygame.Rect(60,60,SW-120,SH-200), 8, 2, ATM_DIM)
        rr(screen, SCREEN_BG, pygame.Rect(70,70,SW-140,SH-220), 6)
        rr(screen, (0,60,0), pygame.Rect(20,20,SW-40,36), 16)
        tc(screen, "D G T   B A N K I N G   S Y S T E M S", F_ATM_XS, ATM_TRIM, SW//2, 38)
        rr(screen, ATM_DIM, pygame.Rect(SW//2-50, SH-100, 100, 12), 4, 1, ATM_TRIM)
        tc(screen, "INSERT CARD", F_ATM_XS, ATM_DIM, SW//2, SH-82)
        for lx in (35, SW-35):
            pygame.draw.circle(screen, ATM_TRIM, (lx, SH//2), 6)
            pygame.draw.circle(screen, (0,80,0),  (lx, SH//2+30), 4)
            pygame.draw.circle(screen, (0,80,0),  (lx, SH//2-30), 4)

    def draw(self):
        self._atm_shell()
        sr = pygame.Rect(70,70,SW-140,SH-220)
        cx = sr.centerx; y = sr.y + 18

        if self.state == "welcome":
            tc(screen, "DGT EDITION",        F_ATM_TITLE, SCREEN_FG, cx, y+12)
            tc(screen, "LUCKY  7s",           F_ATM_TITLE, AMBER,     cx, y+50)
            tc(screen, "─"*28,               F_ATM_SM,   SCREEN_DIM, cx, y+88)
            tc(screen, "CASINO  TERMINAL",   F_ATM_MED,  SCREEN_FG,  cx, y+112)
            tc(screen, "─"*28,               F_ATM_SM,   SCREEN_DIM, cx, y+134)
            blink = "PRESS  ENTER  TO  BEGIN" if self.cur_t < 0.5 else ""
            tc(screen, blink, F_ATM_SM, AMBER, cx, y+164)
            if self.last_co:
                u, a = self.last_co
                tc(screen, f"CASHED OUT: {u}  +${a:.2f}", F_ATM_XS, C_WIN, cx, y+200)
            tc(screen, "v1.0  //  DGT SYSTEMS", F_ATM_XS, SCREEN_DIM, cx, sr.bottom-20)

        elif self.state == "username":
            tc(screen, "ACCOUNT LOGIN",  F_ATM_MED, SCREEN_FG, cx, y+10)
            tc(screen, "─"*28,          F_ATM_SM,  SCREEN_DIM, cx, y+36)
            tc(screen, "ENTER USERNAME:",F_ATM_SM,  SCREEN_FG,  cx, y+72)
            rr(screen, SCREEN_BG, pygame.Rect(cx-100,y+90,200,30), 4, 1, SCREEN_FG)
            cur = "_" if self.cur_t < 0.5 else " "
            tc(screen, self.input_buf+cur, F_ATM_MED, AMBER, cx, y+105)
            tc(screen, "[ENTER] CONFIRM", F_ATM_XS, SCREEN_DIM, cx, y+142)
            if self.msg_t > 0:
                tc(screen, self.msg, F_ATM_SM, RED_C, cx, y+168)

        elif self.state == "newuser":
            tc(screen, "NEW ACCOUNT",     F_ATM_MED,   AMBER,      cx, y+12)
            tc(screen, "─"*28,           F_ATM_SM,    SCREEN_DIM,  cx, y+36)
            tc(screen, "WELCOME,",        F_ATM_SM,    SCREEN_FG,   cx, y+72)
            tc(screen, self.username.upper(), F_ATM_TITLE, AMBER,   cx, y+104)
            tc(screen, "ACCOUNT CREATED", F_ATM_SM,    SCREEN_FG,   cx, y+142)
            tc(screen, "STARTING BALANCE:  $50.00", F_ATM_SM, SCREEN_FG, cx, y+164)
            tc(screen, "[ENTER] CONTINUE",F_ATM_XS,    SCREEN_DIM,  cx, y+202)

        elif self.state == "mainmenu":
            acc  = self.accounts.get(self.username, {})
            cash = acc.get("cash", 0.0)
            tc(screen, self.username.upper()[:14], F_ATM_MED,   AMBER,      cx, y+8)
            tc(screen, "─"*28,                    F_ATM_SM,    SCREEN_DIM,  cx, y+30)
            tc(screen, "CASH BALANCE",             F_ATM_XS,    SCREEN_DIM,  cx, y+52)
            tc(screen, f"${cash:.2f}",             F_ATM_TITLE, SCREEN_FG,   cx, y+76)
            tc(screen, "─"*28,                    F_ATM_SM,    SCREEN_DIM,  cx, y+104)
            items = [
                ("[1] PLAY SLOTS",          SCREEN_FG),
                ("[2] RESET ACCOUNT ($50)", RED_C),
                ("[3] LOG OUT",             SCREEN_DIM),
            ]
            for i,(txt,col) in enumerate(items):
                tc(screen, txt, F_ATM_SM, col, cx, y+128+i*26)
            if self.last_co and self.last_co[0] == self.username:
                _, a = self.last_co
                tc(screen, f"LAST CASHOUT: +${a:.2f}", F_ATM_XS, C_WIN, cx, y+214)
                self.last_co = None
            if self.msg_t > 0:
                tc(screen, self.msg, F_ATM_SM, AMBER, cx, y+242)

        pygame.display.flip()


# =============================================================================
#  Load screen (a part of the start screen) the pre-slot machine game.
#  Yet again a part of the atm function and start sceeen area, this was build after the main slot game.
# =============================================================================

class LoadScreen:
    def __init__(self, username, cash, on_confirm, on_back):
        self.username   = username
        self.cash       = cash
        self.on_confirm = on_confirm
        self.on_back    = on_back
        self.buf        = ""
        self.msg        = ""
        self.msg_t      = 0.0
        self.cur_t      = 0.0

    def set_msg(self, m): self.msg = m; self.msg_t = 2.5

    def update(self, dt):
        self.cur_t += dt
        if self.cur_t > 1.0: self.cur_t = 0.0
        if self.msg_t > 0: self.msg_t -= dt

    def handle(self, event):
        if event.type != pygame.KEYDOWN: return
        k = event.key
        if k == pygame.K_ESCAPE: self.on_back(); return
        if k == pygame.K_RETURN:
            try:
                amt = float(self.buf)
                if amt <= 0 or amt > self.cash: raise ValueError
                self.on_confirm(amt)
            except:
                self.set_msg(f"ENTER 0.01 TO {self.cash:.2f}")
            return
        if k == pygame.K_BACKSPACE:
            self.buf = self.buf[:-1]
        elif event.unicode in "0123456789." and len(self.buf) < 10:
            self.buf += event.unicode

    def draw(self):
        screen.fill(BG)
        rr(screen, ATM_BODY, pygame.Rect(20,20,SW-40,SH-40), 16, 3, ATM_TRIM)
        rr(screen, (5,15,5), pygame.Rect(60,60,SW-120,SH-200), 8, 2, ATM_DIM)
        rr(screen, SCREEN_BG, pygame.Rect(70,70,SW-140,SH-220), 6)
        rr(screen, (0,60,0), pygame.Rect(20,20,SW-40,36), 16)
        tc(screen, "D G T   B A N K I N G   S Y S T E M S", F_ATM_XS, ATM_TRIM, SW//2, 38)
        sr = pygame.Rect(70,70,SW-140,SH-220)
        cx = sr.centerx; y = sr.y+18
        tc(screen, "LOAD MACHINE CREDITS", F_ATM_MED, SCREEN_FG,  cx, y+10)
        tc(screen, "─"*28,                F_ATM_SM,  SCREEN_DIM,  cx, y+34)
        tc(screen, f"USER:  {self.username.upper()}", F_ATM_XS, SCREEN_FG, cx, y+56)
        tc(screen, f"AVAILABLE: ${self.cash:.2f}",    F_ATM_SM,  SCREEN_FG, cx, y+78)
        tc(screen, "HOW MUCH TO LOAD INTO",F_ATM_SM,  SCREEN_FG,  cx, y+108)
        tc(screen, "THE MACHINE?",         F_ATM_SM,  SCREEN_FG,  cx, y+128)
        rr(screen, SCREEN_BG, pygame.Rect(cx-90,y+150,180,30), 4, 1, SCREEN_FG)
        cur = "_" if self.cur_t < 0.5 else " "
        tc(screen, "$"+self.buf+cur, F_ATM_MED, AMBER, cx, y+165)
        tc(screen, "[ENTER] INSERT CREDITS", F_ATM_XS, SCREEN_DIM, cx, y+196)
        tc(screen, "[ESC]   GO BACK",        F_ATM_XS, SCREEN_DIM, cx, y+214)
        if self.msg_t > 0:
            tc(screen, self.msg, F_ATM_SM, RED_C, cx, y+240)
        pygame.display.flip()


# =============================================================================
#  Proper slot machiene game with balance and spinning icons as if it were a proper casino slot machine (with Dgt branding)
#  This is the First aspects of the game that I made, it is the actual slot so I made the program around this design.
#  It has the spinning reels, the lever, the bet input, and the cashout button. It also has the win calculation.
# =============================================================================

class SlotGame:
    def __init__(self, username, start_balance, on_cashout):
        self.username   = username
        self.balance    = round(start_balance, 2)
        self.on_cashout = on_cashout
        self.reels      = [Reel(i) for i in range(3)]
        self.lever      = Lever()
        self.coins      = []
        self.msg        = "Click the lever to spin!"
        self.msg_col    = C_GOLD_LT
        self.win_line   = False
        self.state      = "idle"
        self.outcome    = []
        self._dtimers   = [0.0]*3
        self._rstarted  = [False]*3
        self._last_bet  = 5.0
        self.bet_inp    = BetInput(RX0+150, RY+RH+24, 80, 28)
        self.bet_inp.buf= "5"
        self.cashout_btn= Btn("CASH OUT", SW-100, SH-52, 150, 34, gold=True)

    def _bet(self):
        return min(self.bet_inp.value, self.balance)

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
            if len(set(s)) == 3: return s

    def _calc_win(self, bet):
        k = tuple(self.outcome)
        if k in WIN_MULT: return round(bet * WIN_MULT[k], 2)
        c = {}
        for s in self.outcome: c[s] = c.get(s,0)+1
        for s in PAIR_SYMS:
            if c.get(s,0) >= 2: return round(bet, 2)
        return 0

    def spin(self):
        if self.state != "idle": return
        bet = self._bet()
        if bet <= 0 or self.balance < 0.01:
            self.msg, self.msg_col = "Not enough balance!", C_LOSE; return
        self._last_bet  = bet
        self.balance    = round(self.balance - bet, 2)
        self.outcome    = self._pick()
        self.win_line   = False
        self.msg        = ""
        self.state      = "lever"
        self.lever.pull()
        self._dtimers   = [0.0]*3
        self._rstarted  = [False]*3

    def update(self, dt):
        self.lever.update(dt)
        self.bet_inp.update(dt)
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
                        self.reels[i].start(self.outcome[i]); self._rstarted[i] = True
                    else: all_go = False
            if all_go: self.state = "spinning"
        if self.state == "spinning":
            for r in self.reels: r.update(dt)
            if all(r.done for r in self.reels): self._resolve()

    def _resolve(self):
        bet = self._last_bet
        win = self._calc_win(bet)
        self.balance = round(self.balance + win, 2)
        if win > 0:
            self.win_line = True
            n = 24 if win >= bet*10 else (12 if win >= bet*4 else 6)
            cx, cy = SW//2, RY+RH//2
            self.coins = [Coin(cx+random.randint(-80,80), cy) for _ in range(n)]
            if win >= bet*15:
                self.msg = f"JACKPOT! +${win:.2f}"
            elif win >= bet*4:
                self.msg = f"BIG WIN! +${win:.2f}"
            else:
                self.msg = f"Won  ${win:.2f}!"
            self.msg_col = C_WIN
        else:
            self.msg, self.msg_col = "No luck this time.", C_LOSE
        self.state = "broke" if self.balance < 0.01 else "idle"

    def draw(self):
        screen.fill(C_BG)
        body = pygame.Rect(30,60,SW-96,SH-120)
        rr(screen, C_MAH,   body, 18, 3, C_GOLD)
        rr(screen, C_PANEL, body.inflate(-10,-10), 14)
        tc(screen, "LUCKY  7s",             F_TITLE, C_GOLD_LT, SW//2-28, 94)
        tc(screen, "D G T   E D I T I O N", F_SUB,   C_GOLD,    SW//2-28, 120)
        uimg = F_SM.render(f"{self.username[:10]}  ${self.balance:.2f}", True, C_GOLD)
        screen.blit(uimg, uimg.get_rect(topright=(SW-72, 66)))
        for r in self.reels: r.draw(screen)
        if self.win_line:
            my = RY + RH//2
            wl = pygame.Surface((3*RW+2*RG+8, 3), pygame.SRCALPHA)
            wl.fill((255,60,60,200))
            screen.blit(wl, (RX0-4, my-1))
        hy = RY + RH + 16
        br = pygame.Rect(RX0, hy, 128, 52)
        rr(screen, C_DARK, br, 8, 1, C_GOLD)
        tc(screen, "BALANCE",              F_SM,  C_GOLD,    br.centerx, hy+14)
        tc(screen, f"${self.balance:.2f}", F_BIG, C_GOLD_LT, br.centerx, hy+36)
        blx = RX0+140
        tc(screen, "BET/SPIN", F_SM, C_GOLD, blx+40, hy+14)
        self.bet_inp.rect.topleft = (blx, hy+24)
        self.bet_inp.draw(screen)
        hint = F_SM.render("(click to edit)", True, (100,80,40))
        screen.blit(hint, (blx, hy+56))
        if self.msg:
            tc(screen, self.msg, F_MED, self.msg_col, SW//2-28, RY+RH+84)
        self.lever.draw(screen)
        for c in self.coins: c.draw(screen)
        self._draw_payouts()
        self.cashout_btn.draw(screen)
        if self.state == "broke":
            ov = pygame.Surface((SW,SH), pygame.SRCALPHA)
            ov.fill((0,0,0,170)); screen.blit(ov,(0,0))
            tc(screen, "OUT OF BALANCE",      F_TITLE, C_LOSE,        SW//2, SH//2-40)
            tc(screen, "Returning to ATM...", F_MED,   (200,200,200), SW//2, SH//2+10)
        pygame.display.flip()

    def _draw_payouts(self):
        py = RY + RH + 108
        tc(screen, "─── PAYOUTS ───", F_SM, C_GOLD, SW//2-28, py)
        lx, rx = RX0, RX0+265
        for i,(syms,pay) in enumerate(PAYOUT_ROWS):
            ry = py + 18 + i*17
            ai = F_SM.render(syms, True, C_GOLD_LT)
            bi = F_SM.render(pay,  True, C_GOLD)
            screen.blit(ai, ai.get_rect(midleft =(lx, ry)))
            screen.blit(bi, bi.get_rect(midright=(rx, ry)))

    def handle(self, event):
        self.bet_inp.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            p = event.pos
            if self.cashout_btn.clicked(p):
                self.on_cashout(self.username, self.balance); return
            if self.state == "broke":
                self.on_cashout(self.username, self.balance); return
            if self.state == "idle" and not self.bet_inp.active:
                if self.lever.hit(p): self.spin()
        elif event.type == pygame.MOUSEMOTION:
            self.cashout_btn.hover_check(event.pos)


# =============================================================================
#  MAIN LOOP
# =============================================================================

def main():
    accounts = load_accounts()
    atm      = ATMScreen(accounts)
    game     = None
    loader   = None
    scene    = "atm"

    def do_cashout(username, bal):
        nonlocal scene, game, loader
        atm.cashout(username, bal)
        game = None; loader = None; scene = "atm"

    def open_loader(username, cash):
        nonlocal scene, loader
        def on_confirm(amt):
            nonlocal scene, game, loader
            accounts[username]["cash"] = round(
                accounts[username].get("cash", 0) - amt, 2)
            save_accounts(accounts)
            game   = SlotGame(username, amt, do_cashout)
            loader = None
            scene  = "game"
        def on_back():
            nonlocal scene, loader
            loader = None; scene = "atm"
        loader = LoadScreen(username, cash, on_confirm, on_back)
        scene  = "load"

    atm.on_play = open_loader

    while True:
        dt = min(clock.tick(FPS)/1000.0, 0.05)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if scene == "game" and game:
                    do_cashout(game.username, game.balance)
                elif scene == "load":
                    loader = None; scene = "atm"
                else:
                    pygame.quit(); sys.exit()
            if scene == "atm":
                atm.handle(ev)
            elif scene == "load" and loader:
                loader.handle(ev)
            elif scene == "game" and game:
                game.handle(ev)

        if scene == "atm":
            atm.update(dt); atm.draw()
        elif scene == "load" and loader:
            loader.update(dt); loader.draw()
        elif scene == "game" and game:
            game.update(dt); game.draw()
            if game.state == "broke":
                pygame.time.wait(1800)
                do_cashout(game.username, game.balance)


if __name__ == "__main__":
    main()