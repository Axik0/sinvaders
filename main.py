import turtle as t
from PIL import Image, ImageTk
import random
import time

import obstacles as o
from auxfunc import *

COLORS6 = ["#cdb4db", "#ffc8dd", "#ffafcc", "#bde0fe", "#a2d2ff", "#8ecae6"]
# Global color palette
main_color = '#f0f3f5'
focus_color = '#fff0fb'
text_color_a = '#262626'
text_color_ina = '#848484'

# # Global font
# main_font = ("Helvetica", 16)

w = t.Screen()
w.setup(width=500, height=500, startx=500, starty=100)
w.title('Space Invaders')
# loads an icon file, resizes it with a help of PIL and transfers to an tkinter object underneath Screen class
icon = Image.open("images/icon.png")
icon = icon.resize((35, 35), Image.Resampling.LANCZOS)
icon = ImageTk.PhotoImage(icon)
w._root.iconphoto(False, icon)
# w.textinput("Player setup", "Enter your name:")
w.bgcolor(focus_color)

# center line of main hero ship
BC = -230


class Actor(t.RawTurtle):
    def __init__(self, hero=False):
        super().__init__(canvas=w)
        self.hideturtle()
        self.penup()
        self.shape("square")
        self.shapesize(1, 2)
        # distinguishes main hero from his enemies
        self.type = hero
        if self.type:
            # distinguishes main hero from his enemies
            self.goto(0, BC)
            w.onkeypress(lambda: self.forward(20), 'Right')
            w.onkeypress(lambda: self.backward(20), 'Left')
            w.onkeypress(lambda: self.attack(), 'space')
            w.listen()
        self.showturtle()
        # rockets are connected and thus accessible from their creators
        self.rocket = t.RawTurtle(w)
        self.rocket.hideturtle()
        self.rocket.penup()
        self.rocket.shape("circle")
        self.rocket.shapesize(0.1, 0.1)
        if self.type:
            self.rocket.color('#0096c7')
        else:
            self.rocket.color('#f72585')
        # rocket-related states
        self.reactive = False
        self.disposal = None

    def attack(self):
        # ONE ROCKET PER ACTOR PRINCIPLE
        # !!!!1 NEW TURTLE = 0.5s of TIME unless tracer =0, REUSE AND DON'T EVEN CREATE IT ON CALL!!!!
        if self.disposal:
            # reuse resetted rocket by external reload_rocket call
            self.rocket = self.disposal
            self.disposal = None
            self.init_rocket()
            self.rocket.showturtle()
            self.reactive = True
        elif not self.reactive:
            # set the rocket up near the actor
            self.init_rocket()
            self.rocket.showturtle()
            self.reactive = True
        # Continue using the rocket otherwise
        return self.rocket

    def dispose_rocket(self):
        # reinit (hide) rocket and only then dispose this way, otherwise it stays on canvas till its (random) turn
        self.init_rocket()
        self.disposal = self.rocket
        self.reactive = False

    def init_rocket(self):
        # hide first and then do everything else, an order matters when everything slows down
        self.rocket.hideturtle()
        # rocket turtle is created near its parent, no matter who is that
        if self.type:
            # distinguishes main hero from his enemies
            self.rocket.goto(self.xcor(), BC+10*(self.shapesize()[0]+self.rocket.shapesize()[0]))
            self.rocket.seth(90)
        else:
            self.rocket.goto(self.xcor(), self.ycor()-10*(self.shapesize()[0]+self.rocket.shapesize()[0]))
            self.rocket.seth(-90)


obs = o.Obstacle(window_size=(280, 370), grid_size=(9, 3))
# obs.getlog()
bar_turtles = {}


def place_bars(hide=True, skip=True):
    """This function calls an Obstacle class object and draws all the bars according to those parameters"""
    obs.load()
    # obs.getlog(True)
    cid = 0
    if skip:
        w.tracer(0)
    for lev in obs.bars:
        for coord in obs.bars[lev]:
            bar = Actor()
            global bar_turtles
            bar_turtles[coord] = bar
            if hide:
                bar.hideturtle()
                bar.speed(0)
            bar.penup()
            bar.shape('square')
            # no error, a stretch factor is perpendicular to the corresponding axis (depends of turtle's EAST heading!)
            bar.shapesize(obs.BAR_SEMI_HEIGHT / 10, obs.BAR_SEMI_WIDTH / 10)
            bar.goto(coord)
            bar.color(COLORS6[cid])
            if hide:
                bar.showturtle()
        cid += 1
        if skip:
            w.update()
    w.tracer(1)


