import pygame
import sys
from pygame.locals import QUIT
from vector2d import Vector2D
from math import cos, sin, radians, degrees

class RigidBody2D:
    def __init__(self, position, width, height, rotation=0, mass=1.0, rotational_damping=0.05, velocity_damping=0.05):
        self.position = position
        self.width = width
        self.height = height
        self.mass = mass
        self.velocity = Vector2D(0, 0)
        self.orientation = rotation # in radians
        self.rotational_velocity = 0
        self.rotational_damping = rotational_damping
        self.velocity_damping = velocity_damping

    def AddForceAtPosition(self, force, position):
        # apply linear velocity
        self.velocity.x += force.x / self.mass
        self.velocity.y += force.y / self.mass
        # calculate torque based on position and force
        torque = (position.x - self.position.x) * force.y - (position.y - self.position.y) * force.x
        # calculate rotational acceleration using torque and moment of inertia
        moment_of_inertia = 0.5 * self.mass * (self.width**2 + self.height**2)
        rotational_acceleration = torque / moment_of_inertia
        # apply torque to rotational velocity
        self.rotational_velocity += rotational_acceleration
        
    def GetPointVelocity(self, point):
        # Calculate the distance from the center of mass to the point
        r_x = point.x - self.position.x
        r_y = point.y - self.position.y

        # Calculate the velocity components due to rotation
        v_rot_x = -r_y * self.rotational_velocity
        v_rot_y = r_x * self.rotational_velocity

        # Combine linear velocity and rotational velocity to get the point velocity
        point_velocity_x = self.velocity.x + v_rot_x
        point_velocity_y = self.velocity.y + v_rot_y

        return Vector2D(point_velocity_x, point_velocity_y)

    def update(self, deltaTime):
        # apply velocity
        self.position.x += self.velocity.x * deltaTime
        self.position.y += self.velocity.y * deltaTime
        self.orientation += self.rotational_velocity * deltaTime
        # drag
        self.rotational_velocity -= self.rotational_velocity * self.rotational_damping * deltaTime
        self.velocity.x -= self.velocity.x * self.velocity_damping * deltaTime
        self.velocity.y -= self.velocity.y * self.velocity_damping * deltaTime

    def get_rotated_points(self):
        half_width = self.width / 2
        half_height = self.height / 2
        cos_theta = cos(self.orientation)
        sin_theta = sin(self.orientation)
        x1 = self.position.x + half_width * cos_theta - half_height * sin_theta
        y1 = self.position.y + half_width * sin_theta + half_height * cos_theta
        x2 = self.position.x - half_width * cos_theta - half_height * sin_theta
        y2 = self.position.y - half_width * sin_theta + half_height * cos_theta
        x3 = self.position.x - half_width * cos_theta + half_height * sin_theta
        y3 = self.position.y - half_width * sin_theta - half_height * cos_theta
        x4 = self.position.x + half_width * cos_theta + half_height * sin_theta
        y4 = self.position.y + half_width * sin_theta - half_height * cos_theta
        return [
            Vector2D(x1, y1),
            Vector2D(x2, y2),
            Vector2D(x3, y3),
            Vector2D(x4, y4)
        ]


if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('RigidBody2D Force Test')

    rect_body = RigidBody2D(Vector2D(200, 200), 30, 60, radians(45), 10)

    clock = pygame.time.Clock()
    hit = False
    frame = 0

    while True:
        frame += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if not hit and frame >= 60:
            # Apply force at a specific position
            force = Vector2D(100, 0)
            # application_position = rect_body.position
            application_position = Vector2D(0, 0)
            application_position = Vector2D(200-15, 200-30)
            rect_body.AddForceAtPosition(force, application_position)
            hit = True

        # Update the rigid body for each frame
        delta_time = clock.tick(60) / 1000.0  # Frame rate of 60 frames per second
        rect_body.update(delta_time)

        # Draw the rectangle on the screen
        screen.fill((0, 0, 0))  # Clear the screen

        # Draw the rotated rectangle
        rotated_points = rect_body.get_rotated_points()
        pygame.draw.polygon(screen, (255, 255, 255), [(p.x, p.y) for p in rotated_points], 2)

        pygame.display.flip()  # Update the display
