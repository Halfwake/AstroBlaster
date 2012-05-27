import pyglet
from pyglet.window import key
import time
import random
import Queue

class Game(pyglet.window.Window):
    def __init__(self, width, height):
        super(Game, self).__init__(width, height)
        self.mode = ""
        self.set_caption("AstroBlaster")
        #self.set_icon(IMAGES["ship"]) #Doesn't work, maybe it can't be a png?
        self.background = IMAGES["background"]
        self.fps_display = pyglet.clock.ClockDisplay(color = (200.0, 200.0, 200.5, 200.0))
        self.make_music_players()
        pyglet.clock.set_fps_limit(40) #Makes the game lag go away, no idea why. Maybe the fps goes too fast and it stutters?
        self.switch_mode("menu_screen")
    def make_music_players(self):
        self.ship_screen_music = pyglet.media.Player()
        self.ship_screen_music.queue(SOUNDS["ship_screen"])
        self.ship_screen_music.eos_action = "loop"
        self.menu_screen_music = pyglet.media.Player()
        self.menu_screen_music.queue(SOUNDS["menu_screen"])
        self.menu_screen_music.eos_action = "loop"
        self.credit_screen_music = pyglet.media.Player()
        self.credit_screen_music.queue(SOUNDS["credit_screen"])
        self.credit_screen_music.eos_action = "loop"
    def on_close(self):
        self.ship_screen_music.pause()
        self.menu_screen_music.pause()
        self.credit_screen_music.pause()
        self.close()
    def play_sound(self, music):
        self.ship_screen_music.pause()
        self.menu_screen_music.pause()
        self.credit_screen_music.pause()
        if music == "ship_screen":
            self.ship_screen_music.play()
        elif music == "menu_screen":
            self.menu_screen_music.play()
        elif music == "credit_screen":
            self.credit_screen_music.play()
    def switch_mode(self, mode):
        self.mode = mode
        if mode == "menu_screen":
            self.menu_screen = MenuScreen(self)
            self.ship_screen = None
            self.credit_screen = None
            self.play_sound("menu_screen")
        elif mode == "ship_screen":
            self.ship_screen = ShipScreen(self)
            self.menu_screen = None
            self.credit_screen = None
            self.play_sound("ship_screen")
        elif mode == "credit_screen":
            self.credit_screen = CreditScreen(self)
            #problem here solved by "self.unschedule_events()"
            #in "ShipScreen", thank god!
            self.ship_screen = None
            self.menu_screen = None
            self.play_sound("menu_screen")
    def on_draw(self):
        self.clear()
        self.background.blit(0,0)
        if self.mode == "ship_screen":
            self.ship_screen.on_draw()
            self.fps_display.draw()
        elif self.mode == "menu_screen":
            self.menu_screen.on_draw()
        elif self.mode == "credit_screen":
            self.credit_screen.on_draw()
    def on_key_press(self, symbol, modifiers):
        if self.mode == "ship_screen":
            self.ship_screen.on_key_press(symbol, modifiers)
        elif self.mode == "menu_screen":
            pass
        elif self.mode == "credit_screen":
            pass
    def on_key_release(self, symbol, modifiers):
        if self.mode == "ship_screen":
            self.ship_screen.on_key_release(symbol, modifiers)
        elif self.mode == "menu_screen":
            pass
        elif self.mode == "credit_screen":
            pass
    def on_mouse_press(self, x, y, symbol, modifiers):
        if self.mode == "ship_screen":
            pass
        elif self.mode == "menu_screen":
            self.menu_screen.on_mouse_press(x, y, symbol, modifiers)
        elif self.mode == "credit_screen":
            self.credit_screen.on_mouse_press(x, y, symbol, modifiers)
class CreditScreen():
    def __init__(self, game):
        self.text_size = 20
        self.game = game
        self.score = self.game.ship_screen.score
        self.lives = self.game.ship_screen.lives
        self.shots_fired = self.game.ship_screen.player.shots_fired
        self.aliens_killed = self.game.ship_screen.aliens_killed
        if self.shots_fired == 0:
            self.shot_ratio = 0.0
        else:
            self.shot_ratio = float(self.aliens_killed) / self.shots_fired
        self.make_score_labels()
        self.menu_button = Button(SCREEN_WIDTH / 2,
                   SCREEN_HEIGHT / 4,
                   "menu_button",
                   lambda game : game.switch_mode("menu_screen"))
    def make_score_labels(self):
        self.lives_label = pyglet.text.Label("Lives Left:%d" % self.lives,
                                        font_name = "Comic Sans",
                                        font_size = self.text_size,
                                        x = SCREEN_WIDTH / 2 - 128,
                                        y = SCREEN_HEIGHT / 4 * 1)
        self.score_label = pyglet.text.Label("Total Score:%d" % self.score,
                                        font_name = "Comic Sans",
                                        font_size = self.text_size,
                                        x = SCREEN_WIDTH / 2 - 128,
                                        y = SCREEN_HEIGHT / 4 * 2)
        self.shot_ratio_label = pyglet.text.Label("Accuracy:%1.2f" % self.shot_ratio,
                                        font_name = "Comic Sans",
                                        font_size = self.text_size,
                                        x = SCREEN_WIDTH / 2 - 128,
                                        y = SCREEN_HEIGHT / 4 * 3)
    def on_mouse_press(self, x, y, symbol, modifiers):
        if self.menu_button.position(x, y): self.menu_button.command(self.game)
    def on_draw(self):
        self.lives_label.draw()
        self.score_label.draw()
        self.shot_ratio_label.draw()
        self.menu_button.draw()
