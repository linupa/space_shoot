#!/usr/bin/python3

import pygame as pg
import numpy as np
import time
import random

kWidth = 640
kHeight = 480
kShipSize = 32
kExplosionSize = int(kShipSize * 1.5)
kEnemyShootSpeed = 5
kPlayerShootSpeed = 10
kLives = 5

kBossWidth = 200

kStateOk = 1
kStateHit = 2
kStateExplode = 3
kStateInvin = 4

kTypePlayer = 1
kTypeEnemy = 2

kFireFromEnemy = 100

kBossLife = 100

screen = []

class Fire:
    fires = []
    def __init__(self, direction, pos, fire_type):
        self.dir_ = np.array(direction)
        self.pos_ = np.array(pos)
        self.remove_ = False
        self.size = 2
        if fire_type == kFireFromEnemy:
            self.speed = kEnemyShootSpeed
        else:
            self.speed = kPlayerShootSpeed
        self.fire_type = fire_type
        Fire.fires.append(self)

    def Update(self):
        self.pos_ = self.pos_ + self.dir_ * self.speed
        if self.pos_[0] < 0 or self.pos_[0] > kWidth or self.pos_[1] < 0 or self.pos_[1] > kHeight:
            self.remove_ = True

        if self.fire_type == kFireFromEnemy:
            pg.draw.circle(screen, pg.Color(255,0,0), (self.pos_ - self.size/2).astype(int), 2)
        else:
            pg.draw.circle(screen, pg.Color(0,255,0), (self.pos_ - self.size/2).astype(int), 2)

    @staticmethod
    def UpdateAll():
        for f in Fire.fires:
           f.Update()
        Fire.fires = [f for f in Fire.fires if not f.remove_]

    @staticmethod
    def Hit(other):
        location = other.pos_
        for f in Fire.fires:
            if f.fire_type != kFireFromEnemy and other.type == kTypePlayer:
                continue
            if f.fire_type == kFireFromEnemy and other.type == kTypeEnemy:
                continue

            if other.Contain(f.pos_, 1):
                f.remove_ = True
                if other.state == kStateOk:
                    print('Hit at ', location, ' ', f.pos_)
                    other.state = kStateHit
                    if f.fire_type != kFireFromEnemy:
                        Player.player_ids[f.fire_type].score = Player.player_ids[f.fire_type].score + 1

class Boss:
    def __init__(self, pos, sprite):
        image = pg.image.load(sprite).convert_alpha()
        self.pos_ = np.array(pos)
        self.width = image.get_width()
        self.height = image.get_height()
        ratio = kBossWidth / self.width
        self.width = int(self.width * ratio)
        self.height = int(self.height * ratio)
        self.icon = pg.transform.scale(image, (self.width, self.height))
        print(self.width)
        print(self.height)
        print(self.pos_ + (-self.width/2,-self.height/2))

        self.nudge_counter = 50
        self.acc_count = 0
        self.cur_pos = self.pos_
        self.cur_vel = np.array((0,0))
        self.cur_acc = np.array((0,0))
        self.impulse = np.array((0,0))

        self.remove_ = False
        self.type = kTypeEnemy
        self.state = kStateOk
        self.life = kBossLife

    def Update(self):
        if self.nudge_counter == 0:
            self.impulse[0] = random.random() * 5.5
            self.impulse[1] = random.random() * 5.5
            self.nudge_counter = 50
        if (self.nudge_counter % 3) == 0 and self.state == kStateOk:
            angle = random.random() * 2. * np.pi
            fire_dir = (np.cos(angle), np.sin(angle))
            Fire(fire_dir, self.pos_, kFireFromEnemy)

        if self.state == kStateHit:
            self.life = self.life - 1
            self.state = kStateOk

        if self.life <= 0:
            self.state = kStateExplode

        dt = 0.03
        kp = 0.3
        kAlpha = 0.99
        self.cur_acc = self.impulse + kp *(self.pos_ - self.cur_pos)
        self.cur_vel = self.cur_vel + self.cur_acc * dt
        self.cur_pos = self.cur_pos + self.cur_vel * dt
        self.impulse = self.impulse * kAlpha
        self.nudge_counter = self.nudge_counter - 1

        if self.state != kStateExplode:
            screen.blit(self.icon, self.cur_pos + (-self.width/2,-self.height/2))

        pg.draw.rect(screen, (255,0,0), (20, 30, 600, 20))
        pg.draw.rect(screen, (0,255,0), (20, 30, 600*self.life/kBossLife, 20))

