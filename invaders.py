
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
        super().__init__(x, y, 50,50)
        self.setImage("invader.png")
        self.setAngle(90)

    def move(self):
        self.moveForward(3)

    def handleCollisions(self, collidedWithSprites):
        pass

    def draw(self):
        super().draw()

#
# A Player ship
# 
class PlayerShip(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)
        self.setAngle(90)

    def move(self):
        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT]:
            self.moveBy(-5, 0)
        if pressed[K_RIGHT]:
            self.moveBy(5, 0)

    def draw(self):
        super().draw() # draws a white rectangle for this sprite


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
        pygamehelper.addSprite(PlayerShip(20, 300))

    #
    # TODO
    # This gets called on every frame, before any sprites have been moved or drawn
    # Perform any global game logic here
    #
    def eachFrame(self):
        pass

# Run game loop
MyGameLoop().runGameLoop()