class MenuScreen():
    def __init__(self, game):
        self.game = game
        self.start_button = None
        self.exit_button = None
        self.make_menu_buttons()
        self.title = pyglet.sprite.Sprite(IMAGES["title"])
        self.title.x = SCREEN_WIDTH / 2 - self.title.width / 2
        self.title.y = (SCREEN_HEIGHT / 4 * 3) 
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
                                  #lol wat is this below me
                                   lambda : (self.game.play_sound(None) or True) and (self.game.close() or True))
    def on_draw(self):
        self.title.draw()
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
        self.aliens_killed = 0 #self.player.shots_fired = #use this for hit percentage
        self.current_keys = []
        self.score = 0
        self.lives = 3
        self.aliens = []
        self.alien_spawn_rate = 0.5
        self.alien_batch = pyglet.graphics.Batch()
        self.explosion_batch = pyglet.graphics.Batch()
        self.text_size = 20
        self.time = 30
        self.start_timer = 10
        self.explosions = []
        pyglet.clock.schedule_interval(self.decrease_time, 1)
        pyglet.clock.schedule_interval(self.create_aliens, self.alien_spawn_rate)
        pyglet.clock.schedule_interval(self.update, 0.05)
        pyglet.clock.schedule_interval(self.collision_update, 0.05)
        pyglet.clock.schedule_interval(self.unfreeze_laser, self.player.laser_delay)
        pyglet.clock.schedule_interval(self.timer, 1)
        pyglet.clock.schedule_interval(self.delete_explosion, 0.1)
        self.score_text = pyglet.text.Label(str(self.lives),
                                            font_name = "Comic Sans",
                                            font_size = self.text_size,
                                            x = 0,
                                            y = SCREEN_HEIGHT - self.text_size)
        self.lives_text = pyglet.text.Label(str(self.lives),
                                            font_name = "Comic Sans",
                                            font_size = self.text_size,
                                            x = 0,
                                            y = SCREEN_HEIGHT - (2 * self.text_size) - (self.text_size / 5 * 1))
        self.time_text = pyglet.text.Label(str(self.time),
                                            font_name = "Comic Sans",
                                            font_size = self.text_size,
                                            x = 0,
                                            y = SCREEN_HEIGHT - (3 * self.text_size) - (self.text_size / 5 * 2))
    def unschedule_events(self):
        map(pyglet.clock.unschedule,[self.decrease_time,
                                     self.create_aliens,
                                     self.update,
                                     self.collision_update,
                                     self.unfreeze_laser,
                                     self.timer,])
    def decrease_time(self, dt):
        self.time -= 1
    def delete_explosion(self, dt):
        for explosion in self.explosions:
            if explosion.popped == False:
                explosion.popped = True
                explosion.delete_explosion(self.explosions)
    def unfreeze_laser(self, dt):
        if self.game.mode == "ship_screen":
            self.player.laser_wait = False  
    def on_draw(self):
        "Runs every frame"
        self.explosion_batch.draw()
        self.player.draw()
        self.alien_batch.draw()
        self.draw_lives()
        self.draw_score()
        self.draw_time()
    def draw_lives(self):
        self.lives_text.text = str("%s%d" % ("Lives: ", self.lives))
        self.lives_text.draw()
    def draw_score(self):
        self.score_text.text = str("%s%d" % ("Score: ", self.score))
        self.score_text.draw()
    def draw_time(self):
        self.time_text.text = str("%s%d" % ("Time: ", self.time))
        self.time_text.draw()
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
            temp_alien.x = random.randint(0 + temp_alien.width, SCREEN_WIDTH - temp_alien.width)
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
                    self.explosions.append(Explosion(laser.x, laser.y, self.explosion_batch))
                    self.aliens_killed += 1
                    aliens_to_die.add(alien)
                    lasers_to_die.add(laser)
        #These just run through the sets and do the actual deletion.
        for alien in aliens_to_die: alien.die(self.aliens)
        for laser in lasers_to_die: laser.die(self.player.lasers)
    def lose_life(self):
        "Handles life loss, and passes on the method to the 'Player' instance."
        self.lives -= 1
        self.player.lose_life()
    def timer(self, dt):
        if self.time < self.start_timer:
            SOUNDS["timer_beep"].play()
            self.time_text.color = (255,0,0,255)
    def update(self, dt):
        if self.time == 0 or self.lives < 1:
            self.unschedule_events() #cleans up events, also fixes a ton of shit
            SOUNDS["timer_beep"].play()
            SOUNDS["timer_beep"].play()
            self.game.switch_mode("credit_screen")
        if self.game.mode == "ship_screen":
            self.player.update(self.current_keys, dt)
            for alien in self.aliens:
                alien.update(dt, self.aliens)