#        px = self.cur_pos[0] + 30
#        py = self.cur_pos[1]
#        for i in range(0,21):
#            x = self.cur_pos[0] + int(30 * np.cos(np.pi*2/20*i))
#            y = self.cur_pos[1] + int(130 * np.sin(np.pi*2/20*i))
#            pg.draw.line(screen, (0,0,255), (x,y), (px,py), 1)
#            px = x
#            py = y
#
#        px = self.cur_pos[0] + 30
#        py = self.cur_pos[1]
#        for i in range(0,21):
#            x = self.cur_pos[0] - 40 + int(30 * np.cos(np.pi*2/20*i))
#            y = self.cur_pos[1] - 20 + int(80 * np.sin(np.pi*2/20*i))
#            pg.draw.line(screen, (0,0,255), (x,y), (px,py), 1)
#            px = x
#            py = y
#
#        px = self.cur_pos[0] + 30
#        py = self.cur_pos[1]
#        for i in range(0,21):
#            x = self.cur_pos[0] + 30 + int(30 * np.cos(np.pi*2/20*i))
#            y = self.cur_pos[1] + 50 + int(80 * np.sin(np.pi*2/20*i))
#            pg.draw.line(screen, (0,0,255), (x,y), (px,py), 1)
#            px = x
#            py = y
#
#        px = self.cur_pos[0] + 25
#        py = self.cur_pos[1]
#        for i in range(0,21):
#            x = self.cur_pos[0] - 10 + int(25 * np.cos(np.pi*2/20*i))
#            y = self.cur_pos[1] - 120 + int(25 * np.sin(np.pi*2/20*i))
#            pg.draw.line(screen, (0,0,255), (x,y), (px,py), 1)
#            px = x
#            py = y
#

    def Contain(self, pos, radius):
        a = 30 + radius
        b = 130 + radius
        x = pos[0] - self.cur_pos[0]
        y = pos[1] - self.cur_pos[1]
        if b*b*x*x + a*a*y*y <= a*a*b*b:
            return True

        a = 30 + radius
        b = 80 + radius
        x = pos[0] - self.cur_pos[0] + 40
        y = pos[1] - self.cur_pos[1] + 20
        if b*b*x*x + a*a*y*y <= a*a*b*b:
            return True

        a = 30 + radius
        b = 80 + radius
        x = pos[0] - self.cur_pos[0] - 30
        y = pos[1] - self.cur_pos[1] - 50
        if b*b*x*x + a*a*y*y <= a*a*b*b:
           return True

        a = 25 + radius
        b = 25 + radius
        x = pos[0] - self.cur_pos[0] + 10
        y = pos[1] - self.cur_pos[1] + 120
        if b*b*x*x + a*a*y*y <= a*a*b*b:
            return True

        return False

