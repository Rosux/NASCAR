import pygame
from vector2d import Vector2D
from Utils import clamp
from Entity import Entity
from enum import Enum
from Car import Car
from Wall import Wall
from RaceManager import Race
import math


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
