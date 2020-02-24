#!/usr/bin/python3

import pygame as pg
import numpy as np
import math

class Fire:
    def __init__(self, direction, pos):
        self.dir_ = np.array(direction)
        self.pos_ = np.array(pos)
        self.remove_ = False
    def update(self):
        self.pos_ = self.pos_ + self.dir_ * 0.05
        if self.pos_[0] < 0 or self.pos_[0] > 640 or self.pos_[1] < 0 or self.pos_[1] > 480:
            self.remove_ = True

class Player:
    kLeft = 0
    kRight = 1
    kUp = 2
    kDown = 3
    kSpace = 0x10
    kMove = np.array(((-1,0), (1,0), (0,-1), (0,1)))
    kDir = {(1,0,0,0):90, (0,1,0,0):270, (0,0,1,0):  0, (0,0,0,1):180,
            (1,0,1,0):45, (1,0,0,1):135, (0,1,1,0):315, (0,1,0,1):215}

    def __init__(self, screen, pos, sprite):
        self.screen = screen
        self.pos_ = np.array(pos)
        self.keys = [False] * 4
        self.fire = False;
        self.fires = []
        self.angle = 0
        self.dir = np.array((0,-1))
        self.speed = 0
        self.moving = False
        self.explosion = 0
        image = pg.image.load(sprite).convert_alpha();
        self.icon = self.player = pg.transform.scale(image, (30,30))

    def SetMap(self, keymap, firekey):
        self.keymap = keymap
        self.firekey = firekey

    def SetExplosion(self, exp):
        self.explosion_sprite = exp

    def CheckEvent(self, event):
        if self.explosion > 0:
            return

        if event.type == pg.KEYDOWN:
            if event.key in self.keymap:
                self.keys[self.keymap[event.key]] = True;
            elif event.key == self.firekey:
                self.fire = True
        elif event.type == pg.KEYUP:
            if event.key in self.keymap:
                self.keys[self.keymap[event.key]] = False;

        dirkey = self.keys.copy()
        print(dirkey)
        if not (dirkey[Player.kLeft] ^ dirkey[Player.kRight]):
            dirkey[0:2] = [False] * 2
        if not (dirkey[Player.kUp] ^ dirkey[Player.kDown]):
            dirkey[2:4] = [False] * 2

        if tuple(dirkey) in Player.kDir:
            new_angle = Player.kDir[tuple(dirkey)]
            if new_angle != self.angle:
                self.angle = new_angle
                self.icon = pg.transform.rotate(self.player, self.angle)
                self.dir = np.array((-math.sin(float(self.angle)*math.pi/180.), -math.cos(float(self.angle)*math.pi/180.)))
            self.speed = 0.02
        else:
            self.speed = 0.

    def Update(self):

        if self.explosion <= 0:
            self.pos_ = self.pos_ + self.dir * self.speed

            if self.pos_[0] < 0:
                self.pos_[0] = 0.
            elif self.pos_[0] > 640+30:
                self.pos_[0] = 640.;

            if self.pos_[1] < 0:
                self.pos_[1] = 0.
            elif self.pos_[1] > 480+30:
                self.pos_[1] = 480.

            self.screen.blit(self.icon, self.pos_ + (-15,-15))

            if self.fire:
                fire_dir = self.dir
                f = Fire(fire_dir, self.pos_)
                self.fires.append(f)
                self.fire = False
        else:
            self.screen.blit(self.explosion_sprite[int(self.explosion/300)%4], self.pos_ + (-15,-15))
            self.explosion = self.explosion - 1;

        for f in self.fires:
            f.update()
            pg.draw.circle(self.screen, pg.Color(0,255,0), (int(f.pos_[0]-1), int(f.pos_[1]-1)), 2)

        self.fires = [f for f in self.fires if not f.remove_]

    def Hit(self, other):
        location = other.pos_
        for f in self.fires:
            distance = np.linalg.norm(location - f.pos_)
            if (distance < 10):
                print('Hit at ', location, ' ', f.pos_)
                other.explosion = 5000
                other.moving = False
                other.keys = [False] * 4



pg.init()
screen = pg.display.set_mode((640,480))

player1 = Player(screen, (590., 50.), 'galaga.png')
player1.SetMap({pg.K_a:Player.kLeft, pg.K_d:Player.kRight, pg.K_w:Player.kUp, pg.K_s:Player.kDown}, pg.K_LSHIFT)
player2 = Player(screen, (50., 50.), 'invader.png')
player2.SetMap({pg.K_LEFT:Player.kLeft, pg.K_RIGHT:Player.kRight, pg.K_UP:Player.kUp, pg.K_DOWN:Player.kDown}, pg.K_RSHIFT)

sprite_surface = pg.image.load('sprite.png')
explosion = []
for i in range(0,4):
    explosion.append(sprite_surface.subsurface(pg.Rect(147 + i*30,0,30,30)))
player1.SetExplosion(explosion)
player2.SetExplosion(explosion)


running = True


fires1 = []
fires2 = []

count = 0
while running:
    fire1 = False
    fire2 = False
#    pg.draw.rect(screen, pg.Color(0,0,0), pg.Rect(pos1 - np.array([20.,20.]), (70,70)))
    screen.fill(pg.Color(0,0,0))
    count = count + 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        player1.CheckEvent(event)
        player2.CheckEvent(event)

    player1.Update()
    player2.Update()
    player1.Hit(player2)
    player2.Hit(player1)

    pg.display.flip();
