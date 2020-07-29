#!/usr/bin/env python3
# Vector2 Class for games
# -*- coding: utf-8 -*-

# Original version by Will McGugan, modified extensively by CoolCat467
# Programmed by CoolCat467

__title__ = 'Vector2 Module'
__author__ = 'CoolCat467'
__version__ = '1.0.4'
__ver_major__ = 1
__ver_minor__ = 0
__ver_patch__ = 4

import math

class Vector2(object):
    def __init__(self, x=0, y=0):
        if str(type(x)) in ("<class 'tuple'>", "<class 'list'>"):
            x, y = x
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    
    def __repr__(self):
        x, y = self.x, self.y
        return "Vector2(%s, %s)" % (x, y)
    
    @staticmethod
    def from_points(frompoint, topoint):
        """Return a vector with the direction of frompoint to topoint"""
        P1, P2 = list(frompoint), list(topoint)
        return Vector2(P2[0] - P1[0], P2[1] - P1[1])
    
    def get_magnitude(self):
        """Return the magnitude (length) of the vector"""
        return math.sqrt(self.x**2 + self.y**2)
    
    def get_distance_to(self, point):
        """Get the magnitude to a point"""
        return Vector2.from_points(point, self).get_magnitude()
    
    def normalize(self):
        """Normalize self (make into a unit vector)"""
        magnitude = self.get_magnitude()
        if not magnitude == 0:
            self.x /= magnitude
            self.y /= magnitude
    
    def copy(self):
        """Make a copy of self"""
        return Vector2(self.x, self.y)
    
    def __copy__(self):
        return self.copy()
    
    def get_normalized(self):
        """Return a normalized vector (heading)"""
        vec = self.copy()
        vec.normalize()
        return vec
    
    def getHeading(self):
        """Returns the arc tangent (mesured in radians) of self.y/self.x."""
        return math.atan2(self.y, self.x)
    
    def getHeadingDeg(self):
        """Returns the arc tangent (mesured in degrees) of self.y/self.x."""
        return math.degrees(self.getHeading())
    
    def rotate(self, radians):
        """Returns a new vector by rotating self around (0, 0) by radians."""
        newHeading = self.getHeading() + radians
        magnitude = self.get_magnitude()
        x = math.cos(newHeading) * magnitude
        y = math.sin(newHeading) * magnitude
        # Round up to 13 digits, or we'll get wierd rounding errors, like
        # .00000000000001
        return Vector2(round(x, 13), round(y, 13))
    
    def rotateDeg(self, degrees):
        """Returns a new vector by rotating self around (0, 0) by degrees."""
        return self.rotate(math.radians(degrees))
    
    def _addv(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)
    
    #rhs is Right Hand Side
    def __add__(self, rhs):
        if isinstance(rhs, self.__class__):
            return self._addv(rhs)
        if len(rhs) == 2:
            x, y = rhs
            return Vector2(self.x + x, self.y + y)
        raise LookupError('Length of right hand sign opperator length is not equal to two!')
    
    def _subv(self, vec):
        return Vector2(self.x - vec.x, self.y - vec.y)
    
    def __sub__(self, rhs):
        if isinstance(rhs, self.__class__):
            return self._subv(rhs)
        if len(rhs) == 2:
            x, y = rhs
            return Vector2(self.x - x, self.y - y)
        raise LookupError('Length of right hand sign opperator length is not equal to two!')
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        try:
            x, y = self.x / scalar, self.y / scalar
        except ZeroDivisionError:
            x, y = self.x, self.y
        return Vector2(x, y)
    
    def __len__(self):
        return 2
    
    def __iter__(self):
##        self.iterc = 0
##        return self
        return iter([self.x, self.y])
    
##    def __next__(self):
##        if self.iterc <= 1:
##            val = [self.x, self.y][self.iterc]
##            self.iterc += 1
##            return val
##        else:
##            raise StopIteration
    
    def __getitem__(self, x):
        return [self.x, self.y][x]
    
    def __round__(self):
        return Vector2(round(self.x), round(self.y))
    
    def __abs__(self):
        return Vector2(abs(self.x), abs(self.y))
    pass
