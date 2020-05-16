
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
    def __init__(self, x, y, speed = 3):
        super().__init__(x, y)
        self.setImages(["images/invader1.png", "images/invader2.png"])

        self.movex = speed

        self.setCollisionDetectionEnabled(True)

    def move(self):
        # Move left or right
        self.moveBy(self.movex, 0)
        # When invader reaches edge of screen, move down and reverse left-right direction
        if self.x > screenRect.width or self.x < 0:
            self.moveBy(0, 20)
            self.movex = self.movex * -1

        # Animation for Invader - every 30 game ticks, we change costume
        if pygamehelper.gameTick % 30 == 0:
            self.nextCostume()

    def handleCollisions(self, collidedWithSprites):
        for collidedWithSprite in collidedWithSprites:
            if isinstance(collidedWithSprite, Bullet):
                # Remove both sprites involved in the collision
                self.setDead(True)
                collidedWithSprite.setDead(True)
                # Create Explosion
                addSprite(Explosion(self.x, self.y))
                # Add to score
                self.broadcastMessage("addToScore", 10)

#
# A Player ship
# 
class PlayerShip(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)
        # Only allow the player to fire if bulletCooldown is 0
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
            # Only allow the player to fire if bulletCooldown is 0 - prevents them firing too frequently
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
# Scoreboard
#
class Scoreboard(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.score = 0
        self.level = 1

    def move(self):
        pass

    def draw(self):
        drawText("Score: " + str(self.score), self.x, self.y, pygamehelper.largeFont, green)
        drawText("Level: " + str(self.level), self.x, self.y + 20, pygamehelper.largeFont, green)

    def addToScore(self):
        self.score += 1



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
        self.scoreboard = Scoreboard(screenRect.width - 150, 20)
        pygamehelper.addSprite(self.scoreboard)

        # If a random number 1-10000 is greater than this tolerance, a new invader will be created
        self.invaderCreationTolerance = 9950

        self.listenForMessage("addToScore", self.addToScore)

    def addToScore(self, data):
        self.scoreboard.addToScore()
        if self.scoreboard.score % 5 == 0:
            self.scoreboard.level += 1
            self.invaderCreationTolerance -= 30

    #
    # TODO
    # This gets called on every frame, before any sprites have been moved or drawn
    # Perform any global game logic here
    #
    def eachFrame(self):
        if random.randint(1, 10000) > self.invaderCreationTolerance:
            # TODO: Could increase speed depending on level
            pygamehelper.addSprite(Invader(50, 50, 3))


pygamehelper.debug = False
# Run game loop
MyGameLoop().runGameLoop()
