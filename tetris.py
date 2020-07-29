#!/usr/bin/env python3
# Tetris
# -*- coding: utf-8 -*-

# Programmed by CoolCat467

# For AI Support, the python file has to have the text
# 'AI' in it somewhere, and has to have the '.py' extention.
# Discription here about how AI functions are called and
# the protocal it follows

# Please send your finnished version of your AI to CoolCat467 at Github
# for review and testing and obain permission to change the REGISTERED
# flag to True, but it doesn't really do much anyways.

# IMPORTANT NOTE:
# The updating and turn calls halt execution, including display
# updates. This would be fixed with multiprocessing, but I am not
# very familiar with it and it also might cause some dy-syncronization
# problems.

import os, random, math

# If pygame is not installed, install it
try:
    from pygame.locals import *
    import pygame
except ImportError:
    print('Error: Pygame is not installed!', file=os.sys.stderr)
    while True:
        inp = input('Would you like to install pygame automatically? (y/n) : ').lower()
        if inp in ('y', 'n'):
            break
        else:
            print('Please enter a valid answer.')
    if inp == 'y':
        print('Attempting to automatically install pygame...')
        out = os.system('pip3 install pygame --user')
        if out == 0:
            print('Pygame installed sucessfully!')
            print('Please Restart the program')
        else:
            print('Something went wrong installing pygame.', file=os.sys.stderr)
            inp = 'n'
    if inp == 'n':
        print('To manually install pygame, open your computer\'s command prompt/terminal/shell')
        print('and type in the command "pip3 install pygame --user".')
    input('Press Enter to Continue. ')
    os.abort()

try:
    from Vector2 import *
except ImportError:
    print('Error: Vector2 Module Not Found', file=os.sys.stderr)
    print('''
    Please download the Vector2 Module found with the release of this
    project and ensure it is in the same folder as this program,
    and it\'s filename matches "Vector2.py"''')
    input('Press Enter to Continue. ')
    os.abort()

__title__ = 'Tetris'
__author__ = 'CoolCat467'
__version__ = '0.0.0'
__ver_major__ = 0
__ver_minor__ = 0
__ver_patch__ = 0

SCREENSIZE = (500, 500)

FPS = 60
BLOCKSIZE = 23
FALLPERSEC = 1
# Speed blocks move when left or right arrow key down
FRAMESPERVERTICALMOVE = 100
# Speed blocks move when down key pressed
FRAMESPERHORIZONTALMOVE = 80
# Speed blocks rotate when up key pressed
FRAMESPERROTATION = 500

def replaceWithColor(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    surface = surface.copy().convert_alpha()
    w, h = surface.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))
    return surface

def setAlpha(surface, alpha):
    """Set the alpha value for all pixels in a surface, preserve color."""
    surface = surface.copy().convert_alpha()
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b = surface.get_at((x, y))[:3]
            surface.set_at((x, y), pygame.Color(r, g, b, alpha))
    return surface

def outlineSurf(surface, color, percent=90):
    """Add an outline of a given color to a surface"""
    w, h = surface.get_size()
    # Replace all color on the image with the color
    surf = replaceWithColor(surface, color)
    # Make the surface be 90% of it's size
    perc = percent / 100
    inside_surf = pygame.transform.scale(surface, [round(w*perc), round(h*perc)])
    # Add the modified image to the correct location
    iner = (1 - perc) / 2
    surf.blit(inside_surf, [int(w*iner), int(h*iner)])
    # Return modified image
    return surf

class Block(object):
    """This object represents a block on the screen."""
    def __init__(self, xy, color):
        self.startLoc = Vector2(*xy)
        self.location = Vector2(*xy)
        self.color = color
        self.dead = False
        self.image = self.genBlockSurf(self.color, BLOCKSIZE)
    
    def __repr__(self):
        return 'Block(%s)' % ", ".join([str(i) for i in [self.startLoc, self.color]])
    
    @staticmethod
    def genBlockSurf(color, size):
        """Generate the image used for a tile"""
        # Make a blank surface of the size we're given
        surf = pygame.Surface([size]*2)
        # Fill the blank surface with the color given
        surf.fill(color)
        # Return a square image of the color given
        surf = outlineSurf(surf, [0]*3)
        return surf
    
    def render(self, surface, centered=False, zerozero=(0, 0)):
        """Render self to surface."""
        if self.dead:
            return
        x, y = self.location * BLOCKSIZE + Vector2(*zerozero)
        if centered:
            w, h = self.image.get_size()
            surface.blit(self.image, (int(x-w/2), int(y-h/2)))
            return
        surface.blit(self.image, (int(x), int(y)))
    pass

