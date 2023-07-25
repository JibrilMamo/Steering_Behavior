import pygame
import numpy as np
import random
import math


class Car:
    def __init__(self, x, y, dna=[]):
        # Constants
        self.death_rate = 0.006
        self.lifespan = 1
        self.mr = 0.25
        self.debug = False
        self.angle_radians = 0
        self.maxspeed = 7.5
        self.maxforce = 0.7
        self.size = 15

        # State variables
        self.position = np.array((x, y), dtype=np.float64)
        self.velocity = np.array((0, 1), dtype=np.float64)
        self.acceleration = np.array((0, 0), dtype=np.float64)
        self.speed = 0
        self.dna = [0, 0, 0, 0]
        if dna != []:
            self.dna[0] = dna[0] + random.uniform(-self.mr, self.mr)
            self.dna[1] = dna[1] + random.uniform(-self.mr, self.mr)
            self.dna[2] = dna[2] + random.uniform(-10, 10)
            self.dna[3] = dna[3] + random.uniform(-10, 10)
        else:
            # Random DNA values
            self.dna[0] = random.uniform(-3, 3)
            self.dna[1] = random.uniform(-3, 3)
            self.dna[2] = random.uniform(10, 120)
            self.dna[3] = random.uniform(10, 120)

        self.health = 1
        self.BLACK = (0, 0, 0)
        self.dead = False

    def draw(self, window, show=False):
        # Calculate the rotation angle based on the car's velocity direction
        angle = np.arctan2(self.velocity[1], self.velocity[0])

        # Calculate the points for the modified triangle
        # Front corner (sharp acute point) in the direction of movement
        front_angle = angle
        points = [
            self.position + np.array([np.cos(front_angle) * self.size, np.sin(front_angle) * self.size]),
            self.position + np.array([np.cos(angle + 5 * np.pi / 6) * self.size, np.sin(angle + 5 * np.pi / 6) * self.size]),
            self.position + np.array([np.cos(angle - 5 * np.pi / 6) * self.size, np.sin(angle - 5 * np.pi / 6) * self.size])
        ]

        position_tuple = (int(self.position[0]), int(self.position[1]))

        food_atr = 100 * self.dna[0]
        poison_atr = 100 * self.dna[1]

        food_atr_end_point = (self.position[0] + food_atr * math.cos(self.angle_radians),
                              self.position[1] + food_atr * math.sin(self.angle_radians))

        poison_atr_end_point = (self.position[0] + poison_atr * math.cos(self.angle_radians),
                                self.position[1] + poison_atr * math.sin(self.angle_radians))

        # Draw the line
        if self.debug:
            pygame.draw.circle(window, (0, 255, 0), position_tuple, int(self.dna[2]), 1)
            pygame.draw.circle(window, (255, 0, 0), position_tuple, int(self.dna[3]), 1)
            pygame.draw.line(window, (0, 200, 0), self.position, food_atr_end_point, 4)
            pygame.draw.line(window, (200, 0, 0), self.position, poison_atr_end_point, 2)

        pygame.draw.polygon(window, ((255 * (1 - self.health)), (255 * (self.health)), 0), points)

    def update(self):
        self.lifespan += 1 / 30000
        if (self.mr * (1 / self.lifespan)) >= 0.01:
            self.mr *= (1 / self.lifespan)
        else:
            self.mr = 0.05

        self.angle_radians = math.atan2(self.velocity[1], self.velocity[0])

        self.calc_health(-1 * self.death_rate)
        self.velocity += self.acceleration
        current_speed = np.linalg.norm(self.velocity)

        if current_speed > self.maxspeed:
            limited_velocity = self.velocity * (self.maxspeed / current_speed)
            self.velocity = limited_velocity

        self.speed = current_speed  # Track the current speed
        self.position += self.velocity
        self.acceleration *= 0

    def apply_force(self, force):
        self.acceleration += force

    def seek(self, target):  # target must be an np vector
        desired = target - self.position
        current_magnitude = np.linalg.norm(desired)
        normalized_vector = desired / current_magnitude
        desired = normalized_vector * self.maxspeed

        steer = desired - self.velocity
        current_magnitude = np.linalg.norm(steer)

        if current_magnitude > self.maxforce:
            normalized_vector = steer / current_magnitude
            limited_vector = normalized_vector * self.maxforce
            steer = limited_vector

        # self.apply_force(steer)
        return steer

    def behavior(self, good, bad):
        steerG = self.eat(good, 0.9, self.dna[2], True)
        steerG *= self.dna[0]
        self.apply_force(steerG)

        steerB = self.eat(bad, 0, self.dna[3], False)
        steerB *= self.dna[1]
        self.apply_force(steerB)

    def calc_health(self, diet):
        self.health += diet
        if self.health <= 0:
            self.health = 0
            self.lifespan = 0
            self.dead = True
        if self.health >= 1:
            self.health = 1

    def eat(self, l, diet, perception, can_eat):
        temp = float('inf') - 1
        closest = None

        for i in range(len(l) - 1, -1, -1):
            d = np.linalg.norm(l[i] - self.position)

            if can_eat:
                if d < self.maxspeed:
                    l.pop(i)
                    self.calc_health(diet)
                elif d < temp and d <= perception:
                    temp = d
                    closest = l[i]
            elif d < temp and d <= perception:
                temp = d
                closest = l[i]

        if closest is not None:
            return self.seek(closest)

        return np.array((0, 0), dtype=np.float64)

    def boundaries(self, width, height):
        d = 15
        desired = None

        if self.position[0] < d:
            desired = np.array((self.maxspeed, self.velocity[1]), dtype=np.float64)
        elif self.position[0] > width - d:
            desired = np.array((-self.maxspeed, self.velocity[1]), dtype=np.float64)

        if self.position[1] < d:
            desired = np.array((self.velocity[0], self.maxspeed), dtype=np.float64)
        elif self.position[1] > height - d:
            desired = np.array((self.velocity[0], -self.maxspeed), dtype=np.float64)

        if desired is not None:
            magnitude = np.linalg.norm(desired)
            if magnitude != 0:
                desired = desired / magnitude
                desired *= self.maxspeed

                steer = desired - self.velocity
                self.apply_force(steer)

    def clone(self):
        if random.randint(1, 250) == 200:
            return Car(self.position[0], self.position[1], self.dna)
        else:
            return None


