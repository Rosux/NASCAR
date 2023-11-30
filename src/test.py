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
        self.currentGear = clamp(self.currentGear+1, -1, self.maxGear)
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
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Speedometer")
    
    entities = [engine]
    font = pygame.font.Font(None, 36)
    
    
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(0) / 1000.0
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for entity in entities:
            if entity.active:
                entity.Update(dt, events)
        # Update the display
        screen.fill((0, 0, 0))
        # Draw speedometer background
        pygame.draw.circle(screen, (255, 255, 255), (width // 1.5, height // 2), 150)
        pygame.draw.circle(screen, (0, 0, 0), (width // 1.5, height // 2), 140)

        # Draw rpmmeter background
        pygame.draw.circle(screen, (255, 255, 255), (width // 3, height // 2), 150)
        pygame.draw.circle(screen, (0, 0, 0), (width // 3, height // 2), 140)

        # Draw speedometer needle
        angle = 180 - (engine.speed / engine.speed_limit) * 180  # Convert speed to angle (180 to 0 degrees)
        angle_rad = math.radians(angle)
        needle_length = 120
        end_point = (width // 1.5 + needle_length * math.cos(angle_rad), height // 2 - needle_length * math.sin(angle_rad))
        pygame.draw.line(screen, (255, 0, 0), (width // 1.5, height // 2), (int(end_point[0]), int(end_point[1])), 5)

        # Display speed value
        speed_text = font.render(f"Speed: {int(engine.speed)}", True, (255, 255, 255))
        screen.blit(speed_text, (625, 150))

        # Draw rpm needle
        angle = 180 - (engine.GetRpm() / engine.rpm_limit) * 180  # Convert RPM to angle (180 to 0 degrees)
        angle_rad = math.radians(angle)
        end_point = (width // 3 + needle_length * math.cos(angle_rad), height // 2 - needle_length * math.sin(angle_rad))
        pygame.draw.line(screen, (255, 0, 0), (width // 3, height // 2), (int(end_point[0]), int(end_point[1])), 5)

        # Display rpm value
        rpm_text = font.render(f"Rpm: {int(engine.GetRpm())}", True, (255, 255, 255))
        screen.blit(rpm_text, (300, 150))

        # Display current gear
        gear_text = font.render(f"Gear: {engine.currentGear}", True, (255, 255, 255))
        screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2, height - 100))
        

        pygame.display.flip()

