"""
ZE : Zombies Escape

Game Controls :
            right arrow : move forward
            left arrow  : move backward
            up arrow    : enter gate
            down arrow  : leave gate
            q key       : quit

Cheat Codes :
            k key       : make player invincible
            p key       : level up
            o key       : level down

Developed By :
            Idea and Debugging   : Yaman Kumar Sahu
            Code and Soundtracks : Amitesh Patra
            Graphics and sprites : Manas Banjare
            Documentation        : Rishabh Biswal
"""
import pygame
from pygame.locals import *
from pygame import mixer
import random

import level_data


# Game initialized
pygame.mixer.pre_init( 44100, -16, 2, 512)
mixer.init()
pygame.init()
zombies = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# Game Variables
screen_width = 1200
screen_height = 800
run = True
tile_size = 50
fps = 60
level = 1
max_levels = 6
gate_coordinates = []
draw_rect = False
teleport = False
death = 1
bg = [ 1, 2, 3, 4, 5]
random.shuffle(bg)
bg.append(6)
retreat = False
main_menu = True
how_to_menu = False
settings_menu = False
about_menu = False
finished = False
paused = False
music_disabled = False
effects_disabled = False
played = False
loaded = False
tutorial = 0


# Game classes
class World():
    def __init__(self, world_map):
        super.__init__()
        self.tile_list = []
        floor_img = pygame.image.load( "images/floor/floor_3.jpg")
        wall_img = pygame.image.load( "images/floor/floor_3.jpg")

        row_count = 0
        for row in world_map:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale( floor_img, ( tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = ( img, img_rect)
                    self.tile_list.append( tile)
                elif tile == 2:
                    img = pygame.transform.scale( wall_img, ( tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = ( img, img_rect)
                    self.tile_list.append( tile)
                elif tile in [ 3, 4, 5]:
                    zombie = Zombie( col_count * tile_size + tile_size, row_count * tile_size - 36, tile)
                    zombies.add( zombie)
                col_count += 1
            row_count += 1

    def draw( self):
        for tile in self.tile_list:
            screen.blit( tile[0], tile[1])
            if draw_rect:
                pygame.draw.rect( screen, ( 255, 255, 255), tile[1], 2)

class Zombie( pygame.sprite.Sprite):
    def __init__( self, x, y, type):
        pygame.sprite.Sprite.__init__( self)
        self.spawnZombie( x, y, type)
    
    def spawnZombie( self, x, y, type):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.type = type
        if type == 3:
            for num in range( 8):
                img_right = pygame.image.load( f"images/zombie/zom_1/zombie_{num}.png")
                img_right = pygame.transform.scale( img_right, ( 65, 95))
                img_left = pygame.transform.flip( img_right, True, False)
                self.images_right.append( img_right)
                self.images_left.append( img_left)
            self.image = self.images_right[ self.index]
            self.rect = self.image.get_rect()
            self.rect.y = y
            self.speed = 10
            self.walk_cooldown = 10
            self.rect.x = x
            self.direction = random.choice( [1, -1])
        elif type == 4:
            for num in range( 10):
                img_right = pygame.image.load( f"images/zombie/zom_2/zombie_{num}.png")
                img_right = pygame.transform.scale( img_right, ( 85, 85))
                img_left = pygame.transform.flip( img_right, True, False)
                self.images_right.append( img_right)
                self.images_left.append( img_left)
            self.image = self.images_right[ self.index]
            dummy_image = pygame.image.load( f"images/zombie/zom_2/zombie_{num}.png")
            dummy_image = pygame.transform.scale( img_right, ( 65, 75))
            self.rect = dummy_image.get_rect()
            self.rect.y = y + 5
            self.speed = 20
            self.walk_cooldown = 10
            self.rect.x = x
            self.direction = random.choice( [1, -1])
        if type == 5:
            for num in range( 2, 10):
                img_right = pygame.image.load( f"images/zombie/zom_3/000{num}.png")
                img_right = pygame.transform.scale( img_right, ( 105, 135))
                img_left = pygame.transform.flip( img_right, True, False)
                self.images_left.append( img_right)
                self.images_right.append( img_left)
            self.image = self.images_right[ self.index]
            self.rect = self.image.get_rect()
            self.rect.y = y - 35
            self.speed = 8
            self.walk_cooldown = 15
            self.rect.x = x
            self.teleport_wait = 0
            self.max_wait = random.choice( [ 200, 400, 600])
            self.direction = random.choice( [1, -1])
    
    def checkEdges( self):
        screen_rect = screen.get_rect()  
        if self.direction == 1:
            if self.rect.right >= screen_rect.right - tile_size:
                self.direction *= -1
        if self.direction == -1:
            if self.rect.left <= tile_size:
                self.direction *= -1

    def update( self):
        walk_cooldown = self.walk_cooldown
        self.checkEdges()
        if self.direction == 1:
            self.rect.x += float( random.randint( 1, self.speed) * self.direction) / 6
        elif self.direction == -1:
            self.rect.x += float( random.randint( 1, self.speed) * self.direction) / 6 + 1
        self.counter += 1
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len( self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[ self.index]
            if self.direction == -1:
                self.image = self.images_left[ self.index]
        if self.type == 5:
            self.teleport_wait += 1
            if self.teleport_wait >= self.max_wait:
                teleport_fx.play()
                new_pos = random.choice( gate_coordinates)
                self.rect.x = new_pos[0]
                self.rect.y = new_pos[1]
                self.teleport_wait = 0
                self.max_wait = random.choice( [ 200, 400, 600])
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 2)


class Chopper():
    def __init__( self):
        self.images = []
        self.index = 0
        for num in range(1, 8):
            img = pygame.image.load( f"images/chopper/h{num}.png")
            rect = img.get_rect()
            img = pygame.transform.scale( img, ( rect.w + 20, rect.h + 20))
            self.images.append( img)
        self.image = self.images[ self.index]
        self.rect = self.image.get_rect()
        self.rect.x = 600
        self.rect.y = -110
        self.walk_cooldown = 10
        self.move_cooldown = 2
        self.walk_counter = 0
        self.move_counter = 0
        self.moving = True
        self.direction = 1

    def update( self):
        if not paused:
            if self.moving:
                if self.move_counter >= self.move_cooldown:
                    if self.rect.bottom < 420:
                        self.rect.y += 1 * self.direction
                        self.move_counter = 0
                    else:
                        self.moving = False
                else:
                    self.move_counter += 1
                    
            if self.walk_counter >= self.walk_cooldown:
                self.index = ( self.index + 1) % 7
                self.image = self.images[ self.index]
                self.walk_counter = 0
            else:
                self.walk_counter += 1
        screen.blit( self.image, self.rect)
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 2)


class Ladder():
    def __init__( self):
        image = pygame.image.load( "images/ladder/ladder.png")
        self.image = pygame.transform.scale( image, ( 100, 300))
        self.rect = self.image.get_rect()
        self.rect.x = 680
        self.rect.y = 100
        self.counter = 0
        self.height = 300
        self.move_cooldown = 5
        self.down = False

    def update( self):
        if not paused:
            if self.counter > self.move_cooldown:
                if self.rect.x > 684 or self.rect.x < 676:
                    self.rect.x = 680
                    if retreat:
                        player.rect.x = 710
                dx = random.randint( -2, 2)
                self.rect.x += dx
                if retreat:
                    player.rect.x += dx
                self.counter = 0
            else:
                self.counter += 1
            if not self.down:
                if self.rect.y < 400:
                    self.rect.y += 1
                else:
                    self.down = True
        screen.blit( self.image, self.rect)
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 2)


class Button():
    def __init__( self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x - 150
        self.rect.y = y - 70
        self.clicked = False

    def draw( self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint( pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        screen.blit( self.image, self.rect)
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 4)

        return action

class Player():
    def __init__( self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.speed = 3
        for num in range( 7):
            img_right = pygame.image.load( f"images/player/player_{num}.png")
            img_right = pygame.transform.scale( img_right, ( 45, 85))
            img_left = pygame.transform.flip( img_right, True, False)
            self.images_right.append( img_right.subsurface( img_right.get_rect().x, img_right.get_rect().y,
                    img_right.get_width(), img_right.get_height() - 5))
            self.images_left.append( img_left)
        self.dead_image = pygame.image.load( "images/player/death.png")
        self.image = self.images_right[ self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.temp_pos = [0, 0]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = 0
        self.inside = False
        self.game_over = 0
        self.death_float = 0

    def update( self):
        dx = 0
        dy = 0
        walk_cooldown = 20
        key = pygame.key.get_pressed()

        if not paused:
            if self.game_over == 0 and not retreat:
                if key[ pygame.K_LEFT]:
                    dx -= self.speed
                    self.counter += 3
                    self.direction = -1
                if key[ pygame.K_RIGHT]:
                    dx += self.speed
                    self.counter += 3
                    self.direction = 1
                if not key[ pygame.K_LEFT] and not key[ pygame.K_RIGHT]:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[ self.index]
                    elif self.direction == -1:
                        self.image = self.images_left[ self.index]
                
                if key[ pygame.K_DOWN] and self.inside:
                    if not effects_disabled:
                        leave_fx.play()
                    self.rect.x, self.rect.y = self.temp_pos[0], self.temp_pos[1]
                    self.inside = False

                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len( self.images_right):
                        self.index = 1
                    if self.direction == 1:
                        self.image = self.images_right[ self.index]
                    elif self.direction == -1:
                        self.image = self.images_left[ self.index]
                
                for tile in world.tile_list:
                    if tile[1].colliderect( self.rect.x + dx, self.rect.y, self.width, self.height):
                        dx = 0
                    if tile[1].colliderect( self.rect.x, self.rect.y, self.width, self.height):
                        dy = tile[1].top - self.rect.bottom
                
                if pygame.sprite.spritecollide( self, zombies, False) and death == 1:
                    self.game_over = -1
                
                if pygame.sprite.spritecollide( self, exit_group, False) and key[pygame.K_UP]:
                    self.rect.x, self.rect.y = 10000, 10000
                    if not effects_disabled:
                        level_up_fx.play()
                    self.game_over = 1

                self.rect.x += dx
                self.rect.y += dy
            elif self.game_over == -1:
                self.image = self.dead_image
                if self.death_float < 20:
                    self.rect.y -= 5
                    self.death_float += 1

        screen.blit( self.image, self.rect)
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 2)

    def teleport( self):
        if not paused:
            if self.game_over == 0:
                key = pygame.key.get_pressed()
                
                if key[ pygame.K_UP] and not self.inside:
                    for gate in gates.gate_list:
                        if gate[1].colliderect( self.rect):
                            if gate[2] == -1:
                                if not effects_disabled:
                                    hide_fx.play()
                                self.temp_pos[0] = gate[1].x + tile_size / 2
                                self.temp_pos[1] = gate[1].bottom
                                self.rect.x, self.rect.y = 10000, 10000
                                self.inside = True
                            elif gate[2] > 0:
                                if not effects_disabled:
                                    teleport_fx.play()
                                for teleport_gate in gates.teleport_gates:
                                    if teleport_gate[2] == gate[2] and teleport_gate[3] != gate[3]:
                                        self.rect.x = teleport_gate[1].x + tile_size / 2
                                        self.rect.y =teleport_gate[1].bottom
            elif self.game_over == -1:
                self.image = self.dead_image
                if self.death_float < 20:
                    self.rect.y -= 5
                    self.death_float += 1
        
        screen.blit( self.image, self.rect)
        if draw_rect:
            pygame.draw.rect( screen, ( 255, 255, 255), self.rect, 2)
    
    def reset( self, x, y):
        self.images_right = []
        self.images_right = []
        self.index = 0
        self.counter = 0
        for num in range( 7):
            img_right = pygame.image.load( f"images/player/player_{num}.png")
            img_right = pygame.transform.scale( img_right, ( 45, 85))
            img_left = pygame.transform.flip( img_right, True, False)
            self.images_right.append( img_right.subsurface( img_right.get_rect().x, img_right.get_rect().y,
                    img_right.get_width(), img_right.get_height() - 5))
            self.images_left.append( img_left)
        self.dead_image = pygame.image.load( "images/player/death.png")
        self.image = self.images_right[ self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.temp_pos = [0, 0]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = 0
        self.inside = False
        self.game_over = 0
        self.death_float = 0


class Gate():
    def __init__( self, gate_map):
        self.gate_list = []
        self.teleport_gates = []
        gate_img_1 = pygame.image.load( "images/door/door_1.png")
        gate_img_2 = pygame.image.load( "images/door/door_2.png")
        gate_img_3 = pygame.image.load( "images/door/door_3.png")
        gate_img_4 = pygame.image.load( "images/door/door_4.png")

        gate_id = 0
        row_count = 0
        for row in gate_map:
            col_count = 0
            for gate in row:
                if gate == -3:
                    pass
                elif gate == -2:
                    img = pygame.transform.scale( gate_img_4, ( tile_size * 2, tile_size * 2 + 20))
                    img_rect = img.get_rect()
                    img_rect.x = 2 * tile_size + col_count * img_rect.width + col_count * tile_size
                    img_rect.y = row_count * tile_size + 3 * tile_size * row_count + tile_size - 20
                    gate = ( img, img_rect, gate, gate_id)
                    self.gate_list.append( gate)
                    gate_id += 1
                    gate_coordinates.append( ( img_rect.x, img_rect.y))
                elif gate == -1:
                    img = pygame.transform.scale( gate_img_1, ( tile_size * 2, tile_size * 2 + 20))
                    img_rect = img.get_rect()
                    img_rect.x = 2 * tile_size + col_count * img_rect.width + col_count * tile_size
                    img_rect.y = row_count * tile_size + 3 * tile_size * row_count + tile_size - 20
                    gate = ( img, img_rect, gate, gate_id)
                    self.gate_list.append( gate)
                    gate_id += 1
                    gate_coordinates.append( ( img_rect.x, img_rect.y))
                elif gate == 0:
                    x = 2 * tile_size + col_count * img_rect.width + col_count * tile_size
                    y = row_count * tile_size + 3 * tile_size * row_count + tile_size - 20
                    exit_gate = Exit( x, y)
                    exit_group.add( exit_gate)
                    gate_id += 1
                    gate_coordinates.append( ( img_rect.x, img_rect.y))
                else:
                    img = pygame.transform.scale( gate_img_2, ( tile_size * 2, tile_size * 2 + 20))
                    img_rect = img.get_rect()
                    img_rect.x = 2 * tile_size + col_count * img_rect.width + col_count * tile_size
                    img_rect.y = row_count * tile_size + 3 * tile_size * row_count + tile_size - 20
                    gate = ( img, img_rect, gate, gate_id)
                    self.gate_list.append( gate)
                    self.teleport_gates.append( gate)
                    gate_coordinates.append( ( img_rect.x, img_rect.y))
                col_count += 1
            row_count += 1
    
    def draw( self):
        for gate in self.gate_list:
            screen.blit( gate[0], gate[1])
            if draw_rect:
                pygame.draw.rect( screen, ( 255, 255, 255), gate[1], 2)

class Exit( pygame.sprite.Sprite):
    def __init__( self, x, y):
        pygame.sprite.Sprite.__init__( self)
        img = pygame.image.load( "images/door/door_3.png")
        self.image = pygame.transform.scale( img, ( tile_size * 2, tile_size * 2 + 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Game Functions
def drawGrid():
    for line in range( 0, 60):
        pygame.draw.line(screen, ( 255, 255, 255), ( 0, line * tile_size), ( screen_width, line * tile_size))
        pygame.draw.line(screen, ( 255, 255, 255), ( line * tile_size, 0), ( line * tile_size, screen_width))
    for line in range( 0, 10):
        pygame.draw.line(screen, ( 0, 0, 0), ( 0, line * tile_size * 4), ( screen_width, line * tile_size * 4), 5)
        pygame.draw.line(screen, ( 0, 0, 0), ( line * tile_size * 4, 0), ( line * tile_size * 4, screen_width), 5)

def resetLevel( level):
    global finished
    finished = False
    bg_num = level - 1
    bg_l = pygame.image.load( f"images/background/bg_l{bg[bg_num]}.jpg")
    if level == 6:
        chopper.__init__()
        ladder.__init__()
        retreat = False
        player.reset( tile_size * 5 - 20, screen_height - 75)
    else:
        player.reset( tile_size, screen_height - 75)
    zombies.empty()
    exit_group.empty()
    world = World( level_data.world_maps[ level - 1])
    gates = Gate( level_data.gate_maps[ level - 1])
    return world, gates, bg_l

def retreatSprites( player, chopper, ladder):
    if player.rect.bottom > -10 and not paused:
        player.rect.y -= 1
        chopper.rect.y -= 1
        ladder.rect.y -= 1
    elif player.rect.bottom <= -10:
        player.game_over = -1
        global retreat, finished
        finished = True
        retreat = False

def drawText( text, font, color, x, y):
    img = font.render( text, True, color)
    screen.blit( img, ( x, y))

def fadeIn(width, height): 
    fade = pygame.Surface((width, height))
    fade.fill((255,255,255))
    pygame.mixer.music.pause()
    for alpha in range(0, 300, 1 ):
        fade.set_alpha(alpha)
        redrawWindow()
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(4)


def fadeOut(width,height):
    fade = pygame.Surface((width, height))
    fade.fill((255,255,255))
    pygame.mixer.music.pause()
    for alpha in range(300,0,-3):
        fade.set_alpha(alpha)
        redrawWindow()
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(6)


def redrawWindow():
    screen.blit( bg_l, ( 0, 0))
    world.draw()
    gates.draw()
    zombies.draw( screen)
    exit_group.draw( screen)
    screen.blit( level_img[ level - 1], ( tile_size * 17, tile_size * 13))


# Images
screen = pygame.display.set_mode(( screen_width, screen_height))
pygame.display.set_caption( "Zombies Escape")
bg_l0 = pygame.image.load( f"images/background/bg_l0.jpg")
bg_lb = pygame.image.load( f"images/background/bg_l6b.png")
bg_l = pygame.image.load( f"images/background/bg_l{bg[level - 1]}.jpg")
clock = pygame.time.Clock()

button_bg_img = pygame.image.load( "images/menu/button_bg.png")
button_bg_img = pygame.transform.scale( button_bg_img, (1500, 550))
restart_img = pygame.image.load( "images/button/restart.png")
restart_img = pygame.transform.scale( restart_img, ( 200, 200))
restart_img_2 = pygame.transform.scale( restart_img, ( 150, 150))
menu_img = pygame.image.load( "images/button/menu.png")
menu_img = pygame.transform.scale( menu_img, ( 200, 200))
menu_img_2 = pygame.transform.scale( menu_img, ( 150, 150))
start_img = pygame.image.load( "images/button/start.png")
start_img = pygame.transform.scale( start_img, ( 200, 200))
quit_img = pygame.image.load( "images/button/quit.png")
quit_img = pygame.transform.scale( quit_img, ( 125, 125))
about_img = pygame.image.load( "images/button/about.png")
about_img = pygame.transform.scale( about_img, ( 125, 125))
settings_img = pygame.image.load( "images/button/settings.png")
settings_img = pygame.transform.scale( settings_img, ( 150, 150))
how_to_img = pygame.image.load( "images/button/how_to.png")
how_to_img = pygame.transform.scale( how_to_img, ( 150, 150))
quit_img_2 = pygame.transform.scale( quit_img, ( 100, 100))
music_img = pygame.image.load( "images/button/music.png")
music_img = pygame.transform.scale( music_img, ( 200, 200))
effects_img = pygame.image.load( "images/button/effects.png")
effects_img = pygame.transform.scale( effects_img, ( 200, 200))
disabled_img = pygame.image.load( "images/button/disabled.png")
disabled_img = pygame.transform.scale( disabled_img, ( 200, 200))
prev_img = pygame.image.load( "images/button/prev.png")
prev_img = pygame.transform.scale( prev_img, ( 100, 100))
next_img = pygame.image.load( "images/button/next.png")
next_img = pygame.transform.scale( next_img, ( 100, 100)) 

how_to_menu_img = []
for num in range(1, 6):
    img = pygame.image.load( f"images/menu/tutorial/tutorial_{num}.png")
    img = pygame.transform.scale( img, ( tile_size * 24, tile_size * 16))
    how_to_menu_img.append(img)
about_menu_img = pygame.image.load( "images/menu/about_menu.png")
about_menu_img = pygame.transform.scale( about_menu_img, ( tile_size * 24, tile_size * 16))
game_over_img = pygame.image.load( "images/menu/game_over.png")
finished_img = pygame.image.load( "images/menu/finished.png")
level_img = []
for num in range( 1, max_levels + 1):
    img = pygame.image.load( f"images/menu/l{num}.png")
    img = pygame.transform.scale( img, (400, 250))
    level_img.append( img)
font = pygame.font.SysFont( 'Segoe UI', 70)
logo_img = pygame.image.load( "images/menu/logo.png")
logo_img = pygame.transform.scale( logo_img, ( 700, 700))

# Sounds
pygame.mixer.music.load("music/game.mp3")
if not music_disabled:
    pygame.mixer.music.play(-1, 0.0, 5000)
hide_fx = pygame.mixer.Sound( "music/hide.mp3")
hide_fx.set_volume(0.5)
leave_fx = pygame.mixer.Sound( "music/leave.mp3")
leave_fx.set_volume(0.5)
teleport_fx = pygame.mixer.Sound( "music/teleport.mp3")
teleport_fx.set_volume(0.7)
select_fx = pygame.mixer.Sound( "music/select.mp3")
select_fx.set_volume(0.5)
level_up_fx = pygame.mixer.Sound( "music/level_up.mp3")
level_up_fx.set_volume(0.5)
pause_fx = pygame.mixer.Sound( "music/pause.mp3")
pause_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound( "music/death.mp3")
death_fx.set_volume(0.5)

# Game objects
player = Player( tile_size, screen_height - 75)
world = World( level_data.world_maps[ level - 1])
gates = Gate( level_data.gate_maps[ level - 1])
restart_button = Button(tile_size * 9, screen_height // 2 + 75, restart_img)
menu_button = Button(tile_size * 17, screen_height // 2 + 75, menu_img)
restart_button_2 = Button(tile_size * 8 + 25, screen_height // 2, restart_img_2)
menu_button_2 = Button(tile_size * 19 - 25, screen_height // 2, menu_img_2)
start_button = Button(tile_size * 13, screen_height // 2 + 250, start_img)
start_button_2 = Button(tile_size * 13, screen_height // 2 - 25, start_img)
quit_button = Button(tile_size * 23, screen_height // 2 + 320, quit_img)
about_button = Button(tile_size * 4 + 25, screen_height // 2 + 320, about_img)
settings_button = Button(tile_size * 8 + 25, screen_height // 2 + 290, settings_img)
how_to_button = Button(tile_size * 19 - 25, screen_height // 2 + 290, how_to_img)
quit_button_2 = Button(tile_size * 14, tile_size * 2, quit_img_2)
prev_button = Button(tile_size * 4, tile_size * 2, prev_img)
next_button = Button(tile_size * 24, tile_size * 2, next_img)
music_button = Button(tile_size * 17, screen_height // 2 - 25, music_img)
effects_button = Button(tile_size * 9, screen_height // 2 - 25, effects_img)
disabled_button_1 = Button(tile_size * 17, screen_height // 2 - 25, disabled_img)
disabled_button_2 = Button(tile_size * 9, screen_height // 2 - 25, disabled_img)
chopper = Chopper()
ladder = Ladder()


# Game Loop
while run:
    clock.tick( fps)
    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k and key[pygame.K_c]:
                death = (death + 1) % 2
            if event.key == pygame.K_q:
                run = False
            if event.key == pygame.K_UP:
                if level == 6 and ladder.rect.colliderect( player.rect) and ladder.down:
                        retreat = True
                        player.rect.x = 710
                if teleport == False:
                    player.teleport()
                    teleport = True
                if teleport:
                    teleport = False 
            if event.key == pygame.K_p and key[pygame.K_c]:
                level += 1
                if level == 6:
                    pygame.mixer.music.load("music/chopper.mp3")
                    pygame.mixer.music.play(-1, 0.0, 2000)
                if level <= max_levels:
                    world, gates, bg_l = resetLevel( level)
                    game_over = 0
                else:
                    level = max_levels
            if event.key == pygame.K_o and key[pygame.K_c]:
                retreat = False
                loaded = False
                level -= 1 
                if level == 5:
                    pygame.mixer.music.load("music/game.mp3")
                    pygame.mixer.music.play(-1, 0.0, 2000)
                if level >= 1:
                    world, gates, bg_l = resetLevel( level)
                    game_over = 0
                else:
                    level = 1
            if event.key == pygame.K_l and key[pygame.K_c]:
                if draw_rect == True:
                    draw_rect = False
                else:
                    draw_rect = True
            if event.key == pygame.K_ESCAPE:
                if not any([ main_menu, settings_menu, about_menu, how_to_menu]) and player.game_over != -1:
                    if paused == True:
                        paused = False
                        if not music_disabled:
                            pygame.mixer.music.play(-1, 0.0, 5000)
                    else:
                        if not effects_disabled:
                            pause_fx.play()
                        pygame.mixer.music.pause()
                        paused = True
        
    
    if main_menu:
        pygame.mouse.set_visible( True)
        screen.blit( bg_l0, ( 0, 0))
        screen.blit( button_bg_img, (-150, 560))
        screen.blit( logo_img, ( screen_width // 2 - tile_size * 7, -tile_size * 2))
        if start_button.draw():
            if not effects_disabled:
                select_fx.play()
            pygame.mixer.music.load("music/game.mp3")
            if not music_disabled:
                pygame.mixer.music.play(-1, 0.0, 5000)
            main_menu = False
        if quit_button.draw():
            run = False
        if about_button.draw():
            if not effects_disabled:
                select_fx.play()
            main_menu = False
            about_menu = True
        if settings_button.draw():
            if not effects_disabled:
                select_fx.play()
            main_menu = False
            settings_menu = True
        if how_to_button.draw():
            if not effects_disabled:
                select_fx.play()
            tutorial = 0
            main_menu = False
            how_to_menu = True
    elif how_to_menu:
        screen.blit( bg_l0, ( 0, 0))
        screen.blit( how_to_menu_img[tutorial], (0, 60))
        if quit_button_2.draw():
            if not effects_disabled:
                select_fx.play()
            main_menu = True
            how_to_menu = False
        if prev_button.draw():
            if not effects_disabled:
                select_fx.play()
            tutorial -= 1
            if tutorial < 0:
                tutorial = 0
        if next_button.draw():
            if not effects_disabled:
                select_fx.play()
            tutorial += 1
            if tutorial > 4:
                tutorial = 4
    elif settings_menu:
        screen.blit( bg_l0, ( 0, 0))
        if quit_button_2.draw():
            if not effects_disabled:
                select_fx.play()
            main_menu = True
            settings_menu = False
        if music_button.draw():
            if not effects_disabled:
                select_fx.play()
            if music_disabled:
                music_disabled = False
                pygame.mixer.music.play(-1, 0.0, 5000)
            else:
                music_disabled = True
                pygame.mixer.music.pause()
        if effects_button.draw():
            if not effects_disabled:
                select_fx.play()
            if effects_disabled:
                effects_disabled = False
            else:
                effects_disabled = True
        if effects_disabled:
            disabled_button_2.draw()
        if music_disabled:
            disabled_button_1.draw()
    elif about_menu:
        screen.blit( bg_l0, ( 0, 0))
        screen.blit( about_menu_img, (0, 60))
        if quit_button_2.draw():
            if not effects_disabled:
                select_fx.play()
            main_menu = True
            about_menu = False
    else:
        screen.blit( bg_l, ( 0, 0))
        world.draw()
        gates.draw()
        exit_group.draw( screen)
        if player.game_over == 1:
            level += 1
            if level == 6:
                fadeIn( screen_width,screen_height)
            if level <= max_levels:
                world, gates, bg_l = resetLevel( level)
                game_over = 0
                if level == 6:    
                    fadeOut(screen_width,screen_height)
                    pygame.mixer.music.play(-1, 0.0, 5000)
            else:
                pass
        screen.blit( level_img[ level - 1], ( tile_size * 17, tile_size * 13))
        if player.game_over == 0 and not paused:
            zombies.update()
        zombies.draw( screen)
        if level == 6:
            if not loaded:
                pygame.mixer.music.load("music/chopper.mp3")
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
                loaded = True
            if not chopper.moving:
                ladder.update()
            if not ladder.down:
                screen.blit( bg_lb, ( 0, 0))
            chopper.update()
        player.update()

        if retreat:
            retreatSprites(player, chopper, ladder)
        if paused:
            pygame.mouse.set_visible( True)
            if restart_button_2.draw():
                if not effects_disabled:
                    select_fx.play()
                level = 1
                world, gates, bg_l = resetLevel( level)
                paused = False
                pygame.mixer.music.load("music/game.mp3")
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
                loaded = False
            elif menu_button_2.draw():
                if not effects_disabled:
                    select_fx.play()
                level = 1
                world, gates, bg_l = resetLevel( level)
                main_menu = True
                paused = False
                pygame.mixer.music.load("music/game.mp3")
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
                loaded = False
            elif start_button_2.draw():
                if not effects_disabled:
                    select_fx.play()
                paused = False
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
        if player.game_over == 0 and not paused:
            pygame.mouse.set_visible( False)
        elif player.game_over == -1:
            if not played and level < 6:
                pygame.mixer.music.pause()
                if not effects_disabled:
                    death_fx.play()
                played = True
            pygame.mouse.set_visible( True)
            if finished:
                screen.blit( finished_img, (0, - tile_size * 4))
                loaded = False
                pygame.mixer.music.pause()
            else:
                screen.blit( game_over_img, (0, - tile_size * 4))
            if restart_button.draw():
                if not effects_disabled:
                    select_fx.play()
                played = False
                level = 1
                world, gates, bg_l = resetLevel( level)
                pygame.mixer.music.load("music/game.mp3")
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
            elif menu_button.draw():
                select_fx.play()
                played = False
                level = 1
                world, gates, bg_l = resetLevel( level)
                main_menu = True
                pygame.mixer.music.load("music/game.mp3")
                if not music_disabled:
                    pygame.mixer.music.play(-1, 0.0, 5000)
    if draw_rect:
            drawGrid()
    pygame.display.update()

# Game quitting
pygame.quit()