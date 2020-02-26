#!/usr/bin/python3

import pygame as pg
import numpy as np
import math
import time
import random

kWidth = 640
kHeight = 480
kShipSize = 32
kStateOk = 1
kStateHit = 2
kStateExplode = 3
kStateInvin = 4
kExplosionSize = int(kShipSize * 1.5)
screen = []

class Fire:
    def __init__(self, direction, pos):
        self.dir_ = np.array(direction)
        self.pos_ = np.array(pos)
        self.remove_ = False
        self.size = 2
    def update(self):
        self.pos_ = self.pos_ + self.dir_ * 5
        if self.pos_[0] < 0 or self.pos_[0] > kWidth or self.pos_[1] < 0 or self.pos_[1] > kHeight:
            self.remove_ = True
        pg.draw.circle(screen, pg.Color(0,255,0), (self.pos_ - self.size/2).astype(int), 2)

class Player:
    kLeft = 0
    kRight = 1
    kUp = 2
    kDown = 3
    kSpace = 0x10
    kMove = np.array(((-1,0), (1,0), (0,-1), (0,1)))
    kDir = {(1,0,0,0):90, (0,1,0,0):270, (0,0,1,0):  0, (0,0,0,1):180,
            (1,0,1,0):45, (1,0,0,1):135, (0,1,1,0):315, (0,1,0,1):215}

    def __init__(self, pos, sprite):
        self.pos_ = np.array(pos)
        self.keys = [False] * 4
        self.fire = False;
        self.fires = []
        self.angle = 0
        self.dir_ = np.array((0,-1))
        self.speed = 0
        self.moving = False
        self.explosion = 0
        self.state = kStateInvin
        self.state_count = 100
        self.size = kShipSize
        image = pg.image.load(sprite).convert_alpha();
        self.icon = self.player = pg.transform.scale(image, (kShipSize,kShipSize))

    def SetMap(self, keymap, firekey):
        self.keymap = keymap
        self.firekey = firekey

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
                self.dir_ = np.array((-math.sin(float(self.angle)*math.pi/180.), -math.cos(float(self.angle)*math.pi/180.)))
            self.speed = 2.0
        else:
            self.speed = 0.

    def Update(self):

        if self.state == kStateOk or self.state == kStateInvin:
            self.pos_ = self.pos_ + self.dir_ * self.speed

            if self.pos_[0] < 0:
                self.pos_[0] = 0.
            elif self.pos_[0] > kWidth+kShipSize:
                self.pos_[0] = kWidth;

            if self.pos_[1] < 0:
                self.pos_[1] = 0.
            elif self.pos_[1] > kHeight+kShipSize:
                self.pos_[1] = kHeight

            if self.state == kStateOk or (int(self.state_count/10)%2) == 1:
                screen.blit(self.icon, self.pos_ + (-kShipSize/2,-kShipSize/2))

            if self.fire:
                fire_dir = self.dir_
                f = Fire(fire_dir, self.pos_)
                self.fires.append(f)
                self.fire = False
        else:
            screen.blit(Player.explosion_sprite[int(self.state_count/5)%4], self.pos_ + (-kExplosionSize/2,-kExplosionSize/2))

        self.state_count = self.state_count - 1;
        if (self.state == kStateHit):
            self.state = kStateExplode
            self.state_count = 100
            self.moving = False
            self.keys = [False] * 4

        if (self.state_count < 0):
            if (self.state == kStateExplode):
                self.state = kStateInvin
            elif (self.state == kStateInvin):
                self.state = kStateOk
            self.state_count = 100

        for f in self.fires:
            f.update()

        self.fires = [f for f in self.fires if not f.remove_]

    def Hit(self, other):
        location = other.pos_
        for f in self.fires:
            distance = np.linalg.norm(location - f.pos_)
            if (distance < 10):
                f.remove_ = True
                if other.state == kStateOk:
                    print('Hit at ', location, ' ', f.pos_)
                    other.state = kStateHit

    def Collide(self, other):
        if self.state != kStateOk:
            return

        location = other.pos_
        distance = np.linalg.norm(location - self.pos_)
        if distance < (other.size + self.size)/2:
            self.state = kStateHit
            other.state = kStateHit

