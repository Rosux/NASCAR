from vector2d import Vector2D
from Entity import Entity
from Utils import clamp
from random import random
from Car import Car
import math
import pygame


class Checkpoint:
    def __init__(self, position, radius=10):
        self.position = position
        self.radius = radius
        self.is_passed = False

    def CheckCarPassing(self, car_position):
        if not self.is_passed:
            distance_to_checkpoint = math.dist(car_position, self.position)
            if distance_to_checkpoint < self.radius:
                self.is_passed = True
                return True
        return False

class Race(Entity):
    def __init__(self, cars: list[Car] = [], startPositions: list[Vector2D] = []):
        super().__init__()
        self.collision = False
        self.cars = cars
        self.startPositions = startPositions
        self.raceLength = 60.0 # (1 minute)
        self.currentTime = -5.0
        self.running = False
        self.runOnce = False
        for i, car in enumerate(self.cars):
            car.position = self.startPositions[i]
            car.Pause()

    def Update(self, deltaTime, events):
        self.currentTime += deltaTime
        if self.currentTime >= 0.0 and not self.runOnce:
            self.runOnce = True
            print("DRAG RACE STARTED")
            self.StartRace()
        if self.currentTime >= self.raceLength and self.running:
            print("STOP RACE")
            self.StopRace()

    def StartRace(self):
        self.running = True
        for car in self.cars:
            car.Start()

    def StopRace(self):
        self.running = False
        for car in self.cars:
            car.Pause()
    
        



if __name__ == "__main__":
    pygame.init()  # Initialize Pygame
    font = pygame.font.Font(None, 36)
    screen = pygame.display.set_mode((720, 480), pygame.RESIZABLE)
    pygame.display.set_caption("NASCAR")
    clock = pygame.time.Clock()
    running = True
    paused = False
    screenWidth, screenHeight = pygame.display.get_surface().get_size()


    # verander dit
    RACE = Race()


    entities = [RACE]
    while running:
        dt = clock.tick(60) / 1000.0  # Cap the frame rate at 60 frames per second
        pygame.event.pump()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if not paused:
            entities[0].Update(dt, events)

        screen.fill((0, 0, 0, 255))

        if entities[0].currentTime <= 0:
            countdown_text = font.render(f"Countdown: {entities[0].currentTime:.2f}", True, (255, 255, 255))
        else:
            # Countdown is over, display live race time
            racetime = font.render(f"Racetime: {entities[0].currentTime:.2f}", True, (255, 255, 255))

        # Render the appropriate text
        text_to_render = countdown_text if entities[0].currentTime <= 0 else racetime
        screen.blit(text_to_render, (300, 150))


        pygame.display.flip()

    pygame.quit()