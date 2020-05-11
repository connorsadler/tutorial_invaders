
import pygamehelper
from pygamehelper import *

#
# Starting point for a pygame game
# Features
# - Easy to use a list of sprites, which gets drawn by a standard routine
# - Easy to create your own sprite classes and add them to the list
# - Easy to allow sprites to die and get removed from the list
# - Game loop is in a class
#


# Global init
pygamehelper.initPygame()

#
# TODO
# Define any sprites you want in here - Make them subclasses of Sprite or SpriteWithImage
#


#
# An Invader
# 
class Invader(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.setImage(["invader1.png", "invader2.png"])

    def move(self):
        self.moveBy(1, 0)
        # TODO: Invader movement when it reaches edge of screen

        # Animation for Invader - every 30 game ticks, we change costume
        if pygamehelper.gameTick % 30 == 0:
            self.nextCostume()

        # TODO: Invader dropping bombs (bullets?)

#
# A Player ship
# 
class PlayerShip(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)

        self.bulletCooldown = 0

    def move(self):
        if self.bulletCooldown > 0:
            self.bulletCooldown -= 1

        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT]:
            self.moveBy(-5, 0)
        if pressed[K_RIGHT]:
            self.moveBy(5, 0)

        if pressed[K_SPACE]:
            if self.bulletCooldown == 0:
                boundingRect = self.getBoundingRect()
                addSprite(Bullet(boundingRect.centerx, self.y))
                self.bulletCooldown = 50

    def draw(self):
        super().draw() # draws a white rectangle for this sprite
        # TODO: PlayerShip drawing

#
# A Bullet
# 
class Bullet(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 15)

    def move(self):
        self.moveBy(0,-3)

    def draw(self):
        super().draw() # draws a white rectangle for this sprite
        # TODO: Bullet drawing - maybe an image?


#
# Game loop logic
#
class MyGameLoop(GameLoop):

    def __init__(self):
        super().__init__()
        #
        # TODO
        # Create any initial instances of your sprites here
        #
        pygamehelper.addSprite(Invader(50, 50))
        pygamehelper.addSprite(PlayerShip(20, 500))

    #
    # TODO
    # This gets called on every frame, before any sprites have been moved or drawn
    # Perform any global game logic here
    #
    def eachFrame(self):
        pass

# Run game loop
MyGameLoop().runGameLoop()
