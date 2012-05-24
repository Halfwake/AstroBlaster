import pyglet
from pyglet.window import key
import time
import random

class Game(pyglet.window.Window):
    def __init__(self, width, height):
        super(Game, self).__init__(width, height)
        self.mode = ""
        self.background = IMAGES["background"]
        self.ship_screen = ShipScreen(self)
        self.menu_screen = MenuScreen(self)
        self.fps_display = pyglet.clock.ClockDisplay(color = (200.0, 200.0, 200.5, 200.0))
        self.music_player = pyglet.media.Player()
        self.switch_mode("menu_screen")
        self.music_player.eos_action = "loop"
    def on_close(self):
        self.music_player.pause()
        self.close()
    def switch_mode(self, mode):
        self.mode = mode
        if mode == "menu_screen":
            self.music_player.pause()
            self.music_player.next()
            self.music_player.queue(SOUNDS["menu_screen"])
            self.music_player.play()
        elif mode == "ship_screen":
            self.music_player.pause()
            self.music_player.next()
            self.music_player.queue(SOUNDS["ship_screen"])
            self.music_player.play()
    def on_draw(self):
        self.clear()
        if self.mode == "ship_screen":
            self.background.blit(0,0)
            self.ship_screen.on_draw()
            self.fps_display.draw()
        elif self.mode == "menu_screen":
            self.menu_screen.on_draw()
    def on_key_press(self, symbol, modifiers):
        if self.mode == "ship_screen":
            self.ship_screen.on_key_press(symbol, modifiers)
        elif self.mode == "menu_screen":
            pass
    def on_key_release(self, symbol, modifiers):
        if self.mode == "ship_screen":
            self.ship_screen.on_key_release(symbol, modifiers)
        elif self.mode == "menu_screen":
            pass
    def on_mouse_press(self, x, y, symbol, modifiers):
        if self.mode == "ship_screen":
            pass
        elif self.mode == "menu_screen":
            self.menu_screen.on_mouse_press(x, y, symbol, modifiers)

class MenuScreen():
    def __init__(self, game):
        self.game = game
        self.start_button = None
        self.exit_button = None
        self.make_menu_buttons()
    def on_mouse_press(self, x, y, symbol, modifiers):
        if self.start_button.position(x, y): self.start_button.command(self.game)
        if self.exit_button.position(x, y): self.exit_button.command()
    def make_menu_buttons(self):
        self.start_button = Button(SCREEN_WIDTH / 2,
                                   SCREEN_HEIGHT / 2,
                                   "start_button",
                                   lambda game : game.switch_mode("ship_screen"))
        self.exit_button = Button(SCREEN_WIDTH / 2,
                                   SCREEN_HEIGHT / 4,
                                   "exit_button",
                                   lambda : (self.game.music_player.pause() or True) and (self.game.close() or True))
    def on_draw(self):
        self.start_button.draw()
        self.exit_button.draw()
class Button(pyglet.sprite.Sprite):
    def __init__(self, x, y, image, command):
        super(Button, self).__init__(IMAGES[image])
        self.x = x - self.width / 2
        self.y = y - self.height / 2
        self.command = command
    def position(self, x, y):
        if self.x < x < self.x + self.width:
            if self.y < y < self.y + self.height:
                return True
        return False
class ShipScreen():
    "The main game class for the main instance."
    def __init__(self, game):
        self.game = game
        self.player = Ship()
        self.events = []
        self.current_keys = []
        self.score = 0
        self.lives = 3
        self.aliens = []
        self.alien_spawn_rate = 0.5
        self.alien_batch = pyglet.graphics.Batch()
        self.text_size = 20
        pyglet.clock.schedule_interval(self.create_aliens, self.alien_spawn_rate)
        pyglet.clock.schedule_interval(self.update, 0.05)
        pyglet.clock.schedule_interval(self.collision_update, 0.10)
        pyglet.clock.schedule_interval(self.unfreeze_laser, self.player.laser_delay)
        self.score_text = pyglet.text.Label(str(self.lives),
                                            font_name = "Comic Sans",
                                            font_size = self.text_size,
                                            x = 0,
                                            y = SCREEN_HEIGHT - self.text_size)
        self.lives_text = pyglet.text.Label(str(self.lives),
                                            font_name = "Comic Sans",
                                            font_size = self.text_size,
                                            x = 0,
                                            y = SCREEN_HEIGHT - (2 * self.text_size))
    def unfreeze_laser(self, dt):
        if self.game.mode == "ship_screen":
            self.player.laser_wait = False  
    def on_draw(self):
        "Runs every frame"
        self.player.draw()
        self.alien_batch.draw()
        self.draw_lives()
        self.draw_score()
    def draw_lives(self):
        self.lives_text.text = str(self.lives)
        self.lives_text.draw()
    def draw_score(self):
        self.score_text.text = str(self.score)
        self.score_text.draw()
    def on_key_press(self, symbol, modifiers):
        "Runs every key press, adds held down keys to list of held down keys."
        self.current_keys.append(symbol)
    def on_key_release(self, symbol, modifiers):
        "Runs every key release, removes held down keys from list of held down keys."
        self.current_keys.remove(symbol)
    def create_aliens(self, dt):
        "Spawns aliens periodically."
        if self.game.mode == "ship_screen":
            temp_alien = Alien(0,0, self.alien_batch)
            temp_alien.x = random.randint(0 + temp_alien.display_width, SCREEN_WIDTH - temp_alien.display_width)
            temp_alien.y = SCREEN_HEIGHT
            self.aliens.append(temp_alien)
    def collision_update(self, dt):
        "Handles collision between game objects."
        #These need to be sets because the for loop can add items twice
        #and if we try to remove the same object twice everything will
        #blow up. More importantly we need seperate variables because
        #mutating lists as you iterate them seems like a pretty stupid
        #idea.
        aliens_to_die = set()
        lasers_to_die = set()
        for alien in self.aliens:
            if alien.collide(self.player):
                aliens_to_die.add(alien)
                self.lose_life()
            for laser in self.player.lasers:
                if alien.collide(laser):
                    self.score += alien.points
                    aliens_to_die.add(alien)
                    lasers_to_die.add(laser)
        #These just run through the sets and does the actual deletion.
        for alien in aliens_to_die: alien.die(self.aliens)
        for laser in lasers_to_die: laser.die(self.player.lasers)
    def lose_life(self):
        "Handles life loss, and passes on the method to the 'Player' instance."
        self.lives -= 1
        self.player.lose_life()
    def update(self, dt):
        if self.game.mode == "ship_screen":
            self.player.update(self.current_keys, dt)
            for alien in self.aliens:
                alien.update(dt, self.aliens)