class ShapeId(object):
    """Object for storeing information about shape ids."""
    def __init__(self, blockPositions, rotationPoint, color):
        self.blockPositions = [Vector2(*bpos) for bpos in blockPositions]
        self.rotationPoint = Vector2(*rotationPoint)
        self.color = color
    
    def __repr__(self):
        return 'ShapeId(%s)' % ", ".join([str(i) for i in [self.blockPositions, self.rotationPoint, self.color]])
    pass

class ShapeGenerator(object):
    """Object for generating shapes."""
    def __init__(self, grid):
        self.grid = grid
        self.genShapeIds()
        self.shapes = {'square':self.square, 'l':self.lshape, 'revl':self.revlsp,
                       'i':self.linesp, 't':self.tshape, 'z':self.zshape, 's':self.sshape}
        self.snames = tuple(self.shapes.keys())
##        self.shapeIds = [self.square, self.lshape, self.revlsp, self.linesp, self.tshape, self.zshape, self.sshape]
        self.countSZInRow = 0
    
    def __repr__(self):
        return 'ShapeGenerator(%s)' % repr(self.grid)
    
    @staticmethod
    def rect(w, h, xo=0, yo=0):
        """Returns generated rectangular block positions, given a width, height, x offet, and y offset."""
        return [[x+xo, y+yo] for y in range(h) for x in range(w)]
        
    def genShapeIds(self):
        """Generates shape ids."""
        # Generate and store each shape id in it's own variable
        self.square = ShapeId(self.rect(2, 2),
                              [0.5, 0.5],
                              [255, 239, 43])
        self.lshape = ShapeId(self.rect(1, 3)+[[1, 2]],
                              [0, 1],
                              [247, 167, 0])
        self.revlsp = ShapeId(self.rect(1, 3, 1)+[[0, 2]],
                              [1, 1],
                              [0, 100, 200])
        self.linesp = ShapeId(self.rect(1, 4),
                              [0.5, 1.5],
                              [0, 201, 223])
        self.tshape = ShapeId(self.rect(3, 1, yo=1)+[[1, 0]],
                              [1, 1],
                              [155, 0, 190])
        self.zshape = ShapeId([[0, 0], [1, 0], [1, 1], [2, 1]],
                              [1, 1],
                              [220, 0, 0])
        self.sshape = ShapeId([[0, 1], [1, 1], [1, 0], [2, 0]],
                              [1, 1],
                              [0, 230, 50])
    
    def getRandomShapeId(self):
        """Returns a random shape id."""
        # Choose a random shape name
        shape = random.choice(self.snames)
        # Ensure no more than four z or s shapes can happen in a row
        # Keep track of how many s' or z's have happened in a row
        if shape in ('z', 's'):
            self.countSZInRow += 1
        else:
            self.countSZInRow = 0
        # If there have been four or more in a row,
        if self.countSZInRow >= 4:
            # Set the count to zero
            self.countSZInRow = 0
            # Return a random shape that is NOT an s or a z shape
            return self.shapes[random.choice(self.snames[:-2])]
        # Otherwise, just return the shape
        return self.shapes[shape]
    
    def getRandomShape(self, position):
        """Returns a Shape Object by using a random shape id and position."""
        # Create a new shape object on self.grid from a random shape id and a given position
        return Shape(self.grid, self.getRandomShapeId(), position)
    pass