class Monster(Car):
    def __init__(self, x, y, dna=[]):
        super().__init__(x, y)
        # Monster-specific constants
        self.death_rate = 0.008
        self.mr = 0.1
        self.dna = [0, 0]
        if dna != []:
            self.dna[0] = dna[0] + random.uniform(-self.mr, self.mr)
            self.dna[1] = dna[1] + random.uniform(-10, 10)
        else:
            # Random DNA values
            self.dna[0] = random.uniform(-5, 5)
            self.dna[1] = random.uniform(50, 150)

        self.size = 20
        self.color = (0, 0, 255)  # Blue color for monsters
        self.maxspeed = 5.5
        self.maxforce = 0.85

    def draw(self, window, show=False):
        position_tuple = (int(self.position[0]), int(self.position[1]))

        food_atr = 100 * self.dna[0]

        food_atr_end_point = (self.position[0] + food_atr * math.cos(self.angle_radians),
                              self.position[1] + food_atr * math.sin(self.angle_radians))

        if self.debug:
            pygame.draw.circle(window, (0, 255, 0), position_tuple, int(self.dna[1]), 1)
            pygame.draw.line(window, (0, 200, 0), self.position, food_atr_end_point, 4)
        pygame.draw.circle(window, (255 * (1 - (self.health / 1)), 0, 0), (int(self.position[0]), int(self.position[1])), self.size)

    def behavior(self, cars, bad=None):
        positions = [car.position for car in cars]
        steer = self.eat(positions, 0.09, self.dna[1], cars)

        if steer is not None:  # Check if self.eat returned a valid value
            steer *= self.dna[0]
            self.apply_force(steer)

    def eat(self, cars, diet, perception, car):
        if not cars:  # Check if there are any cars in the environment
            return None
        distances = np.linalg.norm(cars - self.position, axis=1)
        mask_within_perception = distances <= perception

        if np.any(mask_within_perception):
            closest_car = cars[np.argmin(distances)]
            if np.linalg.norm(closest_car - self.position) < self.maxspeed + (self.size // 2):
                car[np.argmin(distances)].calc_health(-0.1)

                self.calc_health(diet)
            return self.seek(closest_car)
        return np.array((0, 0), dtype=np.float64)

    def clone(self):
        if random.randint(1, 370) == 200:
            return Monster(self.position[0], self.position[1], self.dna)
        else:
            return None