class Collide():
    def collide(self, other):
        center_x = self.x + self.display_width / 2
        center_y = self.y + self.display_width / 2
        if other.x < center_x < other.x + other.display_width:
            if other.y < center_y < other.y + other.display_height:
                return True
        center_x = other.x + other.display_width / 2
        center_y = other.y + other.display_width / 2
        if self.x < center_x < self.x + self.display_width:
            if self.y < center_y < self.y + self.display_height:
                return True
        return False
        
class Alien(pyglet.sprite.Sprite, Collide):
    "Alien class for aliens that attack player"
    def __init__(self, x, y, batch):
        super(Alien, self).__init__(IMAGES["alien"])
        self.batch = batch
        self.x = x
        self.y = y
        self.display_width = 64
        self.display_height = 64
        self.speed = 200
        self.points = 100
    def update(self, dt, aliens):
        if self.y + self.display_height < 0:
            aliens.remove(self)
        self.y -= self.speed * dt
    def die(self, aliens):
        aliens.remove(self)
        
class Ship(pyglet.sprite.Sprite, Collide):
    def __init__(self):
        super(Ship, self).__init__(IMAGES["ship"])
        self.display_height = 64
        self.display_width = 64
        self.speed = 250
        self.scale = 1.0
        self.laser_delay = 0.5
        self.laser_wait = False
        self.lasers = []
        self.laser_batch = pyglet.graphics.Batch()
        self.x = SCREEN_WIDTH / 2
        self.y = 0 + self.display_height
    def update(self, current_keys, dt):
        "Takes a list of keys being held down and delta time, it moves the player, and fires lasers PEW PEW"
        for laser in self.lasers:
            laser.update(dt, self.lasers)
        for current_key in current_keys:
            if current_key == key.UP:
                if self.display_height + self.y + self.speed * dt < SCREEN_HEIGHT: self.y += self.speed * dt
            elif current_key == key.DOWN:
                if self.y - self.speed * dt > 0: self.y -= self.speed * dt
            elif current_key == key.RIGHT:
                if self.display_width + self.x + self.speed * dt < SCREEN_WIDTH: self.x += self.speed * dt
            elif current_key == key.LEFT:
                if self.x - self.speed * dt > 0: self.x -= self.speed * dt
            elif current_key == key.SPACE:
                if not self.laser_wait:
                    self.laser_wait = True
                    self.make_laser()
    def draw(self):
        "Draws this ship and all instances relying on it to be drawn (lasers)"
        self.laser_batch.draw()
        super(Ship, self).draw()
    def make_laser(self):
        "Makes a laser and adds it to the player instances list of lasers"
        SOUNDS["laser"].play()
        self.lasers.append(Laser(self.x + (self.display_width / 2) - 4, self.y + self.display_height / 2, self.laser_batch))
    def lose_life(self):
        "Causes the player to act as if they loss a life, the method that calls this one actaully effects the 'Game.lives' arg"
        pass
class Laser(pyglet.sprite.Sprite, Collide):
    def __init__(self, x, y, batch):
        super(Laser, self).__init__(IMAGES["laser"])
        self.batch = batch
        self.x = x
        self.y = y
        self.display_height = 64
        self.display_width = 4
        self.speed = 300
    def update(self, dt, lasers):
        "Moves the laser up, and if it goes outside the screen it's removed from the 'lasers' var passed in from 'Player'."
        if self.y > SCREEN_HEIGHT:
            self.die(lasers)
        else:
            self.y += self.speed * dt
    def die(self, lasers):
        lasers.remove(self)
    

if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
    #Dict of image objects as a constant for effeciency
    IMAGES = {"ship" : pyglet.resource.image("resources/ship.png"),
              "laser" : pyglet.resource.image("resources/laser.png"),
              "alien" : pyglet.resource.image("resources/alien.png"),
              "background" : pyglet.resource.image("resources/background.png"),
              "start_button" : pyglet.resource.image("resources/start_button.png"),
              "exit_button" : pyglet.resource.image("resources/exit_button.png")}
                ###NEED TO ADD MENU BUTTON IMAGES
    SOUNDS = {"menu_screen" : pyglet.media.load("resources/menu1.ogg"),
              "ship_screen" : pyglet.media.load("resources/game1.ogg"),
              "laser" : pyglet.media.load("resources/laser1.ogg", streaming = False)}
    root = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    pyglet.app.run()
