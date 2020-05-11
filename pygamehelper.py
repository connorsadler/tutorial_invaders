#
# helper library to help with pygame games
#

print("DigiLocal pygamehelper.py is running")

import pygame, sys
from pygame.locals import *
import random
import math
import os
import enum

display_width = 800
display_height = 600
screenRect = pygame.Rect(0, 0, display_width, display_height)
centreOfScreen = (display_width/2, display_height/2)

centreOfScreenVector = pygame.math.Vector2(centreOfScreen)

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
redalt = (150,10,15)
redbright = (250,10,15)
blue =(0,0,160)
dark_green = (54, 102, 22)
green = (0, 128, 0)
yellow1 = (236, 245, 66)
purple = (255, 0, 255)
yellow = (255, 255, 0)
teal = (0, 255, 255)
lightgray = (128, 128, 128)
colours = [red, blue, green, purple, yellow, teal]
transparentColour = (0,0,0,0)
transparentColor = transparentColour

def getScreenRect():
    return screenRect

class Sprite():

    #
    # width/height - If you plan on using an image, you can omit both of these values.
    #                The sprite's height/width will be set automatically - they'll be available in self.boundingRect
    # 
    def __init__(self, x, y, width=0, height=0, imageFilenameOrFilenamesOrImageHandler = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # for debugging
        self.debugDrawBoundingRect = False
        # init this here to setup an initial value - sometimes when a sprite is added by another sprite at a certain point in the sequence, it won't have had it's moveDone called
        self.boundingRect = pygame.Rect(self.x, self.y, self.width, self.height)
        # to kill a sprite (i.e. remote it from the game) you can either:
        #    1. set self.dead to True
        # or 2. implement a function checkDead in your Sprite subclass, and return a list of sprites which you want to die on that frame of the game
        self.dead = False
        # by default sprites don't check collisions
        self.collisionDetectionEnabled = False
        # edge of screen checker
        self.edgeOfScreenChecker = None
        # angle the sprite is 'facing' i.e. the angle it's image will be rotated to if it has an image
        self.angle = 0

        # Don't overwrite self.imageDrawingHelper if it's already set by a subclass
        if not hasattr(self, "imageDrawingHelper"):
            self.imageDrawingHelper = None

        # Clip area to use when actually drawing the image
        self.clipArea = None

        # Optional object to handle movement of this sprite
        # If one of these is installed, the default "move" method must be called by the Sprite subclass
        self.moveHandler = None

        # Optional image
        if imageFilenameOrFilenamesOrImageHandler != None:
            self.setImage(imageFilenameOrFilenamesOrImageHandler) # NOTE: Untested

    def setAngle(self, newAngle):
        self.angle = newAngle

    def getAngle(self):
        return self.angle

    def rotateBy(self, angleChange):
        self.angle += angleChange

    def pointTo(self, point):
        # changes our angle so we're pointing from our current location towards "point"
        v = subtractVectors(point, self.getLocation())
        angle = vectorToAngle(v)
        self.setAngle(angle)
        #print("angle: " + str(angle))

    def getLocation(self):
        return (self.x, self.y)
    
    # Alternately you can use: setLocationAnimated
    def setLocation(self, location):
        self.x = location[0]
        self.y = location[1]

    def setLocationAnimated(self, location, speed = 1):
        path = Path()
        path.addWaypoint(location[0], location[1])
        pathFollowMoveHandler = PathFollowMoveHandler.installForSprite(self, path)
        pathFollowMoveHandler.setSpeed(speed)
        # At end of path, clear the moveHandler to stop the animation
        pathFollowMoveHandler.setEndOfPathHook(self.clearMoveHandler)

    def clearMoveHandler(self):
        print("clearMoveHandler running")
        self.moveHandler = None

    def moveBy(self, xvel, yvel):
        self.x += xvel
        self.y += yvel

    def moveByVector(self, v):
        self.moveBy(v[0], v[1])

    def moveForward(self, amount):
        (dx, dy) = resolveAngle(self.angle, amount)
        self.x += dx
        self.y += dy

    def move(self):
        # Call moveHandler delegate if installed
        if self.moveHandler:
            self.moveHandler.move(self)

    def moveDone(self):
        if self.imageDrawingHelper:
            self.imageDrawingHelper.moveDone()
        else:
            self.boundingRect = pygame.Rect(self.x, self.y, self.width, self.height)

    def setMoveHandler(self, moveHandler):
        self.moveHandler = moveHandler

    def getMoveHandler(self):
        return self.moveHandler

    def isOnScreen(self):
        return self.boundingRect.colliderect(getScreenRect())

    # returns:
    #   2 - completely on screen
    #   1 - touching edge of screen
    #   0 - complete off screen
    # TODO: Returning an int is rather iffy - needs to use an enumerated type, can you do that in Python?
    def isOnScreenEx(self):
        if getScreenRect().contains(self.boundingRect):
            return 2
        return 1 if self.isOnScreen() else 0

    def setBounceOfEdgeOfScreen(self):
        self.edgeOfScreenChecker = BounceSprite_EdgeOfScreenChecker()

    def setDieOnEdgeOfScreen(self):
        self.edgeOfScreenChecker = KillSprite_EdgeOfScreenChecker()

    def checkEdgeOfScreen(self):
        if self.edgeOfScreenChecker:
            self.edgeOfScreenChecker.checkEdgeOfScreen(self)

    def bounceOnEdgeOfScreen(self):
        resolveBounce(self)

    def isCollisionDetectionEnabled(self):
        return self.collisionDetectionEnabled

    # If you set this to true, please override handleCollisions in your Sprite subclass
    def setCollisionDetectionEnabled(self, collisionDetectionEnabled):
        self.collisionDetectionEnabled = collisionDetectionEnabled

    def checkCollisions(self):
        collidedWithSprites = findCollisions(self)
        if len(collidedWithSprites) > 0:
            self.handleCollisions(collidedWithSprites)
    
    def handleCollisions(self, collidedWithSprites):
        pass

    # find list of sprites that we're overlapping
    def findSpritesOverlapping(self):
        return findCollisions(self)

    # does this sprite overlap otherSprite
    def isOverlapping(self, otherSprite):
        return self.getBoundingRect().colliderect(otherSprite.getBoundingRect())

    def draw(self):
        if self.imageDrawingHelper:
            if self.debugDrawBoundingRect:
                pygame.draw.rect(gameDisplay, white, self.boundingRect)
            # If there's a drawing delegate, we use it - this can draw a rotated image for example
            self.imageDrawingHelper.draw()
        else:
            # If there's an imageDrawingHelper, we dont draw the white background for this sprite
            # By default our rect starts from x,y and extends by width-height
            pygame.draw.rect(gameDisplay, white, self.boundingRect)

    def setDrawMode(self, drawMode):
        self.imageDrawingHelper.setDrawMode(drawMode)

    def getBoundingRect(self):
        return self.boundingRect

    def setDead(self, dead):
        self.dead = dead

    def checkDead(self):
        # Simple way to kill a sprite
        # If you wish to use a more advanced way to kill sprites, then please implement your own checkDead method in your Sprite subclass
        if self.dead:
            return [self]
        return []
    
    def onDeathSpawn(self):
        return []
    
    # Called when the sprite is removed on death
    # By default this does nothing but can be used as a hook to run logic on sprite death
    def onDeath(self):
        pass

    def drawDebug(self):
        pygame.draw.rect(gameDisplay, red, self.boundingRect, 1)

    def setCostume(self, costumeIndex):
        self.changeCostume(costumeIndex)

    # Only works if we have a self.imageDrawingHelper
    def changeCostume(self, costumeIndex):
        if self.imageDrawingHelper:
            self.imageDrawingHelper.changeCostume(costumeIndex)
        else:
            print("changeCostume called with no imageDrawingHelper, costumeIndex: " + str(costumeIndex))

    # Changes to the next costume. If we've reached the last costume, go back to the first one
    # Only works if we have a self.imageDrawingHelper
    def nextCostume(self):
        if self.imageDrawingHelper:
            self.imageDrawingHelper.nextCostume()
        else:
            print("nextCostume called with no imageDrawingHelper")

    def withTimeout(self, timeoutTicks):
        self.moveHandler = MoveHandlerTimeout(self, timeoutTicks)
        return self

    def setImage(self, imageFilenameOrFilenamesOrImageHandler):
        self.imageDrawingHelper = SpriteImageDrawingHelper(self, imageFilenameOrFilenamesOrImageHandler)

#
# This is reduced in size now and could maybe be deleted
#
class SpriteWithImage(Sprite):
    def __init__(self, x, y, imageFilenameOrFilenamesOrImageHandler):
        super().__init__(x, y)
        self.imageDrawingHelper = SpriteImageDrawingHelper(self, imageFilenameOrFilenamesOrImageHandler)

class SpriteWithText(Sprite):
    def __init__(self, x, y, width, height, text, font, colour):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.colour = colour

    def draw(self):
        drawText(self.text, self.x, self.y, self.font, self.colour)

class DrawMode(enum.Enum):
    XY_IS_UPPER_LEFT = enum.auto()
    XY_IS_CENTRE = enum.auto()

# 
# Helper class which implements a Sprite with image (or images aka costumes)
# This also can optionally rotate the images
# You can change costume by calling: changeCostume(0) for first costume, etc
#
class SpriteImageDrawingHelper():
    # imageFilenameOrFilenamesOrImageHandler can be either:
    # - an image file name
    # - a list of image file names (different costumes)
    # - a custom ImageHandlerBase
    def __init__(self, sprite, imageFilenameOrFilenamesOrImageHandler):
        super().__init__()

        self.sprite = sprite

        # Create an imageHandler or use the custom one supplied
        if isinstance(imageFilenameOrFilenamesOrImageHandler, ImageHandlerBase):
            self.imageHandler = imageFilenameOrFilenamesOrImageHandler
        else:
            self.imageHandler = ImageHandler(imageFilenameOrFilenamesOrImageHandler)

        # Default to no extra sprite image preparation (drawing) - can be overridden later by the subclass
        self.extraSpriteImagePreparer = None

        # Set the size of the sprite now - not exactly sure what sprite width/height get used for TODO: Maybe we can tidy that up?
        imageSize = self.getSpriteImage().get_size()
        self.sprite.width = imageSize[0]
        self.sprite.height = imageSize[1]

        # Default to drawing the sprite with the centre of it's image at x,y
        # This can be changed to draw with x,y as top left instead if required
        self.drawMode = DrawMode.XY_IS_CENTRE

    def setDrawMode(self, drawMode):
        self.drawMode = drawMode

    def changeCostume(self, costumeIndex):
        self.imageHandler.changeCostume(costumeIndex)

    def nextCostume(self):
        self.imageHandler.nextCostume()

    def addExtraSpriteImagePreparer(self, extraSpriteImagePreparer):
        self.extraSpriteImagePreparer = extraSpriteImagePreparer

    def getSpriteImage(self):
        return self.imageHandler.getSpriteImage()

    # prepare the image (from the current costume image)
    # optionally rotate the image
    # update our sprite's bounding box
    def moveDone(self):
        imageToDraw = self.prepareSpriteImage()
        # Optionally rotate the image
        if self.sprite.angle != 0:
            # rotate does counterclockwise rotation, but we want clockwise
            self.imageRotated = pygame.transform.rotate(imageToDraw, -1 * self.sprite.angle)
        else:
            self.imageRotated = imageToDraw
        # Not sure how important sprite.width/height are TODO: Maybe we can tidy that up?
        self.sprite.width = self.imageRotated.get_size()[0]
        self.sprite.height = self.imageRotated.get_size()[1]
        if self.drawMode == DrawMode.XY_IS_CENTRE:
            boundingRect = calcBoundingRectCenteredOnXY(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)
        else:
            boundingRect = pygame.Rect(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)
        self.sprite.boundingRect = boundingRect

    def prepareSpriteImage(self):
        result = self.imageHandler.getSpriteImage()
        if self.extraSpriteImagePreparer:
            # copy the current costume as we're about to do some custom drawing onto it
            result = result.copy()
            self.extraSpriteImagePreparer.prepareSpriteImageExtra(result)
        return result

    def draw(self):
        if self.drawMode == DrawMode.XY_IS_CENTRE:
            # draw the image, centred on x,y - so that any rotation looks good
            drawImageCentered(self.imageRotated, self.sprite.x, self.sprite.y, self.sprite.clipArea)
        else:
            drawImage(self.imageRotated, self.sprite.x, self.sprite.y, self.sprite.clipArea)

# Try to find an image file given a base name e.g. invader.jpg
# We can try whatever prefixes we like
# This allows us to use Visual Studio Code and open the parent dir of "pygamehelperpublic" rather than that exact dir
# and then 'run' will set the working dir to that parent dir
# so we need to try looking in the "pygamehelperpublic" subdir for images
def resolveImageFile(imageFilename):
    print("resolveImageFile: " + imageFilename)

    # Try current dir
    modifiedName = imageFilename
    if os.path.isfile(modifiedName):
        print("-> resolved to: " + modifiedName)
        return imageFilename
    
    # Try pygamehelperpublic dir
    modifiedName = "./pygamehelperpublic/" + imageFilename
    if os.path.isfile(modifiedName):
        print("-> resolved to: " + modifiedName)
        return modifiedName

    print("Cannot resolve imageFilename: " + imageFilename)
    raise NameError("Cannot resolve imageFilename: " + imageFilename)

class ImageHandlerBase:
    def __init__(self):
        self.spriteImages = []
        self.costumeIndex = -1

    def getSpriteImage(self):
        return self.spriteImage

    # costumeIndex starts at 0 for the first costume
    def changeCostume(self, costumeIndex):
        # TODO: What if costumeIndex is invalid?
        self.spriteImage = self.spriteImages[costumeIndex]
        self.costumeIndex = costumeIndex

    # Moves to next costume. If we have no next costume then it goes back to the first one
    def nextCostume(self):
        if self.costumeIndex == -1:
            self.changeCostume(0)
        elif self.costumeIndex + 1 == len(self.spriteImages):
            self.changeCostume(0)
        else:
            self.changeCostume(self.costumeIndex + 1)

# Loads and contains one or more images to use for a SpriteWithImage
# Basically a list of costumes
class ImageHandler(ImageHandlerBase):
    def __init__(self, imageFilenameOrFilenames):
        super().__init__()

        # We are either given one image name or multiple - check which we're given
        if isinstance(imageFilenameOrFilenames, str):
            spriteImageNames = [ imageFilenameOrFilenames ]
        else:
            spriteImageNames = imageFilenameOrFilenames
        
        # Load all the image names and store images
        for spriteImageName in spriteImageNames:
            spriteImageNameResolved = resolveImageFile(spriteImageName)
            image = pygame.image.load(spriteImageNameResolved)
            self.spriteImages.append(image)

        # default to first image
        self.changeCostume(0)

# Sprite sheet ImageHandler
# Uses a large image and picks out the costumes from parts of that large image
class SpriteSheetImageHandler(ImageHandlerBase):
    def __init__(self, spriteSheetImageName):
        super().__init__()
        spriteSheetImageNameResolved = resolveImageFile(spriteSheetImageName)
        self.spriteSheetImage = pygame.image.load(spriteSheetImageNameResolved)

        # sub images
        # TODO: Do this properly - not quite sure how to do it
        x = 70
        y = 28
        for i in range(10):
            self.spriteImages.append(self.spriteSheetImage.subsurface(Rect(x,y,67,67)))
            x += 68
        x = 20
        y = 250
        for i in range(10):
            self.spriteImages.append(self.spriteSheetImage.subsurface(Rect(x,y,67,67)))
            x += 77

        # default to first image
        self.changeCostume(0)

#
# Has a custom transparent Surface that you can paint a sprite image onto in code e.g. an Asteroid in Asteroids
#
class CustomDrawingImageHandler(ImageHandler):
    def __init__(self, width, height):
        # transparency notes: https://riptutorial.com/pygame/example/23788/transparency
        self.spriteImage = pygame.Surface((width, height), pygame.SRCALPHA)
        self.spriteImage.set_alpha(200)  # 0 is fully transparent and 255 fully opaque.

    def getSpriteImage(self):
        return self.spriteImage

#
# Counter
# Animation helper - to show down animation
# Accepts 'tick' events - usually every frame - and calls a particular specified method ("onCountMethod") every "countUpTo" frames
# Basically allows you to slow down some logic by running it every N frames
#
class Counter:
    def __init__(self, countUpTo, onCountMethod):
        self.count = 0
        self.countUpTo = countUpTo
        self.onCountMethod = onCountMethod

    def tick(self):
        self.count += 1
        if self.count >= self.countUpTo:
            self.onCountMethod()
            self.count = 0

#
# Delegate to take over movement for a sprite
#
class MoveHandler:
    def __init__(self):
        pass

    def move(self, sprite):
        pass

#
# Composite List of MoveHandler instances
# TODO: Make use of this somewhere
#
class MoveHandlerList(MoveHandler):
    def __init__(self):
        self.moveHandlerList = []

    def addMoveHandler(self, moveHandler):
        self.moveHandlerList.append(moveHandler)

    def move(self, sprite):
        for moveHandler in self.moveHandlerList:
            moveHandler.move(sprite)

#
# Move handler which simply kills the sprite after a certain number of game ticks
#
class MoveHandlerTimeout(MoveHandler):
    def __init__(self, sprite, timeoutTicks):
        self.sprite = sprite
        self.timeoutTicks = timeoutTicks

    def move(self, sprite):
        self.timeoutTicks -= 1
        if self.timeoutTicks <= 0:
            self.sprite.dead = True

# Says "Get Ready" for a while, then dies and spawns a new Ball
# TODO: Make this generic
class GetReadyMessage(Sprite):
    def __init__(self):
        super().__init__(getScreenRect().width/2, getScreenRect().height/2, 10, 10)
        self.health = 100
        self.colour = red

    def move(self):
        self.y += 0.5
        self.health -= 1
        if self.health == 0:
            self.dead = True
            pygamehelper.game.spawnBall()

    def draw(self):
        drawText("Get Ready", self.x - 60, self.y, pygamehelper.hugeFont, self.colour)


# Will kill the sprite if it goes off screen
# Can be used as a Sprite edgeOfScreenChecker
class KillSprite_EdgeOfScreenChecker():
    def __init__(self):
        pass

    def checkEdgeOfScreen(self, sprite):
        if not sprite.isOnScreen():
            sprite.dead = True

# Will bounce the sprite if it touches the edge of the screen (or if it's completely off screen)
# Can be used as a Sprite edgeOfScreenChecker
# To be bounceable, the Sprite must have a "bounceOnEdgeOfScreen" method
class BounceSprite_EdgeOfScreenChecker():
    def __init__(self):
        self.setModeTouchingEdge()

    def setModeTouchingEdge(self):
        # touching edge
        self.checkForValue = 1

    def setModeCompletelyOffScreen(self):
        # completely off screen
        self.checkForValue = 0

    def checkEdgeOfScreen(self, sprite):
        if sprite.isOnScreenEx() == self.checkForValue:
            # TODO: Determine which edge it is, or provide an easy way for 'bounceOnEdgeOfScreen' to do that
            #  Use calcEdgesHit for this
            #  Maybe it could even be more than one edge, but that is an extreme 'edge case' ;]
            sprite.bounceOnEdgeOfScreen()


def findSprites(point):
    return findSprites2(point[0], point[1])

# Find which sprites are at the point x,y
def findSprites2(x, y):
    result = []
    for sprite in sprites:
        if sprite.getBoundingRect().collidepoint(x, y):
            result.append(sprite)
    return result

def findSpritesByCondition(condition):
    result = []
    for sprite in sprites:
        if condition(sprite):
            result.append(sprite)
    return result


def findCollisions(sprite):
    result = []
    spriteBoundingRect = sprite.getBoundingRect()
    for otherSprite in sprites:
        if otherSprite != sprite:
            if spriteBoundingRect.colliderect(otherSprite.getBoundingRect()):
                result.append(otherSprite)
    return result

def calcBoundingRectCenteredOnXY(x, y, width, height):
    topLeftX = x - width / 2
    topLeftY = y - height / 2
    rect = pygame.Rect(topLeftX, topLeftY, width, height)
    return rect

# allows optional clip area
def drawImageCentered(image, x, y, clipArea):
    halfOfImageWidth = image.get_size()[0] / 2
    halfOfImageHeight = image.get_size()[1] / 2

    topLeft = (x - halfOfImageWidth, y - halfOfImageHeight)
    # draw image
    gameDisplay.blit(image,topLeft, clipArea)

def drawImage(image, x, y, clipArea = None):
    gameDisplay.blit(image,(x, y), clipArea)

def rectFromPoints(p1, p2):
    result = pygame.Rect(p1[0], p1[1], p2[0]-p1[0], p2[1]-p1[1])
    # TODO: Maybe add this in - This will flip the width or height of a rectangle if it has a negative size. The rectangle will remain in the same place, with only the sides swapped.
    #result.normalize()
    return result

# Resolve an angle in degress to a dx, dy value
# The result is like a vector - speed is the length of the vector
# An angle of 0 means pointing "North" which equates to a result vector (0,-1) * speed
# As the angle increases, we rotate clockwise around to the right
def resolveAngle(angleInDegrees, speed):
    angleInRadians = math.radians(angleInDegrees)
    dx = round(math.sin(angleInRadians), 10) * speed
    dy = -1 * round(math.cos(angleInRadians), 10) * speed
    return (dx, dy)

# angle (and speed) -> vector (dx,dy tuple)
def angleToVector(angleInDegrees, speed):
    return resolveAngle(angleInDegrees, speed)

# vector (dx,dy tuple) -> angle in degrees
# 0 is North which is (0,-1)
def vectorToAngle(vector):
    return calcAngle(vector[0], vector[1])

# opposite of resolveAngle - get a dx and dy value and find the angle that this direction represents
# returns an angle in degress
def calcAngle(dx, dy):
    if dx == 0:
        dx = 0.0000001
    if dy == 0:
        dy = 0.0000001
    result = round( math.degrees( round( math.atan(dy/dx), 10) ), 3)

    # part adapted from here: https://stackoverflow.com/questions/6247153/angle-from-2d-unit-vector
    if dx < 0 and dy < 0: # quadrant 3
        result = 180 + result
    elif dx < 0: # quadrant 2
        result = 180 + result # it actually substracts
    elif dy < 0: # quadrant 4
        result = 270 + (90 + result) # it actually substracts

    # current angle is CLOCKWISE from East
    # we wish it to be CLOCKWISE from North
    result += 90
    if result >= 360:
        result -= 360

    return result

def addVectors(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def subtractVectors(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def scaleVector(v, scaleBy):
    return (v[0] * scaleBy, v[1] * scaleBy)

def inverseVector(v):
    return scaleVector(v, -1)

def isVectorZero(v, tolerance):
    if v[0] == 0 and v[1] == 0:
        return True
    if abs(v[0]) <= tolerance and abs(v[1]) <= tolerance:
        return True
    return False

# use Pythagoras's theorem to work out size (length) of vector
def getVectorSize(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def flipYCoord(point):
    return (point[0], -point[1])

# Returns a collection of items:
# 1 top edge
# 2 bottom edge
# 3 right edge
# 4 left edge
def calcEdgesHit(sprite):
    screenRect = getScreenRect()
    spriteRect = sprite.getBoundingRect()
    result = []
    # 1 top edge
    if spriteRect.y <= 0:
        result.append(1)
    # 2 bottom edge
    if spriteRect.bottom >= screenRect.bottom:
        result.append(2)
    # 3 left edge
    if spriteRect.x <= 0:
        result.append(3)
    # 4 right edge
    if spriteRect.right >= screenRect.right:
        result.append(4)
    
    return result

# Called when sprite has touched edge of screen
# Must calculate and set the new angle in sprite
def resolveBounce(sprite):
    # get current vector of movement
    (dx, dy) = resolveAngle(sprite.angle, 1)
    #print("initial dx, dy: " + str(dx) + ", " + str(dy))

    # find edge(s) hit
    edgesHit = calcEdgesHit(sprite)
    #print("edges hit: " + str(edgesHit))

    # calc new vector of movement
    if 1 in edgesHit or 2 in edgesHit:
        dy *= -1
    if 3 in edgesHit or 4 in edgesHit:
        dx *= -1
    
    #print("final dx, dy: " + str(dx) + ", " + str(dy))
    # calc new angle
    newAngle = calcAngle(dx, dy)
    #print("angle: " + str(sprite.angle))
    #print("newAngle: " + str(newAngle))
    sprite.setAngle(newAngle)

# Called when sprite has touched edge of screen
# Must calculate and set the new angle in sprite
# Note: sprite must have a 'velocity' property
def resolveBounceWithVelocity(sprite):
    # get current vector of movement
    (dx, dy) = sprite.velocity

    # find edge(s) hit
    edgesHit = calcEdgesHit(sprite)

    # calc new vector of movement
    if 1 in edgesHit or 2 in edgesHit:
        dy *= -1
    if 3 in edgesHit or 4 in edgesHit:
        dx *= -1
    
    sprite.velocity = (dx, dy)

# Call this when the sprite has gone completely off screen on an edge, and you want to move it just offscreen on the opposite edge
# The assumption is that the sprite will keep moving in the same direction and therefore come back onscreen
def wrapSpriteOffEdge(sprite):
    edgesHit = calcEdgesHit(sprite)
    if 1 in edgesHit:
        # top edge
        sprite.moveBy(0, getScreenRect().height + sprite.getBoundingRect().height)
    if 2 in edgesHit:
        # bottom edge
        sprite.moveBy(0, -getScreenRect().height - sprite.getBoundingRect().height)
    if 3 in edgesHit:
        # left edge
        sprite.moveBy(getScreenRect().width + sprite.getBoundingRect().width, 0)
    if 4 in edgesHit:
        # right edge
        sprite.moveBy(-getScreenRect().width - sprite.getBoundingRect().width, 0)

# chooses a random direction
# returns a (dx,dy) vector
def randomDirectionAsVector(size = 1):
    randomAngle = random.randint(0, 360)
    return angleToVector(randomAngle, size)

def randomDirection():
    return random.randint(0, 360)

def randomX():
    return random.randint(1, getScreenRect().width)

def randomY():
    return random.randint(1, getScreenRect().height)


#-----------------------------------------------------------------------------
# Path stuff
#-----------------------------------------------------------------------------

#
# Path - a list of points
#
class Path(Sprite):
    def __init__(self):
        self.waypoints = []

    def addWaypoint(self, x, y):
        point = (x, y)
        self.waypoints.append(point)

    def getWaypoints(self):
        return self.waypoints

    def getWaypointCount(self):
        return len(self.waypoints)

#
# PathDrawer
# 
class PathDrawer(Sprite):
    def __init__(self, path):
        super().__init__(100, 100, 100, 100)
        self.path = path

    def move(self):
        pass

    def draw(self):
        previous = None
        for waypoint in self.path.getWaypoints():
            if previous != None:
                drawLine(previous, waypoint, red, 2)
            previous = waypoint

#
# PathFollowSprite
#
# Doesnt really do much now - you don't really need one of these - just tag your sprite
# with a PathFollowMoveHandler as it's moveHandler
# 
class PathFollowSprite(Sprite):
    def __init__(self, path):
        super().__init__(200, 0, 10, 10)
        pathFollowModeAlternateDefault = True
        self.moveHandler = PathFollowMoveHandler(self, path, pathFollowModeAlternateDefault)

    def setPathFollowModeAlternate(self, val):
        self.moveHandler.setPathFollowModeAlternate(val)

#
# PathFollowMoveHandler
# 
# The main logic to follow a path
# You can install one of these using: PathFollowMoveHandler.installForSprite
#
# If you have multiple sprites following the same path, you'll need an instance per sprite, because various
# sprite-instance-specific values are stored in an instance of PathFollowMoveHandler
# 
class PathFollowMoveHandler(MoveHandler):
    def __init__(self, sprite, path, pathFollowModeAlternate = False):
        super().__init__()
        self.sprite = sprite
        self.path = path
        # pathFollowModeAlternate
        # True - "advanced" mode which means we calc the number of steps to get from the current point to the destination point
        # False - "simple" mode which means we always take 100 steps between points, no matter how far it is
        self.pathFollowModeAlternate = pathFollowModeAlternate

        # speed with which we move - approx equal to number of pixels to move per step
        self.speed = 1

        # Hook to run when we reach end of path
        self.endOfPathHook = None

        # Which point we're heading towards
        self.headingTowardsPointIdx = 0
        self.calcDestinationAndVelocity()
        # Remember the last location so that we can detect if the sprite has been moved by something else, and recalc our velocity
        self.lastLocation = sprite.getLocation()

    @staticmethod
    def installForSprite(sprite, path):
        pathFollowMoveHandler = PathFollowMoveHandler(sprite, path, True)
        sprite.setMoveHandler(pathFollowMoveHandler)
        return pathFollowMoveHandler

    def setPathFollowModeAlternate(self, val):
        self.pathFollowModeAlternate = val
        # Force a recalc on next 'move' call
        self.velocityVector = None

    def setEndOfPathHook(self, endOfPathHook):
        self.endOfPathHook = endOfPathHook

    def setSpeed(self, speed):
        self.speed = speed
        # Force a recalc on next 'move' call
        self.velocityVector = None

    # Calc how to get from our current x,y to the next point
    def calcDestinationAndVelocity(self):
        # Grab point which we're currently going to head towards
        self.destinationPoint = self.path.getWaypoints()[self.headingTowardsPointIdx]

        # velocityVector is the amount to move on each step along the path to the destination point
        print("checking location vs destination")
        print("  location: " + str(self.sprite.getLocation()))
        print("  destination: " + str(self.destinationPoint))
        self.velocityVector = subtractVectors(self.destinationPoint, self.sprite.getLocation())
        if self.pathFollowModeAlternate:
            print("alternate/advanced mode, with speed: " + str(self.speed))
            numSteps = getVectorSize(self.velocityVector) / self.speed
        else:
            print("simple mode - fixed 100 steps")
            numSteps = 100
        print("numSteps: " + str(numSteps))
        if numSteps > 0:
            self.velocityVector = scaleVector(self.velocityVector, 1 / numSteps)
        else:
            self.velocityVector = (0, 0)
        print("velocityVector: " + str(self.velocityVector))

    # We always assume the sprite passed is our sprite
    def move(self, sprite):
        if self.lastLocation != sprite.getLocation() or self.velocityVector == None:
            print("Something was changed since we last moved - we'll have to recalc the velocity")
            self.calcDestinationAndVelocity()

        # Take a step along the path
        self.sprite.moveBy(self.velocityVector[0], self.velocityVector[1])
        #print("new location: " + str(self.sprite.getLocation()))
        self.lastLocation = sprite.getLocation()

        # Check if we're reached the point
        # TODO: This is slightly confusing, to subtract the points as vectors - we should have an 'isVectorEquals' routine, with a tolerance allowed
        check = subtractVectors(self.destinationPoint, self.sprite.getLocation())
        print("move, location: " + str(self.sprite.getLocation()) + ", destination: " + str(self.destinationPoint) + ", check: " + str(check))

        if isVectorZero(check, 0.01):
            # We reached a point
            print("We reached point: " + str(self.headingTowardsPointIdx))
            # Ensure we're directly on the point now
            self.sprite.setLocation(self.destinationPoint)

            # Now head to the next path point
            self.headingTowardsPointIdx += 1
            if self.headingTowardsPointIdx >= self.path.getWaypointCount():
                # There is no next path point - what should we do? By default we wrap round and go back to the first point
                self.headingTowardsPointIdx = 0
                # Call hook if any - this could stop the movement
                if self.endOfPathHook:
                    print("calling endOfPathHook")
                    self.endOfPathHook()
                    # TODO: Maybe if endOfPathHook returns a False we could just return or something?

            # Calc velocity to the new destination
            self.calcDestinationAndVelocity()
            print("-> Now heading to point: " + str(self.headingTowardsPointIdx) + " at " + str(self.destinationPoint))
        elif self.isNextToDestination(check):
            # We are right next to destination
            # On the next move we should hit the destination
            print("Next to destination - we should reach it on next move - assuring this")
            self.velocityVector = check

    # If we're less than our velocity away
    # TODO: Check this with negative numbers
    def isNextToDestination(self, check):
        return abs(check[0]) <= abs(self.velocityVector[0]) and abs(check[1]) <= abs(self.velocityVector[1])

#-----------------------------------------------------------------------------
# Path stuff ends
#-----------------------------------------------------------------------------



gameDisplay = None
clock = None
defaultFont = None
smallFont = None
largeFont = None
mediumFont = None
mediumSmallFont = None
hugeFont = None
sprites = []
debug = True
gameTick = 0
# This will be the GameLoop subclass instance - you can use "pygamehelper.game" to use this from anywhere e.g. inside a Sprite's code
game = None
# Change this to help debugging e.g. pygamehelper.fps = 10
fps = 60

def drawText(text, x, y, font, colour):
    t = font.render(text, True, colour)
    gameDisplay.blit(t, (x, y))

def initPygame():
    print(">>> initPygame")
    
    global gameDisplay
    global clock
    global defaultFont
    global smallFont
    global largeFont
    global mediumFont
    global mediumSmallFont
    global hugeFont
    pygame.init()
    gameDisplay = pygame.display.set_mode((display_width,display_height))
    print("gameDisplay is now: " + str(gameDisplay))
    clock = pygame.time.Clock()
    defaultFont = pygame.font.SysFont(None, 12)
    smallFont = pygame.font.SysFont(None, 13)
    mediumSmallFont = pygame.font.SysFont(None, 14)
    mediumFont = pygame.font.SysFont(None, 18)
    largeFont = pygame.font.SysFont(None, 36)
    hugeFont = pygame.font.SysFont(None, 72)
    
    print("<<< initPygame")

def displayClear(backgroundColour):
    gameDisplay.fill(backgroundColour)

def displayUpdate():
    global gameTick
    gameTick += 1
    pygame.display.update()

def addSprite(sprite):
    sprites.append(sprite)

def addSpriteBefore(sprite, beforeSprite):
    index = sprites.index(beforeSprite)
    sprites.insert(index, sprite)

# deprecated name - please use moveAndDrawAllSprites
def drawAndMoveAllSprites():
    moveAndDrawAllSprites()

def drawRect(rect, colour, width=0):
    pygame.draw.rect(gameDisplay, colour, rect, width)

def drawPoint(point, colour):
    drawRect(Rect(point[0],point[1],3,3), colour)

def drawLine(fromPoint, toPoint, colour, width = 1):
    pygame.draw.line(gameDisplay, colour, fromPoint, toPoint, width)

def drawLineThick(fromPoint, toPoint, colour):
    for x in range(-2,3):
        for y in range(-2,3):
            p1 = (fromPoint[0] + x, fromPoint[1] + y)
            p2 = (toPoint[0] + x, toPoint[1] + y)
            pygame.draw.line(gameDisplay, colour, p1, p2, 1)

def drawLineaa(fromPoint, toPoint, colour):
    for x in range(-2,3):
        for y in range(-2,3):
            p1 = (fromPoint[0] + x, fromPoint[1] + y)
            p2 = (toPoint[0] + x, toPoint[1] + y)
            pygame.draw.aaline(gameDisplay, colour, p1, p2)

#
# Draws and moves all sprites
# Also asks all sprites whether any sprite is dead, and removes dead sprites from the game
#
def moveAndDrawAllSprites():
    global sprites

    # move
    for sprite in sprites:
        sprite.move()
        # This sets boundingRect so all sprites must have this done before we can check collisions in the next loop
        sprite.moveDone()

    # 'after move' stuff
    allDeads = []
    for sprite in sprites:
        if sprite.isCollisionDetectionEnabled():
            sprite.checkCollisions()
        sprite.checkEdgeOfScreen()

        deadsForMe = sprite.checkDead()
        if deadsForMe != None:
            allDeads.extend(deadsForMe)

    for allDeadItem in allDeads:
        if allDeadItem in sprites:
            sprites.remove(allDeadItem)
            allDeadItem.onDeath()

    # draw
    for sprite in sprites:
        sprite.draw()
        if debug:
            sprite.drawDebug()

    if debug:
        drawText("gameTick: " + str(gameTick), 10, display_height-30, defaultFont, white)
        drawText("sprites count: " + str(len(sprites)), 10, display_height-20, defaultFont, white)

#
# Class to hold the main game loop logic
# You should subclass this in your game, and provide an "eachFrame" method which will be called on every frame.
# That can spawn new sprites or do other 'global' tasks.
#
class GameLoop():

    def __init__(self):
        global game
        game = self

    # Override this to provide your own code which will run on every frame
    def eachFrame(self):
        pass

    # Override this to handle key presses etc
    def onEvent(self, event):
        pass

    # Call this to start the infinite move-draw loop - that's your game loop
    def runGameLoop(self):
        gameExit=False
        while not gameExit:
            # Handle any key events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                self.onEvent(event)

            # clear screen area
            displayClear(blue)

            # Perform any global game logic here
            self.eachFrame()

            # display all sprites in the screen area
            moveAndDrawAllSprites()

            # show the screen area on the display
            displayUpdate()
            # make the game run at 60 fps
            clock.tick(fps)

print("DigiLocal pygamehelper.py has been included")

