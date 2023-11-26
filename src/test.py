import pygame
import sys
from pygame.locals import QUIT
from vector2d import Vector2D
from math import cos, sin

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class RigidBody2D:
    def __init__(self, position, width, height, mass=1.0, rotational_damping=0.98, velocity_damping=0.98):
        self.position = position
        self.width = width
        self.height = height
        self.mass = mass
        self.velocity = Vector2D(0, 0)
        self.orientation = 0  # in radians
        self.rotational_velocity = 0
        self.rotational_damping = rotational_damping
        self.velocity_damping = velocity_damping

    def add_force_at_position(self, force, position):
        # Calculate linear acceleration based on the applied force
        acceleration = Vector2D(force.x / self.mass, force.y / self.mass)

        # Update velocity based on linear acceleration
        self.velocity.x += acceleration.x
        self.velocity.y += acceleration.y

        # Calculate torque based on the applied force and position
        torque = (position.x - self.position.x) * force.y - (position.y - self.position.y) * force.x

        # Calculate rotational acceleration using torque and moment of inertia
        moment_of_inertia = 0.5 * self.mass * (self.width**2 + self.height**2)
        rotational_acceleration = torque / moment_of_inertia

        # Update rotational velocity based on rotational acceleration
        self.rotational_velocity += rotational_acceleration

    def update(self, delta_time):
        # Update position based on the current velocity and delta time
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Update orientation based on the current rotational velocity and delta time
        self.orientation += self.rotational_velocity * delta_time

        # Apply rotational damping to reduce rotational velocity over time
        self.rotational_velocity *= self.rotational_damping
        self.velocity.x *= self.velocity_damping
        self.velocity.y *= self.velocity_damping

    def get_rotated_points(self):
        # Calculate the rotated points of the rectangle
        half_width = self.width / 2
        half_height = self.height / 2

        # Calculate the rotated points
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

# Pygame setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('RigidBody2D Force Test')

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Create a RigidBody2D instance
rect_body = RigidBody2D(Vector2D(200, 200), 30, 60, 1)

# Main game loop
clock = pygame.time.Clock()
hit = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if not hit:
        # Apply force at a specific position
        force = Vector2D(100, 0)
        # application_position = rect_body.position
        application_position = Vector2D(0, 0)
        rect_body.add_force_at_position(force, application_position)
        hit = True

    # Update the rigid body for each frame
    delta_time = clock.tick(60) / 1000.0  # Frame rate of 60 frames per second
    rect_body.update(delta_time)

    # Draw the rectangle on the screen
    screen.fill((0, 0, 0))  # Clear the screen

    # Draw the rotated rectangle
    rotated_points = rect_body.get_rotated_points()
    pygame.draw.polygon(screen, WHITE, [(p.x, p.y) for p in rotated_points], 2)

    pygame.display.flip()  # Update the display