class Alien:
    def __init__(self):
        region = int(random.random() * 4)
        self.pos_ = np.array((0,0))
        self.dir_ = np.array((0.,0.))
        self.index = int(random.random()*len(Alien.alien_sprite))
        self.count_div = int(random.random() * 20) + 15
        self.count = 0
        self.phase = 0
        self.remove_ = False
        self.state = kStateOk
        self.size = kShipSize
        angle = 0
        if region >= 2:
            if region == 0:
                self.pos_[0] = -self.size
                self.dir_[0] = random.random()
            else:
                self.pos_[0] = kWidth+self.size
                self.dir_[0] = -random.random()
            self.pos_[1]= int(random.random() * kHeight)
            self.dir_[1]= random.random()*2 - 1.
        else:
            if region == 2:
                self.pos_[1]= -self.size
                self.dir_[1]= random.random()
            else:
                self.pos_[1]= kHeight+self.size
                self.dir_[1]= -random.random()
            self.pos_[0] = int(random.random() * kWidth)
            self.dir_[0] = random.random()*2 - 1.

        print('New alien at ', self.pos_, ' ', self.dir_, ' ', region)
        norm = np.linalg.norm(self.dir_)
        if norm > 0:
            self.dir_ = self.dir_ / norm
        else:
            self.dir_ = np.array((1,0))
        self.speed = random.random() + 2.5

    def update(self):
        if self.state == kStateOk:
            self.pos_ = self.pos_ + self.dir_ * self.speed
            screen.blit(Alien.alien_sprite[self.index][self.phase], self.pos_ + (-self.size/2,-self.size/2))
            if (self.count%self.count_div) == 0:
                self.phase = 1 - self.phase
        elif self.state == kStateHit:
            self.state = kStateExplode
            self.count = 0
        elif self.state == kStateExplode:
            index = int(self.count/5)
            screen.blit(Alien.explosion_sprite[index], self.pos_ + (-kExplosionSize/2,-kExplosionSize/2))
            if self.count >= 24:
                self.remove_ = True

        self.count = self.count + 1
        if self.pos_[0] < -self.size or self.pos_[1] < -self.size or self.pos_[0] > kWidth+self.size or self.pos_[1] > kHeight+self.size:
            self.remove_ = True




########## Main start ############
pg.init()
screen = pg.display.set_mode((kWidth,kHeight))

player1 = Player((590., 430.), 'galaga.png')
player1.SetMap({pg.K_a:Player.kLeft, pg.K_d:Player.kRight, pg.K_w:Player.kUp, pg.K_s:Player.kDown}, pg.K_LSHIFT)
player2 = Player((50., 50.), 'invader.png')
player2.SetMap({pg.K_LEFT:Player.kLeft, pg.K_RIGHT:Player.kRight, pg.K_UP:Player.kUp, pg.K_DOWN:Player.kDown}, pg.K_RSHIFT)


# Load sprites
sprite_surface = pg.image.load('sprite.png')
explosion = []
alien_explosion = []
for i in range(0,4):
    explosion.append(pg.transform.scale(sprite_surface.subsurface(pg.Rect(145 + i*34,1,32,32)),(kExplosionSize,kExplosionSize)))
for i in range(0,5):
    alien_explosion.append(pg.transform.scale(sprite_surface.subsurface(pg.Rect(290 + i*34,1,32,32)),(kExplosionSize,kExplosionSize)))

alien_sprite = []
for i in range(0,4):
    alien_sprite.append([])
    for j in range(0,2):
        alien_sprite[i].append(pg.transform.scale(sprite_surface.subsurface(pg.Rect(109 + j*18, 37 + i*18, 16, 16)), (kShipSize,kShipSize)))


#fire1_sprite = pg.transform.scale(sprite_surface.subsurface(pg.Rect(308, 136, 16, 16), (kShipSize, kShipSize))
#fire2_sprite = pg.transform.scale(sprite_surface.subsurface(pg.Rect(308, 136-18, 16, 16), (kShipSize, kShipSize))
Player.explosion_sprite = explosion
Alien.alien_sprite = alien_sprite
Alien.explosion_sprite = alien_explosion

running = True

count = 0
aliens = []
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
    player1.Collide(player2)
    player2.Collide(player1)

    if (count%60) == 0:
        alien = Alien()
        aliens.append(alien)
        print(len(aliens))

    for a in aliens:
        player1.Hit(a)
        player2.Hit(a)
        player1.Collide(a)
        player2.Collide(a)
        a.update()
    aliens = [a for a in aliens if not a.remove_]

    pg.display.flip()
    time.sleep(0.03)