def gen_edge(btd):
    # generates a dictionary of all potentially active items (=lowest not shielded)
    edge_t = {}
    for k, v in btd.items():
        if (k[0], k[1] - m.floor(obs.V_STEP)) not in btd:
            edge_t[k] = v
    return edge_t


STEP = 10
STEP_ER = STEP*0.5
# Limits of turtle (their centers) horizontal movement
bar_move_xlim = (-250+obs.SEP+obs.BAR_SEMI_WIDTH-obs.x_cor_range[0], 250-obs.BAR_SEMI_WIDTH-obs.x_cor_range[1])
# print(bar_move_xlim)


def bond_move(sgn):
    """multiple enemies move together as a whole within bar_move_xlim"""
    # w.tracer(0)
    for e in bar_turtles.values():
        e.fd(STEP) if sgn >= 0 else e.bk(STEP)
    # w.tracer(1)

# lowest enemy center line
EBC = round(obs.y_cor_range[0])


lifes = 3
place_bars()
h = Actor(True)

stop = False
cx = 0
sign = True
enemies_wa_rockets = []
destroyed_enemies_but_rockets = []
delayed_disposal_count = 0


# tic = time.perf_counter()
# toc = time.perf_counter()
# print(toc - tic)

w.tracer(0)
# all w.update()-s below have to be here and after each move in order to make everything slower and thus playable
while not stop and lifes > 0:
    # enemies movement handler
    bond_move(sign)
    cx += 10 * sign
    if cx not in range(int(bar_move_xlim[0]), int(bar_move_xlim[1])+1):
        sign = - sign
    w.update()
    # random choice from the turtles on frontier/edge to attack
    edge = gen_edge(bar_turtles)
    try:
        ea = random.choice(list(edge.values()))
    except IndexError:
        # this exception means that hero has succeeded to destroy all enemies
        # stop = True
        break
    # safe, even if random hits an enemy with active rocket, its attack doesn't create new or reset a rocket in 'flight'
    ea.attack()
    enemies_wa_rockets.append(ea)
    w.update()
    for k, e in edge.items():
        w.update()
        if h.reactive and e not in destroyed_enemies_but_rockets:
            # if our hero has launched a rocket and it's active, also exclude hidden enemy with a rocket still active
            h.rocket.fd(STEP)
            w.update()
            if h.rocket.ycor() - e.ycor() + 10*(e.shapesize()[0] + h.rocket.shapesize()[0]) > 0:
                if abs(h.rocket.xcor()-e.xcor()) <= 10*(e.shapesize()[1]+h.rocket.shapesize()[1]):
                    print(k, 'destroyed')
                    e.hideturtle()
                    h.dispose_rocket()
                    # I just hide the destroyed enemy, I don't' want to freeze or destroy his last rocket (if present)
                    if e.reactive:
                        # don't pop it out from bar_turtles yet, but use the list to obtain an extra control
                        destroyed_enemies_but_rockets.append(e)
                    else:
                        bar_turtles.pop(k)
                    w.update()
                else:
                    # we can't destroy hero's rocket at this stage. In contrast to an enemy's case,
                    # here are several levels of enemies, he might reach the next one.
                    # I am delaying this till inner loop's end, moreover I am going to let this happen 3 times.
                    delayed_disposal_count += 1
        if e in enemies_wa_rockets:
            # continue his rocket's 'flight' (even if the enemy doesn't 'exist' anymore)
            e.rocket.fd(STEP_ER)
            w.update()

            if e.rocket.ycor() - BC - 10*(h.shapesize()[0]+e.rocket.shapesize()[0]) <= 0:
                if abs(e.rocket.xcor()-h.xcor()) <= 10*(h.shapesize()[1]+e.rocket.shapesize()[1]):
                    # prevent double hits with a same rocket
                    e.dispose_rocket()
                    w.update()
                    # such a rocket tends to hit a hero on next step, very small chance to escape (let me count as 0)
                    # life handler
                    lifes -= 1
                    print(lifes)
                    if lifes == 0:
                        # Note that it needs break to quit both loops immediately
                        stop = True
                        break
                else:
                    # instead of hiding turtles alike "e.rocket.hideturtle()", let's throw that into a personal bin,
                    # in fact reset this instance's rocket via built-in class method
                    e.dispose_rocket()
                    enemies_wa_rockets.remove(e)
                    w.update()
                if e in destroyed_enemies_but_rockets:
                    # finally, we can get rid of that enemy's rocket remainder
                    destroyed_enemies_but_rockets.remove(e)
                    bar_turtles.pop(k)
    if delayed_disposal_count >= 3:
        # 3 here because we have 3 layers and step=10
        h.dispose_rocket()
        delayed_disposal_count = 0
    w.update()

w.exitonclick()