class Player:
    kLeft = 0
    kRight = 1
    kUp = 2
    kDown = 3
    kSpace = 0x10
    kMove = np.array(((-1,0), (1,0), (0,-1), (0,1)))
    kDir = {(1,0,0,0):90, (0,1,0,0):270, (0,0,1,0):  0, (0,0,0,1):180,
            (1,0,1,0):45, (1,0,0,1):135, (0,1,1,0):315, (0,1,0,1):215}
    player_ids = []

    def __init__(self, pos, sprite):
        self.pos_ = np.array(pos)
        self.player_id = len(Player.player_ids)
        self.keys = [False] * 4
        self.fire = False;
        self.angle = 0
        self.dir_ = np.array((0,-1))
        self.speed = 0
        self.moving = False
        self.explosion = 0
        self.state = kStateInvin
        self.state_count = 100
        self.size = kShipSize
        self.info = (0,0);
        image = pg.image.load(sprite).convert_alpha()
        self.icon = self.player = pg.transform.scale(image, (kShipSize,kShipSize))
        self.score = 0
        self.font = pg.font.SysFont('comicsans', 30)
        self.lives = kLives
        self.life = pg.transform.scale(image, (int(kShipSize/2),int(kShipSize/2)))
        self.type = kTypePlayer
        Player.player_ids.append(self)

    def SetMap(self, keymap, firekey):
        self.keymap = keymap
        self.firekey = firekey

    def SetInfoLocation(self, location):
        self.info = location

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
                self.dir_ = np.array((-np.sin(float(self.angle)*np.pi/180.), -np.cos(float(self.angle)*np.pi/180.)))
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
                Fire(fire_dir, self.pos_, self.player_id)
                self.fire = False
        else:
            screen.blit(Player.explosion_sprite[int(self.state_count/5)%4], self.pos_ + (-kExplosionSize/2,-kExplosionSize/2))

        text = self.font.render('Score: ' + str(self.score), 1, (255,255,255))
        screen.blit(text, self.info)
        xpos = self.info[0] + text.get_width() + 10
        for i in range(0,self.lives-1):
            screen.blit(self.life, (xpos, self.info[1]))
            xpos = xpos + self.life.get_width() + 10

        self.state_count = self.state_count - 1;
        if (self.state == kStateHit):
            self.lives = self.lives - 1
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



    def Collide(self, other):
        if self.state != kStateOk or other.state != kStateOk:
            return

        if other.Contain(self.pos_, self.size/2):
            self.state = kStateHit
            other.state = kStateHit

    def Contain(self, pos, radius):
        distance = np.linalg.norm(self.pos_ - pos)
        if (distance < 10 + radius):
            return True
        else:
            return False

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
        self.lives = 1;
        self.type = kTypeEnemy
        angle_from = 0.
        if region >= 2:
            if region == 0:
                self.pos_[0] = -self.size
                angle_from = np.pi
            else:
                self.pos_[0] = kWidth+self.size
                angle_from = 0.
            self.pos_[1]= int(random.random() * kHeight)
        else:
            if region == 2:
                self.pos_[1]= -self.size
                angle_from = np.pi/2.
            else:
                self.pos_[1]= kHeight+self.size
                angle_from = np.pi*3/2.
            self.pos_[0] = int(random.random() * kWidth)

        self.angle = angle_from + random.random() * np.pi
        self.dir_ = np.array((-np.sin(self.angle), -np.cos(self.angle)))

        print('New alien at ', self.pos_, ' ', self.dir_, ' ', region)
        norm = np.linalg.norm(self.dir_)
        if norm > 0:
            self.dir_ = self.dir_ / norm
        else:
            self.dir_ = np.array((1,0))
        self.speed = random.random() + 2.5

    def Update(self):
        if self.state == kStateOk:
            self.pos_ = self.pos_ + self.dir_ * self.speed
            angle_idx = int(((int(self.angle * 180 / np.pi) + 360) % 360)/45)
            screen.blit(Alien.alien_sprite[self.index][self.phase][angle_idx], self.pos_ + (-self.size/2,-self.size/2))
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

    def Contain(self, pos, radius):
        distance = np.linalg.norm(self.pos_ - pos)
        if (distance < 10 + radius):
            return True
        else:
            return False




########## Main start ############
pg.init()
screen = pg.display.set_mode((kWidth,kHeight))

player1 = Player((590., 430.), 'galaga.png')
player1.SetMap({pg.K_a:Player.kLeft, pg.K_d:Player.kRight, pg.K_w:Player.kUp, pg.K_s:Player.kDown}, pg.K_LSHIFT)
player2 = Player((50., 50.), 'invader.png')
player2.SetMap({pg.K_LEFT:Player.kLeft, pg.K_RIGHT:Player.kRight, pg.K_UP:Player.kUp, pg.K_DOWN:Player.kDown}, pg.K_RSHIFT)

boss01 = Boss((320,240), 'boss01.png');

player1.SetInfoLocation((10,0));
player2.SetInfoLocation((330,0));

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
    alien_sprite.append([[],[]])
    for j in range(0,2):
        image = pg.transform.scale(sprite_surface.subsurface(pg.Rect(109 + j*18, 37 + i*18, 16, 16)), (kShipSize,kShipSize))
        for k in range(0,8):
            alien_sprite[i][j].append(pg.transform.rotate(image, k*45))


#fire1_sprite = pg.transform.scale(sprite_surface.subsurface(pg.Rect(308, 136, 16, 16), (kShipSize, kShipSize))
#fire2_sprite = pg.transform.scale(sprite_surface.subsurface(pg.Rect(308, 136-18, 16, 16), (kShipSize, kShipSize))
Player.explosion_sprite = explosion
Alien.alien_sprite = alien_sprite
Alien.explosion_sprite = alien_explosion

running = True

count = 0
aliens = []

aliens.append(boss01)
while running:
    fire1 = False
    fire2 = False
#    pg.draw.rect(screen, pg.Color(0,0,0), pg.Rect(pos1 - np.array([20.,20.]), (70,70)))
    screen.fill(pg.Color(0,0,0))
    count = count + 1

    Fire.UpdateAll()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        player1.CheckEvent(event)
        player2.CheckEvent(event)

    player1.Update()
    player2.Update()
    Fire.Hit(player2)
    Fire.Hit(player1)
    player1.Collide(player2)
    player2.Collide(player1)

    if (count%60) == 0:
        alien = Alien()
        aliens.append(alien)
        print(len(aliens))

    for a in aliens:
        Fire.Hit(a)
        player1.Collide(a)
        player2.Collide(a)
        a.Update()
    aliens = [a for a in aliens if not a.remove_]

    pg.display.flip()
    time.sleep(0.03)
