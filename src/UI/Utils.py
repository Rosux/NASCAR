from enum import Enum
import pygame
import re

"""
    All the position coordinates are in 0 to 1 floats
"""

class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    
class Anchor(Enum):
    BOTTOMLEFT = 0
    BOTTOMRIGHT = 1
    BOTTOMCENTER = 2
    TOPLEFT = 3
    TOPRIGHT = 4
    TOPCENTER = 5
    CENTER = 6
    CENTERLEFT = 7
    CENTERRIGHT = 8

class Surface():
    def __init__(self, screenWidth, screenHeight):
        pygame.init()
        self.surface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        self.fontPath = None
        self.font = pygame.font.Font(self.fontPath, 24)

    """
        Draws a rectangle to self.surface with given parameters
        if the text parameter is set it automatically fits the text inside the rectangle
        x = 0 to 1 coordinate of where to place the origin of the rectangle
        y = 0 to 1 coordinate of where to place the origin of the rectangle
        width = width of rectangle in 0 to 1 range (0 being nothing and 1 being the whole screen width)
        height = height of rectangle in 0 to 1 range (0 being nothing and 1 being the whole screen height)
        color = (0, 0, 0, 0) singleton of color in rgba
        anchor = define the anchor point of the rect
        text = optional text to render inside the rect if emptry string ignore
        textColor = (0, 0, 0, 0) singleton of colors in rgba
    """
    def Rect(self, x, y, width, height, color, anchor=Anchor.TOPLEFT, text="", textColor=(0, 0, 0, 255), textAlign=Align.CENTER):
        # Calculate the position based on the anchor point
        if anchor == Anchor.CENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2
        elif anchor == Anchor.TOPLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height()
        elif anchor == Anchor.TOPRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height()
        elif anchor == Anchor.BOTTOMLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.BOTTOMRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.TOPCENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height()
        elif anchor == Anchor.BOTTOMCENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.CENTERLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2
        elif anchor == Anchor.CENTERRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2
            
        rect = pygame.Rect(x, y, width * self.surface.get_width(), height * self.surface.get_height())
        pygame.draw.rect(self.surface, color, rect)
        
        if text != "":
            max_font_size = int(height * self.surface.get_height())
            font = pygame.font.Font(self.fontPath, max_font_size)

            text_height = 0
            text_lines = text.split('\n')
            
            for line in text_lines:
                text_height += font.size(line)[1]

            if text_height > height * self.surface.get_height():
                # If the text is too tall, reduce the font size to fit
                scaling_factor = (height * self.surface.get_height()) / text_height
                max_font_size = int(max_font_size * scaling_factor)
                font = pygame.font.Font(self.fontPath, max_font_size)
                
            tmp = None
            for line in text_lines:
                if tmp is None:
                    tmp = font.size(line)[0]
                elif font.size(line)[0] > tmp:
                    tmp = font.size(line)[0]

            if tmp > width * self.surface.get_width():
                scaling_factor = (width * self.surface.get_width()) / tmp
                max_font_size = int(max_font_size * scaling_factor)
                font = pygame.font.Font(self.fontPath, max_font_size)
                text_surface = font.render(line, False, textColor)
                text_rect = text_surface.get_rect()

            # Render each line individually and vertically stack them within the rectangle
            y_offset = 0
            for line in text_lines:
                text_surface = font.render(line, False, textColor)
                text_rect = text_surface.get_rect()
                
                # Calculate the position to center the text horizontally within the rectangle
                text_x = 0
                if textAlign == Align.CENTER:
                    text_x = x + (width * self.surface.get_width() - text_rect.width) / 2
                elif textAlign == Align.LEFT:
                    text_x = 0
                elif textAlign == Align.RIGHT:
                    text_x = width * self.surface.get_width() - text_rect.width
                
                if len(text_lines) > 1:
                    text_y = y + y_offset
                else:
                    text_y = y + (height * self.surface.get_height() - text_rect.height) / 2
                self.surface.blit(text_surface, (text_x, text_y))
                y_offset += text_rect.height  # Move down for the next line of text
            
        return rect
    
    def Text(self, x, y, width, height, anchor=Anchor.TOPLEFT, text="", fontSize=1.0, textColor=(0, 0, 0, 255)):
        if anchor == Anchor.CENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2
        elif anchor == Anchor.TOPLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height()
        elif anchor == Anchor.TOPRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height()
        elif anchor == Anchor.BOTTOMLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.BOTTOMRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.TOPCENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height()
        elif anchor == Anchor.BOTTOMCENTER:
            x = x * self.surface.get_width() - (width * self.surface.get_width()) / 2
            y = y * self.surface.get_height() - (height * self.surface.get_height())
        elif anchor == Anchor.CENTERLEFT:
            x = x * self.surface.get_width()
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2
        elif anchor == Anchor.CENTERRIGHT:
            x = x * self.surface.get_width() - (width * self.surface.get_width())
            y = y * self.surface.get_height() - (height * self.surface.get_height()) / 2

        rect = pygame.Rect(x, y, width * self.surface.get_width(), height * self.surface.get_height())
        xx = x
        
        fontSize = int(self.surface.get_height() * fontSize)
        words = re.split(r" |(\n)", text)
        words = [item for item in words if item and item != " "]

        font = pygame.font.Font(self.fontPath, fontSize)
        spaceSize = (0, 0)
        for word in words:
            spaceSize = font.size(" ")
            wordSize = font.size(word)
            if word == "\n":
                y += spaceSize[1]
                x = xx
                continue
            textSurface = font.render(word, False, textColor)
            textRect = textSurface.get_rect()
            
            if x + wordSize[0] > rect.width:
                x = xx
                y += spaceSize[1]
                
            if y+spaceSize[1] > rect.bottom:
                break
            
            self.surface.blit(textSurface, (x, y))
            x += spaceSize[0] + wordSize[0]

        return [rect, spaceSize]

    def Clear(self):
        self.surface.fill((0, 0, 0, 255))