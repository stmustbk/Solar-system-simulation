import pygame
import math
import tkinter as tk
from tkinter import simpledialog

pygame.init()

WIDTH, HEIGHT = 800, 800

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Planet Simulation")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)
BROWN = (150, 75, 0)
ORANGE = (255, 128, 0)

FONT = pygame.font.SysFont("comicsans", 16)  # Font for displaying text


class Planet:
    AU = 149.6e6 * 1000  # Astronomical Unit in meters
    G = 6.67428e-11  # Gravitational constant
    SCALE = 250 / AU  # Scale for displaying distances on the screen
    TIMESTEP = 3600 * 24  # 1 day in seconds

    def __init__(self, x, y, radius, color, mass, name=""):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = name

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        # Convert the planet's position to screen coordinates
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        # Draw the orbit of the planet
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px, py = point
                px = px * self.SCALE + WIDTH / 2
                py = py * self.SCALE + HEIGHT / 2
                updated_points.append((px, py))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        # Draw the planet
        pygame.draw.circle(win, self.color, (x, y), self.radius)

        # Display the planet's name
        name_text = FONT.render(self.name, True, WHITE)
        win.blit(name_text, (x - name_text.get_width() / 2, y - self.radius - 20))

        # Display the distance to the Sun (for non-Sun objects)
        if not self.sun:
            distance_text = FONT.render(f"{self.distance_to_sun / Planet.AU:.2f} AU", True, WHITE)
            win.blit(distance_text, (x - distance_text.get_width() / 2, y + self.radius + 5))

    def attraction(self, other):
        # Calculate gravitational force exerted by 'other' on this planet
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)
        if other.sun:
            self.distance_to_sun = distance
        force = self.G * self.mass * other.mass / (max(1,distance)**2)

        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        # Update the planet's position based on gravitational forces
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        # Update velocity and position
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))


def add_body_dialog(planets):
    """Adds a new body through a Tkinter dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Request the target planet's name
    planet_name = simpledialog.askstring("Input", "Enter the name of the planet to launch the body from (Sun/Earth/Mercury/Venus):")
    target_planet = next((p for p in planets if p.name.lower() == planet_name.lower()), None)

    if not target_planet:
        print("No such planet exists!")
        return None

    # Request other parameters
    angle = simpledialog.askfloat("Input", "Enter the launch angle in degrees (0-360):")
    velocity = simpledialog.askfloat("Input", "Enter the initial velocity of the body (m/s):")
    mass = simpledialog.askfloat("Input", "Enter the mass of the body (kg):")


    # Calculate initial position and velocities of the body
    x = target_planet.x
    y = target_planet.y

    angle_rad = math.radians(angle)
    x_vel = velocity * math.cos(angle_rad)
    y_vel = velocity * math.sin(angle_rad)

    new_body = Planet(x, y, 5, WHITE, mass, "NewBody")
    new_body.x_vel = target_planet.x_vel + x_vel
    new_body.y_vel = target_planet.y_vel + y_vel
    return new_body



def main():
    run = True
    clock = pygame.time.Clock()
    paused = False

    # Define planets
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30, "Sun")
    sun.sun = True
    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24, "Earth")
    earth.y_vel = 29.765 * 1000
    mercury = Planet(-0.387 * Planet.AU, 0, 8, BROWN, 3.3 * 10**23, "Mercury")
    mercury.y_vel = 48 * 1000
    venus = Planet(-0.723 * Planet.AU, 0, 15, ORANGE, 4.867 * 10**24, "Venus")
    venus.y_vel = 35 * 1000
    planets = [sun, mercury, venus, earth]

    while run:
        clock.tick(60)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused  # Toggle pause
                elif event.key == pygame.K_a:  # Press "A" to add a new body
                    new_body = add_body_dialog(planets)
                    if new_body:
                        planets.append(new_body)
                elif event.key == pygame.K_UP:  # Increase simulation speed
                    Planet.TIMESTEP = min(3600 * 24, Planet.TIMESTEP * 2)  # Max 10 days
                    print(f"Simulation speed increased: TIMESTEP = {Planet.TIMESTEP} seconds")
                elif event.key == pygame.K_DOWN:  # Decrease simulation speed
                    Planet.TIMESTEP = max(3600, Planet.TIMESTEP / 2)  # Minimum 1 hour
                    print(f"Simulation speed decreased: TIMESTEP = {Planet.TIMESTEP} seconds")

        if not paused:
            for planet in planets:
                planet.update_position(planets)

        for planet in planets:
            planet.draw(WIN)

        pygame.display.update()

    pygame.quit()

main()
