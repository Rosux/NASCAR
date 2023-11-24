from vector2d import Vector2D
from Entity import Entity
from Utils import clamp
from random import random


class Car(Entity):
    def __init__(self, position: Vector2D = Vector2D(0, 0), rotation: float = 0, name: str = "Honda Civic", horsePower: float = 180.0, maxRpm: int = 7800, gears: int = 6, downForce: float = 1.0, turbo: bool = False):
        self.position = position
        self.rotation = rotation
        self.speed = 0.0
        # -1.0 = steering to the left
        # 1.0 = steering to the right
        # 0.0 = center
        self.steeringAngle = 0.0
        self.name = name
        
        # rpm
        self.maxRpm = maxRpm
        self.rpm = 0
        
        # turbo
        self.hasTurbo = turbo
        self.turboPSI = 0.0
        self.maxTurboPSI = 1.0
        self.minTurboPSI = -1.0
        
        # gears
        # gear -1 = reverse
        # gear 0 = neutral
        # gear >1 = forward
        self.gear = 0
        self.maxGears = gears
        
        # car states
        self.braking = False
        self.accelerating = False
        
        # stats
        self.horsePower = horsePower
        self.downForce = downForce # range for downforce is 0.0 to 1.0 where 0.0 is no downforce (u spin) and 1.0 is full downforce (u cant even turn idk)
        self.tireWear = 0.0
        self.maxTireWear = 10.0
        self.bodyWear = 0.0
        self.maxBodyWear = 10.0
        self.grip = 1.0 # range of grip is 0.0 to 1.0 where 0.0 is no grip at all and 1.0 is full grip

    def ShiftUp(self):
        self.gear = clamp(self.gear+1, -1, self.maxGears)
        self.rpm = clamp(self.rpm-1000, 0, self.maxRpm)

    def ShifDown(self):
        self.gear = clamp(self.gear-1, -1, self.maxGears)
        self.rpm = clamp(self.rpm+1000, 0, self.maxRpm)

    def Update(self, deltaTime):
        # this runs each frame, use deltaTime to calculate physics stuff and timings. (yes i made it stfu declan <3)
        # here you should update the cars position and rotation based on its properties like horsePower, speed, braking, accelerating and steeringAngle
        if self.accelerating:
            self.rpm += 10 * deltaTime
        if self.braking:
            self.rpm -= 10 * deltaTime
        # self.speed += someAmmount * gear * rpm * horsepower * deltaTime # some example of speed increase (speed should be increased if accelerating and should be increased by an ammount made from combining the car settings etc)