class Shape(object):
    """This is shape object."""
    def __init__(self, grid, shapeId, xy):
        self.grid = grid
        self.shapeId = shapeId
        self.location = Vector2(*xy)
        self.startLoc = Vector2(*xy)
        self.blocks = [Block(pos + self.startLoc, shapeId.color) for pos in self.shapeId.blockPositions]
        self.dead = False
    
    def render(self, surface, centered=False, atLoc=None):
        """Renders all of self.blocks to surface."""
        # If we don't have any special arguments about where to be rendered at,
        if atLoc is None:
            # For each block in this shape, render that block to the surface
            for block in self.blocks:
                block.render(surface, centered)
        else:
            # Otherwise, get the sum of the x and y positions in each of our blocks...
            sumX = sum([block.location.x + 0.5 for block in self.blocks])
            sumY = sum([block.location.y + 0.5 for block in self.blocks])
            # And get the midpoint for all the blocks...
            midPoint = Vector2(sumX / len(self.blocks), sumY / len(self.blocks))
            # And use that midpoint to get what our zero zero positon should be,
            # plus the location we want the blocks rendered relative to
            position = -midPoint * BLOCKSIZE + atLoc
            # Finaly, render all the blocks.
            for block in self.blocks:
                block.render(surface, centered, position)
    
    def canMove(self, x, y):
        """Returns True if this shape is allowed to move to x, y on self.grid."""
        xy = Vector2(x, y)
        # For each block in this shape,
        for block in self.blocks:
            # If the block's new position if this move were to happen is already
            # occupied, we cannot move.
            if not self.grid.isPositionVacant(block.location + xy):
                return False
        # Otherwise, we should be good.
        return True
    
    def canMoveDown(self):
        """Returns True if this shape can move down."""
        # Return wether we can move one grid space downward
        return self.canMove(0, 1)
    
    def moveShape(self, x, y):
        """Moves self to x, y if we are allowed to."""
        # If we are allowed to move to this position,
        if self.canMove(x, y):
            # Change our position to the new position
            self.location += Vector2(x, y)
            # For each of our blocks, update their position
            for block in self.blocks:
                block.location += Vector2(x, y)
    
    def killShape(self):
        """Sets self.dead to True and sets dead = True for all self.blocks."""
        self.dead = True
        # For each block that makes up this shape,
        for block in self.blocks:
            # Add the block to the grid's dead blocks list
            self.grid.deadBlocks.append(block)
            # Add the block to the dead blocks matrix at it's location
            x, y = block.location
            self.grid.deadBlocksMatrix[y][x] = block
    
    def moveDown(self):
        """Moves self down by one block if allowed, if not allowed kill this shape."""
        # If we are allowed to move a block down,
        if self.canMove(0, 1):
            # Move there.
            self.moveShape(0, 1)
        else:
            # Otherwise kill this shape.
            self.killShape()
    
    def getBlockPosAfterRotate(self, block, isClockwise):
        """Return block position after a rotation."""
        # Get the block's position it's at now, in shapeId format, not grid location
        startingPos = block.location - self.location
        # Get the point the block should be rotated around from our shape id
        rotationPoint = self.shapeId.rotationPoint
        # Get the block's relative position from the location point
        startingPosRelativeToRotationPoint = startingPos - rotationPoint
        # Get the proper rotation, clockwise or anti-clockwise, mesured in radians.
        # math.pi / 2 is the same as +90 degrees, negative of that is -90 degrees.
        rotation = {True:math.pi / 2, False:-math.pi / 2}[isClockwise]
        # Get the rotated point relative to the rotation point by roateing the relative
        # point in the given direction
        rotatedRelativePoint = startingPosRelativeToRotationPoint.rotate(rotation)
        # Get the new position by adding the relative point to the rotation point,
        # makeing it not relative to it anymore and therefore an absolute point
        newPosition = rotatedRelativePoint + rotationPoint
        # Return the block's new position plus our location for a grid position.
        # Rounded because floating point math is wierd, and plus we want intigers.
        return round(newPosition + self.location)
    
    def canRotate(self, isClockwise):
        """Returns True if all of the blocks in this shape can rotate without colliding with other blocks."""
        # For each block in this shape,
        for block in self.blocks:
            # Get the block's position after it would rotate
            newPos = self.getBlockPosAfterRotate(block, isClockwise)
            # If that new position on the grid is not vacant, we cannot rotate.
            if not self.grid.isPositionVacant(newPos):
                return False
        # If everyone (blocks) can move to an un-occupied space, we can rotate!
        return True
    
    def rotate(self, isClockwise):
        """Rotates this shape if we are allowed to."""
        # If we are allowed to rotate,
        if self.canRotate(isClockwise):
            # For each block that makes up this shape,
            for block in self.blocks:
                # Set the block's location to it's location after being rotated
                block.location = self.getBlockPosAfterRotate(block, isClockwise)
    
    def resetPosition(self):
        """Resets position to the position we were initialized to."""
        # Set our location to our start position
        self.location = self.startLoc.copy()
        # For each block that makes up this shape,
        for block in self.blocks:
            # Set the block's location to it's start position
            block.location = block.startLoc
    pass

