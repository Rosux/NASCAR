from vector2d import Vector2D
from Entity import Entity
from Utils import clamp, RotateVector, clampVector, Magnitude
from random import random
from Collision import RectangleCollision
import math
import pygame


class Car(Entity):
    """Create a car object to controll

    Args:
        name (str, optional): give a name to the car. Defaults to "Honda Civic".
        position (Vector2D, optional): give a position to the car. Defaults to Vector2D(0, 0).
        rotation (float, optional): give a rotation to the car. Defaults to 0.
        weight (float, optional): weight of the car in kg. Defaults to 2800.
        horsePower (float, optional): horsepower of the car. Defaults to 180.0.
        transmissionRatio (list, optional): transmission ratios of the car, first item in list is reverse gear the rest is 1st and so on. the gears ammount is also calculated from this list. Defaults to [3.153, 3.250, 1.909, 1.250, 0.909, 0.702].
        turbo (bool, optional): if the car has a turbocharger or not. Defaults to False.
        tireWear (float, optional): how much the tires are worn in range of 0.0 to 1.0 where 1.0 is perfect and 0.0 is ruined. Defaults to 0.75.
        bodyWear (float, optional): how much the body is worn in range of 0.0 to 1.0 where 1.0 is perfect and 0.0 is ruined. Defaults to 0.9.
        maxRpm (int, optional): maximum rpm of the car. Defaults to 7800.
        maxTurboPSI (float, optional): maximum turbo psi. Defaults to 14.0.
    """
    def __init__(self,
            name: str = "Honda Civic",
            position: Vector2D = Vector2D(0, 0),
            rotation: float = 0,
            # stats
            weight: float = 2800,
            horsePower: float = 180.0,
            transmissionRatio: list = [3.153, 3.250, 1.909, 1.250, 0.909, 0.702],
            turbo: bool = False,
            tireWear: float = 0.75,
            bodyWear: float = 0.9,
            # limits
            maxRpm: int = 7800,
            idleRpm: int = 2300,
            maxTurboPSI: float = 2.0,
            minTurboPSI: float = -1.0,
            # controlls
            steeringSpeed: float = 1.0, # how fast the wheel turns
            steeringReturnSpeed: float = 2.0, # how fast the wheel turns back to center
            throttleSpeed: float = 0.6,
            brakingSpeed: float = 0.4,
            maxSteeringAngle: float = 40.0,
        ):
        super().__init__()
        self.name = name
        self.position = Vector2D(position.x, position.y)
        self.velocity = Vector2D(0, 0)
        self.rotation = rotation
        self.angularVelocity = 0
        self.collider = RectangleCollision(self.position, 23, 69, self.rotation)
        self.steeringSpeed = steeringSpeed
        self.steeringReturnSpeed = steeringReturnSpeed
        self.throttleSpeed = throttleSpeed
        self.brakingSpeed = brakingSpeed
        self.maxSteeringAngle = maxSteeringAngle
        self.transmissionRatio = transmissionRatio

        # settings
        self.hasTurbo = turbo
        self.maxRpm = maxRpm
        self.idleRpm = idleRpm
        self.maxTurboPSI = maxTurboPSI
        self.minTurboPSI = minTurboPSI
        # gear -1 = reverse
        # gear 0 = neutral
        # gear >1 = forward
        self.maxGears = len(transmissionRatio)-1
        
        # changing variables for calculating physics
        self.speed = 0.0
        # -1.0 = steering to the left
        # 1.0 = steering to the right
        # 0.0 = center
        self.steeringAngle = 0.0
        self.steering = False
        self.rpm = 0
        self.turboPSI = self.minTurboPSI
        self.gear = 0
        self.braking = False
        self.brakes = 0.0
        self.accelerating = False
        self.throttle = 0.0
        self.handBrake = False
        self.mass = weight
        self.horsePower = horsePower
        self.downForce = 0.5 # range for downforce is 0.0 to 1.0 where 0.0 is no downforce (u spin) and 1.0 is full downforce (u cant even turn idk)
        self.tireWear = tireWear # range for tireWear is 0.0 to 1.0 where 0.0 is where u ride on the rims and 1.0 is perfectly new race tires
        self.bodyWear = bodyWear # range for bodywear is 0.0 to 1.0 where 0.0 is ur riding a wreck and 1.0 is perfectly new race car
        self.grip = 1.0 # range of grip is 0.0 to 1.0 where 0.0 is no grip at all and 1.0 is full grip

    def GetTransmissionRatio(self):
        if self.gear == -1:
            return self.transmissionRatio[0]
        elif self.gear == 0:
            return 0.0
        elif self.gear > 0 and self.gear <= self.maxGears:
            return self.transmissionRatio[self.gear]

    def ShiftUp(self):
        self.gear = clamp(self.gear+1, -1, self.maxGears)
        self.turboPSI = self.minTurboPSI

    def ShifDown(self):
        self.gear = clamp(self.gear-1, -1, self.maxGears)
        self.turboPSI = self.minTurboPSI

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

    def GetEngineForce(self):
        if self.hasTurbo:
            return self.throttle * ((self.horsePower * clamp(self.turboPSI, 1.0, self.turboPSI)) * self.GetTransmissionRatio())
        else:
            return self.throttle * (self.horsePower * self.GetTransmissionRatio())

    # def GetEngineRPM(self):
    #     if Magnitude(self.velocity) == 0:
    #         return self.idleRpm
    #     rpm = Magnitude(self.velocity) / (60*2*math.pi*10) * self.GetTransmissionRatio() * 1000
    #     # rpm = ((self.GetEngineForce() * self.GetTransmissionRatio() * 60) / (2 * math.pi * 0.3 * Magnitude(self.velocity)))
    #     print(f"{self.GetEngineForce():.2f}, {(rpm):.2f}")
    #     return rpm

    def Update(self, deltaTime, events):
        self.HandleInput(deltaTime, events)
        
        if self.accelerating:
            self.velocity.y += self.GetEngineForce() * deltaTime
        if self.braking:
            self.velocity.y -= self.GetEngineForce()/4 * deltaTime
        
        # calculate the drag
        drag = 0.01 * self.mass * self.grip
        if self.velocity.y < 0:
            self.velocity.y = clamp(self.velocity.y - drag * deltaTime, -10000000.0, 0.0)
        if self.velocity.y > 0:
            self.velocity.y = clamp(self.velocity.y - drag * deltaTime, 0.0, 10000000.0)

        # rotate velocity in cars direction
        radians = self.rotation * (math.pi/180)
        self.velocity = Vector2D(round(self.velocity.x * math.cos(radians) - self.velocity.y * math.sin(radians), 10), round(self.velocity.x * math.sin(radians) + self.velocity.y * math.cos(radians), 10))
        
        # self.GetEngineRPM()
        # print(Magnitude(self.velocity))
        # print(self.velocity)
        # print(self.gear, self.maxGears, self.GetTransmissionRatio(), self.transmissionRatio)
        
        self.position += self.velocity/100000
        
        # apply velocity to the position and rotation
        # self.angularVelocity -= angulareDrag * self.angularVelocity * deltaTime
        # self.rotation += self.angularVelocity * deltaTime
        # self.position += self.velocity * deltaTime
        # self.collider.UpdatePositions(self.position, self.rotation)
        # print(self.velocity, self.rotation)
        # this runs each frame, use deltaTime to calculate physics stuff and timings. (yes i made it stfu declan <3)
        # here you should update the cars position and rotation based on its properties like horsePower, speed, braking, accelerating and steeringAngle
        # if self.accelerating:
        #     self.rpm += 10 * deltaTime
        # if self.braking:
        #     self.rpm -= 10 * deltaTime
        
        # self.speed += someAmmount * gear * rpm * horsepower * deltaTime # some example of speed increase (speed should be increased if accelerating and should be increased by an ammount made from combining the car settings etc)


if __name__ == "__main__":
    pygame.display.init()
    screen = pygame.display.set_mode((720, 480), pygame.RESIZABLE)
    pygame.display.set_caption("NASCAR")
    clock = pygame.time.Clock()
    running = True
    paused = False
    screenWidth, screenHeight = pygame.display.get_surface().get_size()
    car = Car("UwU", Vector2D(screenWidth//2, screenHeight//2), 0)
    entities = [car]
    carImage = pygame.image.load("./assets/sprites/Annett-car2.jpg")
    carRect = carImage.get_rect()
    while running:
        dt = clock.tick(0) / 1000.0
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        if not paused:
            for entity in entities:
                if entity.active:
                    entity.Update(dt, events)
        screen.fill((0, 0, 0, 255))
        for entity in entities:
            rotatedCar = pygame.transform.rotate(pygame.transform.scale(carImage, (entity.collider.height, entity.collider.width)), entity.rotation+90)
            rotatedRect = rotatedCar.get_rect(center=(entity.position.x, entity.position.y))
            screen.blit(rotatedCar, rotatedRect)
        pygame.display.flip()
