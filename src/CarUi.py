import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Speedometer")

# Set up colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Set up font
font = pygame.font.Font(None, 36)

# Set up speedometer parameters
speed = 0
speed_limit = 321
rpm = 0
rpm_limit = 9000

# Transmission parameters
current_gear = 1
gear_ratios = [3.5, 2.5, 1.8, 1.3, 1.0]
final_drive_ratio = 3.9  # Adjust this based on your car's characteristics

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Increase or decrease speed with arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        speed = min(speed + 2, speed_limit)
    else:
        speed = max(speed - 1, 0)

    if keys[pygame.K_DOWN]:
        speed = max(speed - 1.5, 0)

    # Determine gear based on speed
    if speed < 50:
        current_gear = 1
    elif speed < 100:
        current_gear = 2
    elif speed < 150:
        current_gear = 3
    elif speed < 200:
        current_gear = 4
    else:
        current_gear = 5

    # Calculate RPM based on speed, gear, and other parameters
    wheel_circumference = 2 * math.pi * 0.5  # Assuming a tire radius of 0.5 units (adjust based on your scale)
    axle_ratio = final_drive_ratio * gear_ratios[current_gear - 1]
    rpm = (speed / (wheel_circumference * axle_ratio)) * 45 * 30 / math.pi  # Convert speed to RPM

    # Cap RPM at the limit
    rpm = min(rpm, rpm_limit)

    # Update the display
    screen.fill(black)

    # Draw speedometer background
    pygame.draw.circle(screen, white, (width // 1.5, height // 2), 150)
    pygame.draw.circle(screen, black, (width // 1.5, height // 2), 140)

    # Draw rpmmeter background
    pygame.draw.circle(screen, white, (width // 3, height // 2), 150)
    pygame.draw.circle(screen, black, (width // 3, height // 2), 140)

    # Draw speedometer needle
    angle = 180 - (speed / speed_limit) * 180  # Convert speed to angle (180 to 0 degrees)
    angle_rad = math.radians(angle)
    needle_length = 120
    end_point = (width // 1.5 + needle_length * math.cos(angle_rad), height // 2 - needle_length * math.sin(angle_rad))
    pygame.draw.line(screen, red, (width // 1.5, height // 2), (int(end_point[0]), int(end_point[1])), 5)

    # Display speed value
    speed_text = font.render(f"Speed: {speed}", True, white)
    screen.blit(speed_text, (625, 150))

    # Draw rpm needle
    angle = 180 - (rpm / rpm_limit) * 180  # Convert RPM to angle (180 to 0 degrees)
    angle_rad = math.radians(angle)
    end_point = (width // 3 + needle_length * math.cos(angle_rad), height // 2 - needle_length * math.sin(angle_rad))
    pygame.draw.line(screen, red, (width // 3, height // 2), (int(end_point[0]), int(end_point[1])), 5)

    # Display rpm value
    rpm_text = font.render(f"Rpm: {int(rpm)}", True, white)
    screen.blit(rpm_text, (300, 150))

    # Display current gear
    gear_text = font.render(f"Gear: {current_gear}", True, white)
    screen.blit(gear_text, (width // 2 - gear_text.get_width() // 2, height - 100))

    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
