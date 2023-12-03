import pygame
from vector2d import Vector2D
from Utils import clamp, Magnitude
from Entity import Entity
from enum import Enum
from Car import Car
from CarPlayerTwo import CarPlayerTwo
from CarAi import CarAI
from Wall import Wall
from RaceManager import Race
from Collision import RectangleCollision
import UI.Utils as Utils
import math
import random
import pygame.mixer


class Scene(Enum):
    MAINMENU = 0
    RACE = 1
    STATS = 3

class Game:
    def __init__(self):
        pygame.display.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("DragStrip")
        self.clock = pygame.time.Clock()
        self.running = True
        # car1 = Car("Player", Vector2D(-70, -60), 0)
        # car2 = CarPlayerTwo("Player2", Vector2D(70, -60), 0)
        # carAI = CarPlayerTwo("Player", Vector2D(70, -60), 0)
        self.finish = Wall(Vector2D(0, -10300), 600, 600, 0)
        self.entities = []
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.speed_limit = 320
        # sprites
        self.car1 = pygame.image.load("./assets/sprites/pitstop_car_10.png")
        self.car2 = pygame.image.load("./assets/sprites/pitstop_car_1.png")
        self.background = pygame.image.load("./assets/sprites/Dragstripfinish.png")
        self.currentScene = Scene.MAINMENU
        self.currentSelection = 0
        self.currentTime = -5.0
        self.winTitle = ""
        self.winCar = 0
        self.musicRun = False
        self.musicRun2 = False

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
                if entity.active and self.currentScene == Scene.RACE and self.currentTime >= 0.0:
                    entity.Update(dt, events)
            filteredEntites = [e for e in self.entities if e.active and e.collision and hasattr(e, "collider")]
            
            if self.currentScene == Scene.RACE:
                self.currentTime += dt
                if self.currentTime >= 0.0:
                    for i in range(len(filteredEntites)):
                        for j in range(i+1, len(filteredEntites)):
                            entity1 = filteredEntites[i]
                            entity2 = filteredEntites[j]
                            colliderHit = entity1.collider.CheckCollision(entity2.collider)
                            if (isinstance(entity1, Car) or isinstance(entity1, CarPlayerTwo) or isinstance(entity1, CarAI)) and (isinstance(entity2, Car) or isinstance(entity2, CarPlayerTwo) or isinstance(entity2, CarAI)):
                                entity2.collider.VerticesInsideOtherShape(entity1)
                                entity1.collider.VerticesInsideOtherShape(entity2)
                            if (isinstance(entity1, Car) or isinstance(entity1, CarPlayerTwo) or isinstance(entity1, CarAI)) and colliderHit:
                                entity1.rb.velocity = Vector2D(0, 0)
                                entity1.rb.rotational_velocity = 0
                                entity2.collider.VerticesInsideOtherShape(entity1)
                            if (isinstance(entity2, Car) or isinstance(entity2, CarPlayerTwo) or isinstance(entity2, CarAI)) and colliderHit:
                                entity2.rb.rotational_velocity = 0
                                entity2.rb.velocity = Vector2D(0, 0)
                                entity1.collider.VerticesInsideOtherShape(entity2)
                            if isinstance(entity1, Car) and entity1.collider.CheckCollision(self.finish.collider):
                                print("player 1 wins!")
                                self.winTitle = f"Player 1 won!\nTime: {self.currentTime:.2f}"
                                self.winCar = self.car1
                                self.currentScene = Scene.STATS
                            if isinstance(entity1, CarPlayerTwo) and entity1.collider.CheckCollision(self.finish.collider):
                                print("player 2 wins!")
                                self.winCar = self.car2
                                self.winTitle = f"Player 2 won!\nTime: {self.currentTime:.2f}"
                                self.currentScene = Scene.STATS
                            if isinstance(entity1, CarAI) and entity1.collider.CheckCollision(self.finish.collider):
                                print("AI wins!")
                                self.winCar = self.car2
                                self.winTitle = f"AI won!\nTime: {self.currentTime:.2f}"
                                self.currentScene = Scene.STATS
            # clear screen then draw new stuff to screen
            self.screen.fill((0, 0, 0, 255))
            if self.currentScene == Scene.RACE:
                if not self.musicRun:
                    pygame.mixer.music.stop()  # Stop any currently playing music
                    pygame.mixer.music.load('./assets/Gas.wav')
                    pygame.mixer.music.set_volume(0.05)
                    pygame.mixer.music.play(-1)
                    self.musicRun = True
                self.DrawScene()
                self.DrawUI()
                self.DrawLapTime(self.currentTime)
            elif self.currentScene == Scene.STATS:
                if not self.musicRun2:
                    pygame.mixer.music.stop()  # Stop any currently playing music
                    pygame.mixer.music.load('./assets/finishHIM.mp3')
                    pygame.mixer.music.set_volume(0.05)
                    pygame.mixer.music.play(-1)
                    self.musicRun2 = True
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.currentScene = Scene.MAINMENU
                            self.musicRun = False
                            self.musicRun2 = False
                self.DrawStats()
            elif self.currentScene == Scene.MAINMENU:
                pygame.mixer.music.stop() 
                self.DrawMainMenu(events)
            pygame.display.flip()
            
    def DrawLapTime(self, time):
        screenWidth, screenHeight = pygame.display.get_surface().get_size()
        screenSize = Vector2D(screenWidth, screenHeight)
        overlay = Utils.Surface(screenWidth, screenHeight)
        overlay.Rect(0.0, 0.0, 1.0, 0.1, (0, 0, 0, 0), Utils.Anchor.TOPLEFT, f"{time:.2f}", (255, 255, 255), Utils.Align.LEFT)
        self.screen.blit(overlay.surface, (0, 0))
        
    def DrawMainMenu(self, events):
        screenWidth, screenHeight = pygame.display.get_surface().get_size()
        screenSize = Vector2D(screenWidth, screenHeight)
        overlay = Utils.Surface(screenWidth, screenHeight)
        overlay.Rect(0.0, 0.0, 1.0, 1.0, (255, 255, 255, 255))
        
        if self.currentSelection == 0:
            overlay.Rect(0.5, 0.35, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Single Player", (255, 255, 0))
        else:
            overlay.Rect(0.5, 0.35, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Single Player", (255, 255, 255, 255))
        if self.currentSelection == 1:
            overlay.Rect(0.5, 0.5, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Two Player", (255, 255, 0))
        else:
            overlay.Rect(0.5, 0.5, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Two Player", (255, 255, 255, 255))
        if self.currentSelection == 2:
            overlay.Rect(0.5, 0.65, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Quit", (255, 255, 0))
        else:
            overlay.Rect(0.5, 0.65, 0.3, 0.1, (0, 0, 0, 255), Utils.Anchor.CENTER, "Quit", (255, 255, 255, 255))
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.currentSelection = (self.currentSelection - 1) % 3
                if event.key == pygame.K_DOWN:
                    self.currentSelection = (self.currentSelection + 1) % 3
                if event.key == pygame.K_RETURN:
                    if self.currentSelection == 0: # singleplayer
                        self.entities = [
                            Car("Player", Vector2D(70, -60), 0),
                            CarAI("AI", Vector2D(-70, -60), 0),
                            Wall(Vector2D(0, 300), 600, 600, 0),
                            Wall(Vector2D(250, -5000), 200, 10000, 0),
                            Wall(Vector2D(-250, -5000), 200, 10000, 0),
                        ]
                        self.currentScene = Scene.RACE
                        self.currentTime = -5.0
                    if self.currentSelection == 1: # 2 players
                        self.entities = [
                            Car("Player", Vector2D(70, -60), 0),
                            CarPlayerTwo("Player2", Vector2D(-70, -60), 0),
                            Wall(Vector2D(0, 300), 600, 600, 0),
                            Wall(Vector2D(250, -5000), 200, 10000, 0),
                            Wall(Vector2D(-250, -5000), 200, 10000, 0),
                        ]
                        self.currentScene = Scene.RACE
                        self.currentTime = -5.0
                    if self.currentSelection == 2: # quit
                        self.running = False
        
        self.screen.blit(overlay.surface, (0, 0))

    def DrawScene(self):
        width, height = pygame.display.get_surface().get_size()
        player = Vector2D(0, 0)
        for car in self.entities:
            if isinstance(car, Car) and car.name == "Player":
                player = car.position
                break
        multuplePlayers = [c for c in self.entities if isinstance(c, Car) or isinstance(c, CarPlayerTwo)]
        if len(multuplePlayers) >= 2:
            player1 = multuplePlayers[0].position
            player2 = multuplePlayers[1].position
            player = Vector2D((player1.x + player2.x) / 2, (player1.y + player2.y) / 2)
        offset = player
        # remove
        f = [c for c in self.entities if isinstance(c, CarAI)]
        offset = f[0].position
        # remove ^
        img = self.background
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        rect = img.get_rect(midbottom=(0-offset.x+(width//2), 0-offset.y+(height//2)))
        self.screen.blit(img, rect.topleft)
        for entity in self.entities:
            if isinstance(entity, Car) or isinstance(entity, CarPlayerTwo) or isinstance(entity, CarAI):
                img = self.car1 if isinstance(entity, Car) else self.car2
                img = pygame.transform.scale(img, (entity.rb.width, entity.rb.height))
                img = pygame.transform.rotate(img,- math.degrees(entity.rotation)+180)
                rect = img.get_rect(center=(entity.position.x-offset.x+(width//2), entity.position.y-offset.y+(height//2)))
                self.screen.blit(img, rect.topleft)
            # if isinstance(entity, Wall):
            #     points = entity.collider.GetPoints(entity.collider)
            #     pygame.draw.polygon(self.screen, (255, 0, 0), [(p.x-offset.x+(width//2), p.y-offset.y+(height//2)) for p in points], 1)

    def DrawStats(self):
        screenWidth, screenHeight = pygame.display.get_surface().get_size()
        screenSize = Vector2D(screenWidth, screenHeight)
        overlay = Utils.Surface(screenWidth, screenHeight)
        overlay.Rect(0.0, 0.0, 1.0, 1.0, (0, 0, 0, 255), Utils.Anchor.TOPLEFT, self.winTitle+"\nPress enter to return to menu.", (255, 255, 255), Utils.Align.CENTER)
        self.screen.blit(overlay.surface, (0, 0))
        img = self.winCar
        img = pygame.transform.scale(img, (img.get_width()/2, img.get_height()/2))
        img = pygame.transform.rotate(img, 90)
        rect = img.get_rect(center=(screenWidth//2, screenHeight//2+(screenHeight//6)))
        self.screen.blit(img, rect.topleft)
    
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
            
                # Draw speedometer needle
                angle = 180 - (car.GetSpeef()/ car.speed_limit) * 180
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
                gear_text = self.font.render(f"Speed: {int(car.GetSpeef())}", True, (0, 0, 0))
                self.screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2 + (width // 7), height - (height // 5)))
                
                # Display rpm value
                rpm_text = self.font.render(f"Rpm: {int(car.GetRpm())}", True, (0, 0, 0))
                self.screen.blit(rpm_text, (width // 2 - rpm_text.get_width() // 2 - (width // 7), height - (height // 5)))
                
                # Display current gear
                gear_text = self.font.render(f"Gear: {car.gear}", True, (255, 255, 255))
                self.screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2, height - (height // 5)))