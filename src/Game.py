import pygame
from vector2d import Vector2D
from Utils import clamp, Magnitude
from Entity import Entity
from enum import Enum
from Car import Car
from Wall import Wall
from RaceManager import Race
import math
import random

class Game:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("NASCAR")
        self.clock = pygame.time.Clock()
        self.running = True
        car1 = Car("Player", Vector2D(100, 100), 0)
        self.entities = [
            car1,
            Wall(Vector2D(0, 0), 50, 50, 45),
        ]
        self.speed_limit = 320
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def AddEntity(self, entity):
        self.entities.append(entity)

    def RemoveEntity(self, entity):
        self.entities.remove(entity)

    def GetEntity(self, entityType):
        for entity in self.entities:
            if isinstance(entity, entityType):
                return entity
        return None

    def GetAllEntitiesType(self, entityType):
        tmp = []
        for entity in self.entities:
            if isinstance(entity, entityType):
                tmp.append(entity)
        if len(tmp) > 0:
            return tmp
        else:
            return None


    def Run(self):
        while self.running:
            # calculate deltatime
            # dont limit fps. we have deltaTime to calculate stuff
            dt = self.clock.tick(0) / 1000.0
            # print(self.clock.get_fps())
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # run update method on all entities
            for entity in self.entities:
                if entity.active:
                    entity.Update(dt, events)
            filteredEntites = [e for e in self.entities if e.active and e.collision and hasattr(e, "collider")]
            for i in range(len(filteredEntites)):
                for j in range(i+1, len(filteredEntites)):
                    entity1 = filteredEntites[i]
                    entity2 = filteredEntites[j]
                    colliderHit = entity1.collider.CheckCollision(entity2.collider)
                    if isinstance(entity1, Car) and colliderHit:
                        entity2.collider.VerticesInsideOtherShape(entity1)
                    if isinstance(entity2, Car) and colliderHit:
                        entity1.collider.VerticesInsideOtherShape(entity2)
            # clear screen then draw new stuff to screen
            self.screen.fill((0, 0, 0, 255))

            self.DrawScene()
            self.DrawRaceStats()
            self.DrawUI()

            pygame.display.flip()

    def DrawScene(self):
        width, height = pygame.display.get_surface().get_size()
        player = Vector2D(0, 0)
        for car in self.entities:
            if isinstance(car, Car) and car.name == "Player":
                player = car.position
                break
        offset = player
        for entity in self.entities:
            if isinstance(entity, Car):
                img = pygame.image.load("./assets/sprites/pitstop_car_10.png")
                img = pygame.transform.scale(img, (entity.rb.width, entity.rb.height))
                img = pygame.transform.rotate(img,- math.degrees(entity.rotation)+180)
                rect = img.get_rect(center=(entity.position.x-offset.x+(width//2), entity.position.y-offset.y+(height//2)))
                self.screen.blit(img, rect.topleft)
            if isinstance(entity, Wall):
                points = entity.collider.GetPoints(entity.collider)
                pygame.draw.polygon(self.screen, (255, 0, 0), [(p.x-offset.x+(width//2), p.y-offset.y+(height//2)) for p in points], 1)

    def DrawRaceStats(self):
        # teken racemanager ui hier zoals tijd over, punten, positie, etc
        pass
    
    def DrawUI(self):
        for car in self.entities:
            if isinstance(car, Car):
                width, height = pygame.display.get_surface().get_size()
                
                # Draw speedometer background
                center_x, center_y = width // 2, height - (height // 40)
                pygame.draw.circle(self.screen, (128, 128, 128), (center_x -  min(width // 4, height // 4), center_y), min(width // 4, height // 4), 2)
                pygame.draw.circle(self.screen, (255, 255, 255), (center_x -  min(width // 4, height // 4), center_y), min(width // 4, height // 4) - 10)

                # Draw rpm meter background
                center_x, center_y = width // 2, height - (height // 40)
                pygame.draw.circle(self.screen, (128, 128, 128), (center_x + min(width // 4, height // 4), center_y), min(width // 4, height // 4),2 )
                pygame.draw.circle(self.screen, (255, 255, 255), (center_x + min(width // 4, height // 4), center_y), min(width // 4, height // 4) - 10)
                
                #draw speef
                cc = car.rb.GetPointVelocity(car.rb.position)
                speef = (Magnitude(cc) / 1500) * 300
                print(speef)

                # # Draw speedometer needle
                angle = 180 - (speef / self.speed_limit) * 180
                angle_rad = math.radians(angle)
                needle_length = min(width // 4, height // 4) - 20
                end_point = ((center_x + min(width // 4, height // 4)) + needle_length * math.cos(angle_rad), center_y - needle_length * math.sin(angle_rad))
                pygame.draw.line(self.screen, (255, 0, 0), (center_x + min(width // 4, height // 4), center_y), (int(end_point[0]), int(end_point[1])), 5)
               
                # Draw rpm needle
                angle = 180 - (car.GetRpm() / car.rpm_limit) * 180
                angle_rad = math.radians(angle)
                end_point = ((center_x - min(width // 4, height // 4)) + needle_length * math.cos(angle_rad), center_y - needle_length * math.sin(angle_rad))
                pygame.draw.line(self.screen, (255, 0, 0), (center_x - min(width // 4, height // 4), center_y), (int(end_point[0]), int(end_point[1])), 5)
                
                # Display speed
                gear_text = self.font.render(f"Speed: {int(speef)}", True, (0, 0, 0))
                self.screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2 + (width // 7), height - (height // 6)))
                
                # Display rpm value
                rpm_text = self.font.render(f"Rpm: {int(car.GetRpm())}", True, (0, 0, 0))
                self.screen.blit(rpm_text, (width // 2 - rpm_text.get_width() // 2 - (width // 7), height - (height // 5)))
                
                # Display current gear
                gear_text = self.font.render(f"Gear: {car.gear}", True, (255, 255, 255))
                self.screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2, height - (height // 5)))