class Grid(object):
    def __init__(self, width, height, location):
        self.width = width
        self.height = height
        self.location = Vector2(*location)
        self.deadBlocks = []
        self.resetBlocksMatrix()
        self.shapeGenerator = ShapeGenerator(self)
        self.currentShape = self.getNewShape()
        self.nextShape = self.getNewShape()
        self.heldShape = None
        self.hasHeldThisShape = False
        self.gridImage = self.drawGrid()
        self.shapeBox = self.drawShapeBox()
    
    def resetBlocksMatrix(self):
        """Resets self.deadBlocksMatrix to blank."""
        # Create a dictionary with lots of stuff.
        # Note: It's a dictionary because wierd stuff happens with lists. Trust me.
        self.deadBlocksMatrix = {y:[None]*self.width for y in range(self.height)}
    
    def isPositionVacant(self, xy):
        """Returns True if the xy location on the grid is vacant."""
        # If the xy position is a valid block matrix position,
        x, y = xy
        if y >= 0 and y < self.height and x >= 0 and x < self.width:
            # Return wether that matrix position is empty or not
            return self.deadBlocksMatrix[y][x] is None
        return False
    
    def checkForClearedLines(self):
        """Checks for cleared lines in self.deadBlocksMatrix."""
        # For each row in the grid,
        for y in range(self.height):
            # For all we know, we should clear the row.
            clearRow = True
            # For each block on this row,
            for x in range(self.width):
                # If the block at position is vacant, don't clear the row.
                if self.deadBlocksMatrix[y][x] is None:
                    clearRow = False
                    break
            # If every position in this row is filled, clear the row
            if clearRow:
                # Deactivate row
                for i in range(self.width):
                    self.deadBlocksMatrix[y][i].dead = True
                
                # For each row above the cleared row, move them down.
                for collumn in range(y - 1, -1, -1):
                    for x in range(self.width):
                        # If there is a block at the position we're moveing,
                        if not self.deadBlocksMatrix[collumn][x] is None:
                            # Increment that block's y position by one
                            self.deadBlocksMatrix[collumn][x].location.y += 1
                        # Make a copy of the target block down one row
                        self.deadBlocksMatrix[collumn + 1][x] = self.deadBlocksMatrix[collumn][x]
                        # Delete the target block
                        self.deadBlocksMatrix[collumn][x] = None
    
    def getNewShape(self):
        """Returns a new shape object from self.shapeGenerator."""
        # Return a new shape generated from our shape generator,
        # with initialized x position being the middle of the grid.
        return self.shapeGenerator.getRandomShape([round(self.width / 2), 0])
    
    def moveShapeDown(self):
        """Moves self.currentShape down."""
        # Move the current shape down
        self.currentShape.moveDown()
        
        # If the current shape died while moving,
        if self.currentShape.dead:
            # We have not held the shape, it is dropped on the floor.
            self.hasHeldThisShape = False
            # See if the shape's falling elemenated any lines
            self.checkForClearedLines()
            # The current shape is now the next shape,
            # and the next shape is now a new shape
            self.currentShape, self.nextShape = self.nextShape, self.getNewShape()
            # If the new block is stuck, then reset everything because the game is over.
            if not self.currentShape.canMoveDown():
                # Reset the dead blocks matrix
                self.resetBlocksMatrix()
                # There are no dead blocks
                self.deadBlocks = []
                # The current shape is a new shape
                self.currentShape = self.getNewShape()
                # The next shape is a new shape
                self.nextShape = self.getNewShape()
                # We are no longer holding anything
                self.heldShape = None
    
    def moveShapeLeft(self):
        """Move self.currentShape to the left."""
        # Move the current shape to the left
        self.currentShape.moveShape(-1, 0)
    
    def moveShapeRight(self):
        """Move self.currentShape to the right."""
        # Move the current shape to the right
        self.currentShape.moveShape(1, 0)
    
    def rotateShape(self):
        """Rotates self.currentShape clockwise."""
        # Rotate the current shape clockwise
        self.currentShape.rotate(True)
    
    def drawGrid(self):
        """Returns a surface of a grid."""
        # Get the dimentions of self
        w, h = Vector2(self.width, self.height) * BLOCKSIZE
        # Create a new surface of our dimentions, being completely transparent.
        surface = setAlpha(pygame.Surface((w, h)).convert_alpha(), 0)
        # Draw a rectange on our blank surface
        color = [200]*3
        pygame.draw.rect(surface, color, pygame.Rect(0, 0, w, h), 1)
        # Draw the lines for the grid on our surface
        for i in range(self.width):
            pygame.draw.line(surface, color, [i * BLOCKSIZE, 0], [i * BLOCKSIZE, self.height * BLOCKSIZE], 1)
        for i in range(self.height):
            pygame.draw.line(surface, color, [0, i * BLOCKSIZE], [self.width * BLOCKSIZE, i * BLOCKSIZE], 1)
        # Return the surface
        return surface
    
    def render(self, surface):
        """Renders all shapes to the surface."""
        # Get our position and dimentions
        x, y = self.location
        w, h = Vector2(self.width, self.height) * BLOCKSIZE
        # Create a surface of our dimentions
        surf = pygame.Surface((w, h))
        # Fill the surface with white
        surf.fill([255]*3)
        # Stick the grid image on top of it
        surf.blit(self.gridImage, (0, 0))
        # For all of the dead blocks, render them to our surface
        for block in self.deadBlocks:
            block.render(surf)
        # Render the current shape to our surface
        self.currentShape.render(surf)
        # Stick our image to the given surface at the right spot
        # for self.location to be in the middle of our surface
        surface.blit(surf, (int(x-w/2), int(y-h/2)))
        # Render the nextShape box and the heldShape box to the surface
        self.renderNextShape(surface)
        self.renderHeldShape(surface)
    
    def holdShape(self):
        """Hold current shape in held box if not occupied."""
        # If we have already held this shape, we cannot continue.
        if self.hasHeldThisShape:
            return
        # Otherwise, if we are holding a shape already,
        if not self.heldShape is None:
            # We held a shape, stop the future self from swaping stuff again.
            self.hasHeldThisShape = True
            # Reset the position of the piece that's falling at the moment
            self.currentShape.resetPosition()
            # Swap held shape and current shape
            self.heldShape, self.currentShape = self.currentShape, self.heldShape
        else:# If we are not already holding a shape,
            # Set held shape to current shape and current shape to next shape,
            # and generate a new next shape
            self.heldShape, self.currentShape = self.currentShape, self.nextShape
            # Reset the position of the held shape for the future
            self.heldShape.resetPosition()
            # Set the next shape to a random new shape
            self.nextShape = self.getNewShape()
    
    def drawShapeBox(self):
        """Returns a surface of the shape box."""
        # Get the maximum size of a shape
        shapeWidthPixels = 4 * BLOCKSIZE
        # Generate a new blank surface of the dimentions of the max shape size
        surface = setAlpha(pygame.Surface([shapeWidthPixels]*2).convert_alpha(), 0)
        # Draw a black rectange on the surface
        pygame.draw.rect(surface, [0]*3, pygame.Rect(2, 2, shapeWidthPixels-4, shapeWidthPixels-4), 4)
        # Return our new shape box
        return surface
    
    def drawShapeInBox(self, shape):
        """Returns a surface of a given shape in a box."""
        # Get a copy of our shape box
        surface = self.shapeBox.copy()
        # If the shape argument is not blank,
        if not shape is None:
            # Render that shape to our shape box surface in the middle of it
            shape.render(surface, False, round(Vector2(*[4 * BLOCKSIZE]*2) / 2))
        # Return the surface with the shape box and given shape rendered in it
        return surface
    
    def renderNextShape(self, surface):
        """Renders the next shape inside of a box to the right side of the grid."""
        wh = Vector2(self.width, self.height) * BLOCKSIZE
        swh = Vector2(*SCREENSIZE)
        posTopLeft = (swh - wh) / 2
        
        surf = self.drawShapeInBox(self.nextShape)
        surface.blit(surf, round(posTopLeft + Vector2(wh[0] + BLOCKSIZE, BLOCKSIZE)))
    
    def renderHeldShape(self, surface):
        """Renders the held shape inside of a box to the left side of the grid."""
        # Get the width and height of ourselves and the screen
        wh = Vector2(self.width, self.height) * BLOCKSIZE
        swh = Vector2(*SCREENSIZE)
        # Get the position of the top left corner of our grid image
        posTopLeft = (swh - wh) / 2
        # Get a surface of our shape in a box
        surf = self.drawShapeInBox(self.heldShape)
        # Copy the shape in a box to the right position.
        # Position is to the right of the grid by one block and down by a block
        surface.blit(surf, round(posTopLeft + Vector2(-BLOCKSIZE * 5, BLOCKSIZE)))
    pass

