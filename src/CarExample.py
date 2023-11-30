from vector2d import Vector2D
from Entity import Entity
from Utils import clamp, RotateVector, clampVector, Magnitude, Dot
from random import random
from Collision import RectangleCollision
from RigidBody2D import RigidBody2D
from Wall import Wall
import math
import pygame
from enum import Enum

class DriveType(Enum):
    ALL = 0
    FRONT = 1
    REAR = 2

class Car(Entity):
    
    @property
    def position(self):
        return self.rb.position
    
    @property
    def rotation(self):
        return self.rb.orientation
    
    @property
    def velocity(self):
        return self.rb.velocity
    
    @property
    def rotationVelocity(self):
        return self.rb.rotational_velocity
    
    @position.setter
    def position(self, value):
        if isinstance(value, Vector2D):
            self.rb.position = value

    @rotation.setter
    def rotation(self, value):
        self.rb.orientation = value

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, Vector2D):
            self.rb.velocity = value
    
    @rotationVelocity.setter
    def rotationVelocity(self, value):
        self.rb.rotational_velocity = value
            
    def __init__(self,
            name: str = "Honda Civic",
            position: Vector2D = Vector2D(0, 0),
            rotation: float = 0,
            # stats
            # weight: float = 2800,
            # horsePower: float = 180.0,
            gearSpeed: list = [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0], # 4 gears
            # transmissionRatio: list = [3.153, 3.250, 1.909, 1.250, 0.909, 0.702],
            # tireWear: float = 0.75,
            # bodyWear: float = 0.9,
            # controlls
            steeringSpeed: float = 15.0, # how fast the wheel turns
            steeringReturnSpeed: float = 15.0, # how fast the wheel turns back to center
            throttleSpeed: float = 0.6, # how fast the throttle goes up and down
            brakingSpeed: float = 0.4, # how fast the brake pedal goes up and down
            maxSteeringAngle: float = 45.0, # maximum steering angle in degrees
        ):
        super().__init__()
        self.name = name
        # physics
        self.rb = RigidBody2D(position, 23, 69, math.radians(rotation), 1.0, 2.5, 5.0)
        self.collider = RectangleCollision(self.rb.position, self.rb.width, self.rb.height, self.rb.orientation)
        # input
        self.steeringSpeed = steeringSpeed
        self.steeringReturnSpeed = steeringReturnSpeed
        self.throttleSpeed = throttleSpeed
        self.brakingSpeed = brakingSpeed
        self.maxSteeringAngle = math.radians(maxSteeringAngle)
        self.steeringAngle = 0.0 # range from -1.0 to 1.0
        self.steering = False
        self.braking = False
        self.brakes = 0.0
        self.accelerating = False
        self.throttle = 0.0
        # meta data
        self.frontTireOffset = [
            Vector2D(11.5, -30),
            Vector2D(-11.5, -30),
        ]
        self.rearTireOffset = [
            Vector2D(11.5, 30),
            Vector2D(-11.5, 30),
        ]
        self.driveType = DriveType.REAR

        # settings
        # gear -1 = reverse
        # gear 0 = neutral
        # gear >1 = forward
        
        self.handBrake = False
        # self.tireWear = tireWear # range for tireWear is 0.0 to 1.0 where 0.0 is where u ride on the rims and 1.0 is perfectly new race tires
        # self.bodyWear = bodyWear # range for bodywear is 0.0 to 1.0 where 0.0 is ur riding a wreck and 1.0 is perfectly new race car
        self.gearSpeed = gearSpeed
        self.maxGears = len(self.gearSpeed) - 2
        self.gear = 0
        self.frontDriftGrip = 1.0
        self.rearDriftGrip = 0.0
        self.frontGrip = 0.95
        self.rearGrip = 0.95

    def GetSpeed(self):
        return self.gearSpeed[self.gear+1]

    def ShiftUp(self):
        self.gear = clamp(self.gear+1, -1, self.maxGears)

    def ShifDown(self):
        self.gear = clamp(self.gear-1, -1, self.maxGears)

    def HandleInput(self, deltaTime, events):
        keys = pygame.key.get_pressed()
        
        # keypresses
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    self.ShiftUp()
                if event.key == pygame.K_LCTRL:
                    self.ShifDown()
        # handle steering input
        if keys[pygame.K_LEFT]:
            self.steering = True
            self.steeringAngle = clamp(self.steeringAngle - (self.steeringSpeed * deltaTime), -1.0, 1.0)
        if keys[pygame.K_RIGHT]:
            self.steering = True
            self.steeringAngle = clamp(self.steeringAngle + (self.steeringSpeed * deltaTime), -1.0, 1.0)
        if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.steering = False
        # turn steering wheel back if user isnt controlling it
        if self.steeringAngle > 0.0 and not self.steering:
            self.steeringAngle = clamp(self.steeringAngle - (self.steeringReturnSpeed * deltaTime), -1.0, 1.0)
        if self.steeringAngle < 0.0 and not self.steering:
            self.steeringAngle = clamp(self.steeringAngle + (self.steeringReturnSpeed * deltaTime), -1.0, 1.0)
        # handle throttle and braking input
        if keys[pygame.K_UP]:
            self.accelerating = True
            self.throttle = clamp(self.throttle + (self.throttleSpeed * deltaTime), 0.0, 1.0)
        else:
            self.accelerating = False
            self.throttle = clamp(self.throttle - (self.throttleSpeed * deltaTime), 0.0, 1.0)
        if keys[pygame.K_DOWN]:
            self.braking = True
            self.brakes = clamp(self.brakes + (self.brakingSpeed * deltaTime), 0.0, 1.0)
        else:
            self.braking = False
            self.brakes = clamp(self.brakes - (self.brakingSpeed * deltaTime), 0.0, 1.0)
        # handbrake (drift king)
        if keys[pygame.K_SPACE]:
            self.handBrake = True
        else:
            self.handBrake = False
            
        # print(f"{self.braking} {round(self.brakes, 2)}, {self.accelerating} {round(self.throttle, 2)}, {round(self.steeringAngle, 2)}, {round(self.position.x, 2)} {round(self.position.y, 2)}")

    def Update(self, deltaTime, events):
        self.HandleInput(deltaTime, events)
        
        force = RotateVector(Vector2D(0, -1.0) * self.throttle, self.rotation, True)
        
        self.forces = []
        self.tireForces = []
        for i, tire in enumerate(self.frontTireOffset):
            # set tire location relative to car and rotate it
            location = self.position + RotateVector(tire, self.rotation, True)
            # set force applied to tire into tire direction (still gotta do hp rpm etc)
            if self.driveType == DriveType.ALL or self.driveType == DriveType.FRONT:
                force = RotateVector(Vector2D(0, -1) * self.GetSpeed() * self.throttle, self.rotation+(self.maxSteeringAngle * self.steeringAngle), True) * deltaTime
            else:
                force = RotateVector(Vector2D(0, -1) * 1.0 * self.throttle, self.rotation+(self.maxSteeringAngle * self.steeringAngle), True) * deltaTime
            # calculate force required to aid in steering
            rightVel = Vector2D.DotProduct(self.rb.GetPointVelocity(location), RotateVector(Vector2D(-1, 0), self.rotation+(self.maxSteeringAngle * self.steeringAngle), True))
            rotatedPushForce = RotateVector(Vector2D(rightVel, 0), self.rotation+(self.maxSteeringAngle * self.steeringAngle), True) * (self.frontDriftGrip if (self.handBrake) else self.frontGrip) * deltaTime
            # apply force at tire position
            self.rb.AddForceAtPosition(rotatedPushForce, location)
            self.rb.AddForceAtPosition(force, location)
            self.forces.append(force)
            self.tireForces.append(rotatedPushForce)
        for i, tire in enumerate(self.rearTireOffset):
            # set tire location relative to car and rotate it
            location = self.position + RotateVector(tire, self.rotation, True)
            # set force applied to tire into tire direction (still gotta do hp rpm etc)
            if self.driveType == DriveType.ALL or self.driveType == DriveType.REAR:
                force = RotateVector(Vector2D(0, -1) * self.GetSpeed() * self.throttle, self.rotation, True) * 1000 * deltaTime
            else:
                force = RotateVector(Vector2D(0, -1) * 1.0 * self.throttle, self.rotation, True) * 1000 * deltaTime
            # calculate force required to aid in steering
            rightVel = Vector2D.DotProduct(self.rb.GetPointVelocity(location), RotateVector(Vector2D(-1, 0), self.rotation, True))
            rotatedPushForce = RotateVector(Vector2D(rightVel, 0), self.rotation, True) * (self.rearDriftGrip if (self.handBrake) else self.rearGrip) * deltaTime
            # apply force at tire position
            self.rb.AddForceAtPosition(rotatedPushForce, location)
            self.rb.AddForceAtPosition(force, location)
            self.forces.append(force)
            self.tireForces.append(rotatedPushForce)
            
        self.rb.update(deltaTime)
        self.collider.UpdatePositions(self.rb.position, self.rb.orientation)

