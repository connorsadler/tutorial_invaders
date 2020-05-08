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
# A Box moves around the screen
# and bounces
# 
class Box(Sprite):
    def __init__(self, x, y, angle, sizex, sizey):
        super().__init__(x, y, sizex, sizey)
        self.angle = angle
        self.setBounceOfEdgeOfScreen()

    def move(self):
        self.moveForward(5)

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
        # Create a couple of boxes which will bounce around
        pygamehelper.addSprite(Box(20, 20, 110, 70, 125))
        pygamehelper.addSprite(Box(20, 300, 45, 90, 90))
        # TODO: You can add more boxes here if you like
        #pygamehelper.addSprite(Box(20, 150, 45, 90, 90))


    #
    # TODO
    # This gets called on every frame, before any sprites have been moved or drawn
    # Perform any global game logic here
    #
    def eachFrame(self):
        pass

# Run game loop
MyGameLoop().runGameLoop()
