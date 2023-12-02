import pygame
import sys
import math
import random
from Utils import clamp, RotateVector, clampVector, Magnitude
from Entity import Entity


class Engine(Entity):
    def __init__(self, maxGear: int=4):
        super().__init__()
        # Set up speedometer parameters
        self.speed = 0
        self.speed_limit = 320
        self.rpm = 0
        self.rpm_limit = 9000
        self.minRpm = 2000
        self.maxRpm = 6500

        self.maxGear = maxGear
        self.currentGear = 0
        
        self.xxx = 0
        self.oldRandomFactor = random.uniform(0, 450)

    def ShiftUp(self):
       if self.currentGear == 0 or self.currentGear == -1 or self.speed >= 0.8 * self.speed_limit:  # Allow upshifting only if speed is at least 80% of the speed limit
            self.currentGear = clamp(self.currentGear + 1, -1, self.maxGear)
            self.rpm -= self.minRpm


    def ShifDown(self):
        self.currentGear = clamp(self.currentGear-1, -1, self.maxGear)
        self.rpm += self.minRpm

    def Update(self, deltaTime, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    self.ShiftUp()
                if event.key == pygame.K_LCTRL:
                    self.ShifDown()
                    
        keys = pygame.key.get_pressed()

        acceleration_factor = 2  # Adjust this factor based on your preference
        deceleration_factor = 1.5  # Adjust this factor based on your preference

        if keys[pygame.K_UP]:
            if self.currentGear == 0:
                acceleration_factor = 0
            elif self.currentGear == 1:
                self.speed_limit = 80
            elif self.currentGear ==2:
                self.speed_limit = 160
            elif self.currentGear == 3:
                self.speed_limit = 240
            elif self.currentGear == 4:
                self.speed_limit = 320
            elif self.currentGear == -1:
                self.speed_limit = 30
            self.speed = min(self.speed + acceleration_factor * 60 * deltaTime, self.speed_limit)
            
            
            # Fix gear based on self.speed and adjust rpm
            self.rpm += 100 * 60 * deltaTime
            self.rpm = min(self.rpm, self.rpm_limit)
            # if self.rpm >= self.maxRpm and self.current_gear != self.maxGear:
            #     self.current_gear = max(1, min(self.current_gear + 1, self.maxGear))
            #     self.rpm -= self.minRpm
        else:
            self.speed = max(self.speed - deceleration_factor * 60 * deltaTime, 0)
            self.rpm = max(self.rpm - 100 * 60 * deltaTime, self.minRpm)
            # if self.rpm <= self.minRpm and self.current_gear != 1:
            #     self.current_gear = min(self.maxGear, max(self.current_gear - 1, 1))
            #     self.rpm += self.minRpm

        if keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 1.5 * 60 * deltaTime, 0)

    def GetRpm(self):
        self.xxx += 1
        if self.xxx >= 90:
            self.xxx = 0
            self.oldRandomFactor = random.uniform(0, 250)
        return min(self.rpm + self.oldRandomFactor, self.rpm_limit)



if __name__ == "__main__":
    
    engine = Engine()
        
    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 1200, 1000
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Speedometer")
    
    entities = [engine]
    font = pygame.font.Font(None, 36)
    
    
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000.0  # Set the frame rate to 60 FPS
        pygame.event.pump()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        for entity in entities:
            if entity.active:
                entity.Update(dt, events)

        # Update the display
        screen.fill((255, 255, 255))

        # Draw speedometer background
        center_x, center_y = width // 2, height - (height // 40)
        pygame.draw.circle(screen, (128, 128, 128), (center_x -  min(width // 4, height // 4), center_y), min(width // 4, height // 4), 2)
        pygame.draw.circle(screen, (255, 255, 255), (center_x -  min(width // 4, height // 4), center_y), min(width // 4, height // 4) - 10)

        # Draw rpm meter background
        center_x, center_y = width // 2, height - (height // 40)
        pygame.draw.circle(screen, (128, 128, 128), (center_x + min(width // 4, height // 4), center_y), min(width // 4, height // 4),2 )
        pygame.draw.circle(screen, (255, 255, 255), (center_x + min(width // 4, height // 4), center_y), min(width // 4, height // 4) - 10)

        # Draw speedometer needle
        angle = 180 - (engine.speed / engine.speed_limit) * 180
        angle_rad = math.radians(angle)
        needle_length = min(width // 4, height // 4) - 20
        end_point = ((center_x + min(width // 4, height // 4)) + needle_length * math.cos(angle_rad), center_y - needle_length * math.sin(angle_rad))
        pygame.draw.line(screen, (255, 0, 0), (center_x + min(width // 4, height // 4), center_y), (int(end_point[0]), int(end_point[1])), 5)

        # Draw rpm needle
        angle = 180 - (engine.GetRpm() / engine.rpm_limit) * 180
        angle_rad = math.radians(angle)
        end_point = ((center_x - min(width // 4, height // 4)) + needle_length * math.cos(angle_rad), center_y - needle_length * math.sin(angle_rad))
        pygame.draw.line(screen, (255, 0, 0), (center_x - min(width // 4, height // 4), center_y), (int(end_point[0]), int(end_point[1])), 5)

        # Display current gear
        gear_text = font.render(f"Gear: {engine.currentGear}", True, (0, 0, 0))
        screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2, height - (height // 5)))

        pygame.display.flip()