class Keyboard(object):
    """Keyboard object, handles keyboard input."""
    def __init__(self, grid):
        self.grid = grid
        self.keys = {K_LEFT:'left', K_RIGHT:'right', K_UP:'up', K_DOWN:'down'}
        self.triggers = tuple(self.keys.keys())
        self.knames = tuple(self.keys.values())
        self.delay = {'left':FRAMESPERVERTICALMOVE, 'right':FRAMESPERVERTICALMOVE,
                      'down':FRAMESPERHORIZONTALMOVE, 'up':FRAMESPERROTATION}
        self.time = {name:0 for name in self.keys.values()}
        self.active = {name:False for name in self.keys.values()}
        self.actions = {'left' :self.grid.moveShapeLeft,
                        'right':self.grid.moveShapeRight,
                        'down' :self.grid.moveShapeDown,
                        'up'   :self.grid.rotateShape,
                        'space':self.grid.holdShape}
    
    def readEvent(self, event):
        """Handles an event."""
        if event.type == KEYDOWN:
            if event.key in self.triggers:
                name = self.keys[event.key]
                self.active[name] = True
            elif event.key == K_SPACE:
                self.actions['space']()
        elif event.type == KEYUP:
            if event.key in self.triggers:
                name = self.keys[event.key]
                self.active[name] = False
                self.time[name] = 0
    
    def readEvents(self, events):
        """Handles a list of events."""
        for event in events:
            self.readEvent(event)
    
    def process(self, time_passed):
        """Sends commands to self.grid based on pressed keys and time."""
        for name in self.knames:
            self.time[name] = max(self.time[name] - time_passed, 0)
            if self.active[name]:
                if self.time[name] == 0:
                    self.actions[name]()
                    self.time[name] = self.delay[name]
    pass

