
import pygamehelper
from pygamehelper import *

#
# Starting point for Invaders game
# Features
# - TODO
#
# TODO: Bases that you can shoot past
#       In the first version of that you can just make bullets die when they hit a base
#       In the more advanced version you can allow bullets to slowly destroy a base when they hit it

# TODO: Invader dropping bombs (different type of bullets)



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
        self.setImages(["images/invader1.png", "images/invader2.png"])

        self.movex = 3

        self.setCollisionDetectionEnabled(True)

    def move(self):
        self.moveBy(self.movex, 0)
        # TODO: Invader movement when it reaches edge of screen
        if not self.isOnScreen():
            print("reverse at: " + str(self.getLocation()))
            self.movex = self.movex * -1

        # Animation for Invader - every 30 game ticks, we change costume
        if pygamehelper.gameTick % 30 == 0:
            self.nextCostume()

    def handleCollisions(self, collidedWithSprites):
        for collidedWithSprite in collidedWithSprites:
            self.setDead(True)
            collidedWithSprite.setDead(True)
            # Create Explosion
            addSprite(Explosion(self.x, self.y))

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
                addSprite(Bullet(boundingRect.centerx-5, self.y-10))
                self.bulletCooldown = 50

    def draw(self):
        super().draw() # draws a white rectangle for this sprite
        boundingRect = self.getBoundingRect()
        # Draw gun turret above white rectangle
        drawRect((boundingRect.centerx-5,self.y,10,-10), white)

#
# A Bullet
# 
class Bullet(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 15)

    def move(self):
        self.moveBy(0,-6)

    def draw(self):
        super().draw() # draws a white rectangle for this sprite
        # TODO: Bullet drawing - maybe an image?

#
# An Explosion
# 
class Explosion(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.setImages(["images/explosion_blue_1.png", "images/explosion_blue_2.png", "images/explosion_blue_3.png"])

    def move(self):
        if pygamehelper.gameTick % 15 == 0:
            self.nextCostume()
            if self.getCostumeIndex() == 0:
                self.setDead(True)

    # No need for a 'draw' method as the Sprite class will do all that for us


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

pygamehelper.debug = False
# Run game loop
MyGameLoop().runGameLoop()
