import pygame
from vector2d import Vector2D
from Utils import clamp
from Entity import Entity
from enum import Enum


class Game:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((720, 480), pygame.RESIZABLE)
        pygame.display.set_caption("NASCAR")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.entities = []

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
            # if user presses the quit button stop game
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # run update method on all entities
            if not self.paused:
                for entity in self.entities:
                    if entity.active:
                        entity.Update(dt, events)
            if not self.paused:
                self.DrawScene(dt)
            else:
                self.DrawScene(0)

            # clear screen then draw new stuff to screen
            self.screen.fill((0, 0, 0, 255))

    def DrawScene(self, deltaTime):
        pass