def run():
    """Main loop of everything"""
    print(__title__+' '+__version__)
    # Initialize Pygame
    pygame.init()
    
    # Set up the screen
    screen = pygame.display.set_mode(SCREENSIZE, 0, 16)
    pygame.display.set_caption(__title__+' '+__version__)
    
    global grid, keyboard
    grid = Grid(10, 20, (SCREENSIZE[0]/2, SCREENSIZE[1]/2))
    keyboard = Keyboard(grid)
    
    # Set up the FPS clock
    clock = pygame.time.Clock()
    
    MUSIC_END = USEREVENT + 1#This event is sent when a music track ends
    
    # Set music end event to our new event
    pygame.mixer.music.set_endevent(MUSIC_END)
    
    # Load and start playing the music
    pygame.mixer.music.load('sound/tetris.mid')
    pygame.mixer.music.play()
    
    fallTime = FALLPERSEC
    
    RUNNING = True
    
    # While the game is active
    while RUNNING:
        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                RUNNING = False
            elif event.type == MUSIC_END:
                pygame.mixer.music.stop()
                pygame.mixer.music.play()
            else:
                keyboard.readEvent(event)
        
        time_passed = clock.tick(FPS)
        keyboard.process(time_passed)
        
        if keyboard.active['down']:
            fallTime = FALLPERSEC
        if fallTime <= 0:
            grid.moveShapeDown()
            fallTime = FALLPERSEC
        fallTime = max(fallTime - (time_passed / 1000), 0)
        
        screen.unlock()
        
        screen.fill([255]*3)
        pygame.draw.rect(screen, [200]*3, pygame.Rect(2, 2, SCREENSIZE[0]-5, SCREENSIZE[1]-5), 4)
        
        grid.render(screen)
        
        screen.lock()
        
        # Update the display
        pygame.display.update()
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == '__main__':
    # If we're not imported as a module, run.
    run()
