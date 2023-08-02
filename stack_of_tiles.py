# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 19:50:16 2022

@author: Baba

"""

import tkinter as tk
from tkinter import ttk
# import time as pytm
import random
# from tkinter import font
import numpy


# -----------------------------------------------------------------------------
class Paddle():
    LEFT, RIGHT = 'left', 'right'

    def __init__(self, master, mwidth):
        self.master = master
        self.height, self.width = 10, 100  # width & height of the paddle
        # self.height,self.width = 10,70 # width & height of the paddle
        self.pspeed = 20  # paddle movement speed
        # self.pspeed = 15 # paddle movement speed
        self.yloc = 470
        self.xloc = random.choice(numpy.arange(2, mwidth-self.width, 5,
                                               dtype=int))

        self.paddle = self.master.create_rectangle(
                                self.xloc, self.yloc, self.xloc+self.width,
                                self.yloc+self.height, fill='#A8324E'
                                )
        self.master.bind('<Left>', lambda _: move_paddle(Paddle.LEFT, mwidth))
        self.master.bind('<Right>', lambda _: move_paddle(Paddle.RIGHT,
                                                          mwidth))
        self.master.bind('<KeyPress-a>', lambda _: move_paddle(Paddle.LEFT,
                                                               mwidth))
        self.master.bind('<KeyPress-d>', lambda _: move_paddle(Paddle.RIGHT,
                                                               mwidth))
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        def move_paddle(dirc, mwidth):
            x0, y0, x1, y1 = self.master.coords(self.paddle)
            if dirc == Paddle.LEFT and x0 > 2:
                if x0-self.pspeed < 2:
                    self.master.move(self.paddle, -(x0-2), 0)
                else:
                    self.master.move(self.paddle, -self.pspeed, 0)
            elif dirc == Paddle.RIGHT and x1 < mwidth:
                if x1+self.pspeed > mwidth:
                    self.master.move(self.paddle, mwidth-x1+1, 0)
                else:
                    self.master.move(self.paddle, self.pspeed, 0)
# -----------------------------------------------------------------------------


# =============================================================================
class Brick():
    colorList = '#00FF00', '#00FFFF', '#FF00FF'  # Green:1, Blue:2, Red:3

    def __init__(self, master, x0, y0, x1, y1, color):
        self.strength = Brick.colorList.index(color)
        self.brick = master.create_rectangle(x0, y0, x1, y1, fill=color,
                                             tags='brick')
        self.master = master

    def hit(self):
        delbrick = None
        if self.strength == 0:
            # print('\ndeleting brick: ',self.brick)
            delbrick = self.brick
            self.master.delete(self.brick)
        else:
            self.strength -= 1
            self.master.itemconfigure(self.brick,
                                      fill=Brick.colorList[self.strength])
        return delbrick


# =============================================================================
class Game():
    brickColors = '#00FF00', '#00FFFF', '#FF00FF'  # Green:1, Blue:2, Red:3

    def __init__(self):
        self.width, self.height = 705, 500  # width & height of the game window
        self.wbrick, self.hbrick = 100, 20  # width & height of the brick
        self.ballRun = False
        self.speed = 10
        self.gameLevel = 40
        self.lives = 3
        self.dirMag = [-1, -1]  # move in +x and +y
        self.rball = 8  # radius of the ball
        self.objects = {}
        # number of bricks - horizontally and vertically
        # self.nrow, self.ncol = 1, 1
        self.nrow, self.ncol = 4, 7

        self.mwin = tk.Tk()
        self.mwin.title('Paddle and Brick Game')
        self.mwin.geometry('710x600+80+100')
        self.mwin.lift()

        self.mfrm = tk.Frame(self.mwin, width=self.width+5, height=60,
                             bg='#ae519e')
        self.mfrm.place(x=0, y=0)

        self.master = tk.Canvas(self.mwin, width=self.width,
                                height=self.height, bg='#dab3ff')
        self.master.place(x=0, y=60)
        self.btnExt = ttk.Button(self.mwin, text='Exit Game',
                                 command=self.mwin.destroy, takefocus=False)
        self.btnExt.place(x=400, y=self.height+64, height=35, width=120)
        self.restartbtn = ttk.Button(self.mwin, text='Reboot Game',
                                     state=tk.DISABLED,
                                     command=self.rebootGame, takefocus=False)
        self.restartbtn.place(x=100, y=self.height+64, height=35, width=130)

        self.master.focus_set()
        self.initiate_game()
        # print(font.families())
        # self.count = 0
        self.mwin.mainloop()
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    def rebootGame(self):
        self.lives = 3
        self.liveText.set('Lives Available: %d' % self.lives)
        self.startNextLife(True)
        self.restartbtn.config(state=tk.DISABLED)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    def initiate_game(self):
        self.addObjects()

        self.liveText, self.infoText = tk.StringVar(), tk.StringVar()
        self.lbl = tk.Label(self.mfrm, textvariable=self.liveText,
                            fg='white', bg='#ae519e',
                            font=('DejaVu Sans Mono', 20, 'bold'))
        self.lbl.place(x=5, y=10)
        self.liveText.set('Lives Available: %d' % self.lives)

        imsg = 'Press Space to start the game!\nAvailable Lives: %d' %\
            self.lives
        self.infoText.set(imsg)
        self.start_lbl = tk.Label(self.master, textvariable=self.infoText,
                                  fg='black', bg='#dab3ff', anchor=tk.CENTER,
                                  font=('Lucida Calligraphy', 20, 'italic'))
        self.start_lbl.place(x=2, y=self.height//2, width=self.width)
        self.master.bind('<space>', self.startTheGame)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def addObjects(self, addbricks=True):
        # Adding paddle
        self.pdl = Paddle(self.master, self.width)

        # Adding the ball to the screen
        px0, py0, px1, _ = self.master.coords(self.pdl.paddle)

        px = (px0+px1)//2
        self.ball = self.master.create_oval(px-self.rball, py0-2*self.rball,
                                            px+self.rball, py0, fill='white')
        if not addbricks:
            return

        # Adding the bricks to the screen
        n = self.nrow*self.ncol
        a, b = n//3, n % 3
        colors = list(Game.brickColors) * a + [Game.brickColors[2],] * b
        random.shuffle(colors)
        for j in range(self.nrow):
            for i in range(self.ncol):
                ib = Brick(
                            self.master, 4+self.wbrick*i, 44+self.hbrick*j,
                            4+self.wbrick*(i+1), 44+self.hbrick*(j+1),
                            colors[self.ncol*j+i]
                            )
                self.objects[ib.brick] = ib
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def checkLives(self):
        _, _, _, py1 = self.master.coords(self.pdl.paddle)
        _, y0, _, _ = self.master.coords(self.ball)
        if y0 >= py1:
            self.lives -= 1
            if self.lives == 0:
                self.start_lbl.place(x=2, y=self.height//2, width=self.width)
                self.master.unbind('<space>')
                self.liveText.set('Lives Available: %d' % self.lives)
                self.infoText.set('Game Over!!!')
                self.restartbtn.configure(state=tk.ACTIVE)
                self.run_ball = False
                return
            self.start_lbl.place(x=2, y=self.height//2, width=self.width)
            self.liveText.set('Lives Available: %d' % self.lives)
            imsg = ('Oops! You lost a life.\n'
                    'Press Space to start the game again!')
            self.infoText.set(imsg)
            self.master.unbind('<space>')
            self.master.bind('<space>', self.startNextLife)
            self.run_ball = False
        #     return False
        # else:
        #     return True
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def startNextLife(self, e):
        self.master.unbind('<space>')
        self.master.delete(self.ball)
        self.master.delete(self.pdl.paddle)

        if e is True:
            self.addObjects()
        else:
            self.addObjects(addbricks=False)

        imsg = 'Press Space to start!\nAvailable Lives: %d' % self.lives
        self.start_lbl.place_forget()
        self.start_lbl.place(x=2, y=self.height//2, width=self.width)
        self.infoText.set(imsg)
        self.master.bind('<space>', self.startTheGame)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def startTheGame(self, e):
        self.start_lbl.place_forget()
        self.run_ball = True
        self.move_ball()
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def move_ball(self):
        self.checkLives()
        if not self.run_ball:
            return

        x0, y0, x1, y1 = self.master.coords(self.ball)
        xoff, yoff = self.dirMag[0]*self.speed, self.dirMag[1]*self.speed

        ispeed = self.speed
        if x0+xoff < 2:  # for left edge
            if x0 > 2:
                ispeed = x0 - 2
            else:
                self.dirMag[0] *= -1
        elif x1+xoff-1 > self.width:  # right edge
            if x1-1 < self.width:
                ispeed = self.width-x1+1
            else:
                self.dirMag[0] *= -1
        if y0+yoff < 2:  # top edge
            if y0 > 2:
                ispeed = y0 - 2
            else:
                self.dirMag[1] *= -1
        elif y1+yoff-1 > self.height:  # bottom edge
            if y1-1 < self.height:
                ispeed = self.height-y1+1
            else:
                self.dirMag[1] *= -1

        xoff, yoff = self.dirMag[0]*ispeed, self.dirMag[1]*ispeed

        # Finding overlapping objects in next ball movement:
        # hence added xoff and yoff
        objs = self.master.find_overlapping(x0+xoff, y0+yoff,
                                            x1+xoff, y1+yoff)
        if len(objs) > 1:
            xoff, yoff = self.collision(objs)

        self.master.move(self.ball, xoff, yoff)

        self.mwin.after(self.gameLevel, self.move_ball)
        # self.count += 1
        # if self.count != 10000:
        #     self.mwin.after(self.gameLevel, self.move_ball)
        #     # self.after(self.speed, self.move_ball)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def checkBricks(self, delBrick):
        if delBrick:
            self.objects.pop(delBrick)
            if not self.objects:
                self.run_ball = False
                imsg = 'Congratulation!!!\nYou WON!!!'
                self.start_lbl.place_forget()
                self.start_lbl.place(x=2, y=self.height//2, width=self.width)
                self.infoText.set(imsg)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def collision(self, items):
        # print('\n'+'-'*40)
        # print('Ball is colliading...',items)
        xoff, yoff = self.dirMag[0]*self.speed, self.dirMag[1]*self.speed
        # print('xoff,yoff: ',xoff,yoff)
        x0, y0, x1, y1 = self.master.coords(self.ball)
        # print('ball coords:',x0, y0, x1, y1)
        x, y = (x0+x1)/2, (y0+y1)/2
        # print('x y', x,y,'\n')
        ispeed = self.speed

        # ball hitting to the paddle
        if self.pdl.paddle in items:
            xx0, yy0, xx1, yy1 = self.master.coords(self.pdl.paddle)
            # print('paddle coords: ', xx0, yy0,xx1, yy1)
            # print('ball is going to hit the paddle...')
            if xx0 <= x1+xoff <= xx1 or xx0 <= x0+xoff <= xx1:
                # print('ball will hit from vertically downward direction.')
                if x1 < xx0:  # hitting from left to edge
                    ispeed = xx0 - x1
                elif x0 > xx1:  # hitting from right to edge
                    ispeed = x0 - xx1
                elif (x1 == xx0) or (x0 == xx1):
                    if y1 < yy0:
                        ispeed = yy0 - y1
                    else:
                        self.dirMag[0] *= -1
                elif y1 < yy0:  # hitting from left to edge
                    ispeed = yy0 - y1
                elif y1 == yy0:
                    self.dirMag[1] *= -1
            return self.dirMag[0]*ispeed, self.dirMag[1]*ispeed

        temp = list(items)
        temp.remove(self.ball)
        items = tuple(temp)
        out3 = None
        for obj in items:
            # print()
            xx0, yy0, xx1, yy1 = self.master.coords(obj)
            # print(obj, xx0, yy0,xx1, yy1)
            hitFlag1, hitFlag2 = False, False
            if xx0 < x0 < xx1 or xx0 < x1 < xx1:  # ball hitting vartically
                # print('x is inside the limits')
                if y0 > yy1:  # ball near from below
                    # print('y0, yy1',y0, yy1,)
                    ispeed = y0 - yy1
                    # print('if if ',ispeed)
                    out2 = [ispeed, 1]
                elif y1 < yy0:  # ball near from above
                    # print('y1, yy0',y1, yy0)
                    ispeed = yy0 - y1
                    # print('if elif ',ispeed)
                    out2 = [ispeed, 1]
                else:  # ball hitting exactly - change direction
                    # print('ball hit %d object' % obj)
                    delBrick = self.objects[obj].hit()  # ball hit the brick
                    self.checkBricks(delBrick)
                    print('bricks left: ', len(self.objects))
                    out2 = [self.speed, -1]
                    # print('if else ',self.speed)
                hitFlag1 = True
            elif yy0 < y < yy1:  # ball hitting horizontally
                # print('y is inside the limits of mean Y')
                # print('horizontal hit')
                if x0 > xx1:  # ball near from right side
                    ispeed = x0 - xx1
                    out1 = [ispeed, 1]
                    # print('else if ',ispeed)
                    # print('horizontal hit',x0,xx1,x0-xx1, ispeed)
                elif x1 < xx0:  # ball near from left side
                    ispeed = xx0 - x1
                    out1 = [ispeed, 1]
                    # print('else elif ',ispeed)
                    # print('horizontal hit',xx0,x1,xx0 - x1, ispeed)
                else:  # ball hitting exactly - change direction
                    delBrick = self.objects[obj].hit()  # ball hit the brick
                    self.checkBricks(delBrick)
                    print('bricks left: ', len(self.objects))
                    out1 = [self.speed, -1]
                    # print('else else ',self.speed)
                hitFlag2 = True
            # print(hitFlag1, hitFlag2)
            if not out3:
                if hitFlag1 and hitFlag2:
                    out3 = [min(out1[0], out2[0]), out1[1], out2[1]]
                elif hitFlag2:
                    out3 = [out1[0], out1[1], 1]
                elif hitFlag1:
                    out3 = [out2[0], 1, out2[1]]
            else:
                if hitFlag1 and hitFlag2:
                    if min(out1[0], out2[0]) < out3[0]:
                        out3 = [min(out1[0], out2[0]), out1[1], out2[1]]
                elif hitFlag2:
                    if out1[0] < out3[0]:
                        out3[0] = out1[0]
                        out3[1] *= out1[1]
                elif hitFlag1:
                    if out2[0] < out3[0]:
                        out3[0] = out2[0]
                        out3[2] *= out2[1]

        if not out3:
            out3 = [self.speed, 1, 1]
        # print('speed details: ',self.speed, out3[0])
        # print('direction before',self.dirMag[0], self.dirMag[1])
        self.dirMag[0] *= out3[1]
        self.dirMag[1] *= out3[2]
        # print('direction after',self.dirMag[0], self.dirMag[1])
        return self.dirMag[0]*out3[0], self.dirMag[1]*out3[0]
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
    def stop_ball(self):
        pass
# -----------------------------------------------------------------------------


a = Game()
# if __name__ == '__main__':
#     root = tk.Tk()
#     root.geometry('710x540+80+100')
#     root.lift()
#     Game(root)
#     root.mainloop()
