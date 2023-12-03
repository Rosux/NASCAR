from vector2d import Vector2D
from Entity import Entity
from Utils import clamp, RotateVector, clampVector, Magnitude, Dot
from random import random, uniform
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

class CarAI(Entity):
    
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
            steeringSpeed: float = 1.0, # how fast the wheel turns
            steeringReturnSpeed: float = 1.0, # how fast the wheel turns back to center
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
        self.speef = 0
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
        self.rpm = 0
        self.rpm_limit = 9000
        self.minRpm = 2000
        self.maxRpm = 6500
        self.xxx = 0
        self.oldRandomFactor = uniform(0, 450)
        self.speed_limit = 320
        # settings
        # gear -1 = reverse
        # gear 0 = neutral
        # gear >1 = forward
        
        self.handBrake = False
        # self.tireWear = tireWear # range for tireWear is 0.0 to 1.0 where 0.0 is where u ride on the rims and 1.0 is perfectly new race tires
        # self.bodyWear = bodyWear # range for bodywear is 0.0 to 1.0 where 0.0 is ur riding a wreck and 1.0 is perfectly new race car
        self.gearSpeed = gearSpeed
        self.maxGears = len(self.gearSpeed) - 2
        self.gear = 1
        self.frontDriftGrip = 1.0
        self.rearDriftGrip = 0.0
        self.frontGrip = 0.95
        self.rearGrip = 0.95
        self.paused = False
    
    def GetSpeef(self):
        cc = self.rb.GetPointVelocity(self.rb.position)
        self.speef = (Magnitude(cc) / 1500) * 300
        return self.speef
    
    def GetRpm(self):
        self.xxx += 1
        if self.xxx >= 10:
            self.xxx = 0
            self.oldRandomFactor = uniform(0, 250)
        return min(self.rpm + self.oldRandomFactor, self.rpm_limit)
    
    def GetSpeed(self):
        return self.gearSpeed[self.gear+1]

    def ShiftUp(self):
        if self.gear == 0 or self.gear == -1 or self.GetSpeef() >= 0.9 * self.speed_limit:    
            if self.paused:
                return
            self.gear = clamp(self.gear+1, -1, self.maxGears)
            if self.gear != self.maxGears:
                self.rpm -= self.minRpm

    def ShifDown(self):
        if self.paused:
            return
        self.gear = clamp(self.gear-1, -1, self.maxGears)
        if self.gear != -1:
            self.rpm += self.minRpm

    def HandleInput(self, deltaTime, events):
        self.ShiftUp()
        self.steering = True
        self.steeringAngle = clamp(-0.0068, -1.0, 1.0)
        # turn steering wheel back if user isnt controlling it
        if self.steeringAngle > 0.0 and not self.steering:
            self.steeringAngle = clamp(self.steeringAngle - (self.steeringReturnSpeed * deltaTime), -1.0, 1.0)
        if self.steeringAngle < 0.0 and not self.steering:
            self.steeringAngle = clamp(self.steeringAngle + (self.steeringReturnSpeed * deltaTime), -1.0, 1.0)
        # handle throttle and braking input
        if True:
            self.rpm += 100 * 60 * deltaTime
            self.rpm = min(self.rpm, self.rpm_limit)
            self.accelerating = True
            self.throttle = clamp(self.throttle + (self.throttleSpeed * deltaTime), 0.0, 1.0)
            if self.gear == 1:
                self.speed_limit = 68
            elif self.gear == 2:
                self.speed_limit = 135
            elif self.gear == 3:
                self.speed_limit = 200
            elif self.gear == 4:
                self.speed_limit = 320
            elif self.gear == -1:
                self.speed_limit = 30
        self.braking = False
        self.brakes = clamp(self.brakes - (self.brakingSpeed * deltaTime), 0.0, 1.0)
        # handbrake (drift king)
        self.handBrake = False

    def Update(self, deltaTime, events):
        if self.paused:
            return
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
        
        if self.brakes > 0.0:
            vd = self.rb.velocity_damping
            self.rb.velocity_damping += 15.0 * self.brakes * 1000 * deltaTime
        self.rb.update(deltaTime)
        if self.brakes > 0.0:
            self.rb.velocity_damping = vd
        self.collider.UpdatePositions(self.rb.position, self.rb.orientation)
        return self.rb.velocity

    def Pause(self):
        self.paused = True
    def Start(self):
        self.paused = False

if __name__ == "__main__":
    pygame.display.init()
    screen = pygame.display.set_mode((720, 480), pygame.RESIZABLE)
    pygame.display.set_caption("NASCAR")
    clock = pygame.time.Clock()
    running = True
    paused = False
    screenWidth, screenHeight = pygame.display.get_surface().get_size()
    
    car = Car("UwU", Vector2D(40, 40), 90)
    wall = Wall(Vector2D(screenWidth//2, screenHeight//2), 100, 150, 0)
    
    entities = [car, wall]
    while running:
        dt = clock.tick(0) / 1000.0
        pygame.event.pump()
        events = pygame.event.get()

        colliderHit = False
        pp = []
        
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
                    if isinstance(entity1, Car) and colliderHit:
                        pp = entity2.collider.VerticesInsideOtherShape(entity1)
                    # if colliderHit != False and isinstance(entity1, Car):
                    #     v1 = entity1.rb.position
                    #     v2 = entity2.collider.position
                    #     difference = v1 - v2
                    #     entity1.rb.velocity = -entity1.rb.velocity
                    #     entity1.rb.rotational_velocity = 0
                    #     entity1.rb.AddForceAtPosition(difference, entity1.rb.position)
                        
        screen.fill((0, 0, 0, 255))
        for entity in entities:
            # draw collision masks
            points = entity.collider.GetPoints(entity.collider)
            if colliderHit != False:
                pygame.draw.polygon(screen, (255, 0, 0), [(p.x, p.y) for p in points], 1)
            else:
                pygame.draw.polygon(screen, (255, 255, 255), [(p.x, p.y) for p in points], 1)
            
            if pp:
                for p in pp:
                    pygame.draw.circle(screen, (0, 255, 0), (p.x, p.y), 10)
            
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