class Explosion(pyglet.sprite.Sprite):
    def __init__(self, x, y, batch):
        super(Explosion, self).__init__(IMAGES["explosion"])
        self.x = x
        self.y = y
        self.batch = batch
        self.duration = 2
        self.popped = False
    def delete_explosion(self, explosions):
        pyglet.clock.schedule_once(lambda dt : self.clear_batch() and explosions.pop(explosions.index(self)), 0.5)
    def clear_batch(self):
        self.batch = None
        
class Collide(object):
    def collide(self, other):
        center_x = self.x + self.width / 2
        center_y = self.y + self.width / 2
        if other.x < center_x < other.x + other.width:
            if other.y < center_y < other.y + other.height:
                return True
        center_x = other.x + other.width / 2
        center_y = other.y + other.width / 2
        if self.x < center_x < self.x + self.width:
            if self.y < center_y < self.y + self.height:
                return True
        return False
        
class Alien(pyglet.sprite.Sprite, Collide):
    "Alien class for aliens that attack player"
    def __init__(self, x, y, batch):
        super(Alien, self).__init__(IMAGES["alien"])
        self.batch = batch
        self.x = x
        self.y = y
        self.speed = 150
        self.points = 100
    def update(self, dt, aliens):
        if self.y + self.height < 0:
            aliens.remove(self)
        self.y -= self.speed * dt
    def die(self, aliens):
        aliens.remove(self)
        
class Ship(pyglet.sprite.Sprite, Collide):
    def __init__(self):
        super(Ship, self).__init__(IMAGES["ship"])
        self.shots_fired = 0 #Maybe useful
        self.speed = 250
        self.scale = 1.0
        self.laser_delay = 0.5
        self.laser_wait = False
        self.lasers = []
        self.laser_batch = pyglet.graphics.Batch()
        self.x = SCREEN_WIDTH / 2
        self.y = 0 + self.height
    def update(self, current_keys, dt):
        "Takes a list of keys being held down and delta time, it moves the player, and fires lasers PEW PEW"
        for laser in self.lasers:
            laser.update(dt, self.lasers)
        for current_key in current_keys:
            if current_key == key.UP:
                if self.height + self.y + self.speed * dt < SCREEN_HEIGHT: self.y += self.speed * dt
            elif current_key == key.DOWN:
                if self.y - self.speed * dt > 0: self.y -= self.speed * dt
            elif current_key == key.RIGHT:
                if self.width + self.x + self.speed * dt < SCREEN_WIDTH: self.x += self.speed * dt
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
        self.shots_fired += 1
        self.lasers.append(Laser(self.x + (self.width / 2) - 4, self.y + self.height / 2, self.laser_batch))
    def lose_life(self):
        "Causes the player to act as if they loss a life, the method that calls this one actaully effects the 'Game.lives' arg"
        pass
class Laser(pyglet.sprite.Sprite, Collide):
    def __init__(self, x, y, batch):
        super(Laser, self).__init__(IMAGES["laser"])
        self.batch = batch
        self.x = x
        self.y = y
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
    try: #This will install avbin if needed, and it works on windows and linux!
        pyglet.resource.image("resources/ship.png")
    except:
        if sys.platform.startswith("win"):
            raise "Error: avbin.dll not found."
        elif sys.platform.startswith("linux"):
            os.system("avbin-linux-x86-32-7/install.sh")
        elif sys.platform == "dawrwin":
            #Note, osx doesn't work because the avbin devs don't care about it
            #and left it in the dust. Just a small town OS living in a
            #dangerious dog eat world. Lost it all at the gambling games.
            #Working hard to fight the man. Didn't even really have a plan.
            #But hey, man? You gotta work. Work. Work this out. Get ahead.
            #You gotta work. Work. Work this out. Get ahead. Ah yeah!
            raise "Error: This game is not supported on OSX."
            os.system("avbin-darwin-universal-5/install.sh")
    #Dicts of image and sound objects as a constant for effeciency
    IMAGES = {"ship" : pyglet.resource.image("resources/ship.png"),
              "laser" : pyglet.resource.image("resources/laser.png"),
              "alien" : pyglet.resource.image("resources/alien.png"),
              "background" : pyglet.resource.image("resources/background.png"),
              "start_button" : pyglet.resource.image("resources/start_button.png"),
              "exit_button" : pyglet.resource.image("resources/exit_button.png"),
              "menu_button" : pyglet.resource.image("resources/menu_button.png"),
              "title" : pyglet.resource.image("resources/title.png"),
              "explosion" : pyglet.resource.animation('resources/kboom.gif')}
    SOUNDS = {"menu_screen" : pyglet.media.load("resources/menu1.ogg"),
              "ship_screen" : pyglet.media.load("resources/game1.ogg"),
              "credit_screen" : pyglet.media.load("resources/credit1.ogg"),
              "timer_beep" : pyglet.media.load("resources/beep-7.ogg", streaming = False),
              "laser" : pyglet.media.load("resources/laser1.ogg", streaming = False)}
    root = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    pyglet.app.run()