if __name__ == "__main__":
    pygame.display.init()
    screen = pygame.display.set_mode((720, 480), pygame.RESIZABLE)
    pygame.display.set_caption("NASCAR")
    clock = pygame.time.Clock()
    running = True
    paused = False
    screenWidth, screenHeight = pygame.display.get_surface().get_size()
    car = Car("UwU", Vector2D(40, 40), 90)
    wall = Wall(Vector2D(screenWidth//2, screenHeight//2), 50, 50, 0)
    entities = [car, wall]
    carImage = pygame.image.load("./assets/sprites/Annett-car2.jpg")
    carRect = carImage.get_rect()
    while running:
        dt = clock.tick(0) / 1000.0
        pygame.event.pump()
        events = pygame.event.get()

        colliderHit = False
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        if not paused:
            for entity in entities:
                if entity.active:
                    entity.Update(dt, events)
            filteredEntites = [e for e in entities if e.active and e.collision and hasattr(e, "collider")]
            for i in range(len(filteredEntites)):
                for j in range(i+1, len(filteredEntites)):
                    entity1 = filteredEntites[i]
                    entity2 = filteredEntites[j]
                    colliderHit = entity1.collider.CheckCollision(entity2.collider)
                        
        screen.fill((0, 0, 0, 255))
        for entity in entities:
            # draw collision masks
            points = entity.collider.GetPoints(entity.collider)
            if colliderHit:
                pygame.draw.polygon(screen, (255, 0, 0), [(p.x, p.y) for p in points], 1)
            else:
                pygame.draw.polygon(screen, (255, 255, 255), [(p.x, p.y) for p in points], 1)
            
            
            if isinstance(entity, Car):
                rotatedTire1 = RotateVector(entity.frontTireOffset[0], entity.rotation, True)
                rotatedTire2 = RotateVector(entity.frontTireOffset[1], entity.rotation, True)
                center1 = (entity.position.x+rotatedTire1.x, entity.position.y+rotatedTire1.y)
                center2 = (entity.position.x+rotatedTire2.x, entity.position.y+rotatedTire2.y)
                pygame.draw.circle(screen, (255, 255, 255), center1, 2)
                pygame.draw.circle(screen, (255, 255, 255), center2, 2)
                
                rearrotatedTire1 = RotateVector(entity.rearTireOffset[0], entity.rotation, True)
                rearrotatedTire2 = RotateVector(entity.rearTireOffset[1], entity.rotation, True)
                center11 = (entity.position.x+rearrotatedTire1.x, entity.position.y+rearrotatedTire1.y)
                center22 = (entity.position.x+rearrotatedTire2.x, entity.position.y+rearrotatedTire2.y)
                pygame.draw.circle(screen, (255, 0, 0), center11, 2)
                pygame.draw.circle(screen, (255, 0, 0), center22, 2)

                # draw velocity vector
                pygame.draw.line(screen, (255, 255, 0), (entity.position.x, entity.position.y), (entity.position.x+entity.velocity.x/100, entity.position.y+entity.velocity.y/100), 2)
                
                # draw forces on wheels
                centers = [center1, center2, center11, center22]
                for i, force in enumerate(entity.forces):
                    pygame.draw.line(screen, (0, 0, 255), centers[i], (centers[i][0]+(force.x), centers[i][1]+(force.y)), 2)
                for i, force in enumerate(entity.tireForces):
                    pygame.draw.line(screen, (255, 0, 0), centers[i], (centers[i][0]+(force.x*5), centers[i][1]+(force.y*5)), 2)
            
        pygame.display.flip()
