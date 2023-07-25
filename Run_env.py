import pygame
import random
import numpy as np
import matplotlib.pyplot as plt
from target import target as Target
from Vehicle import Car, Monster

# Helper function to draw text on the window
def draw_text(window, font, text, position, color):
    text_surface = font.render(text, True, color)
    window.blit(text_surface, position)

def main():
    # Initialize pygame
    pygame.init()

    # Window settings
    window_width, window_height = 800, 600
    window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Steering behavior")

    clock = pygame.time.Clock()

    cars, food, poison = [], [], []
    debug = False
    font = pygame.font.SysFont(None, 30)

    # Data for graph
    time_data, mon_data, car_data = [], [], []
    attraction_food_values, attraction_poison_values = [], []
    perception_food_values, perception_poison_values = [], []

    # Create monsters and cars
    mon, mon_pos = [], []
    for i in range(10):
        x, y = random.randint(10, window_width - 10), random.randint(10, window_height - 10)
        mon.append(Monster(x, y))
        mon_pos.append(mon[i].position)

    for i in range(100):
        x2, y2 = random.randint(10, window_width - 10), random.randint(10, window_height - 10)
        if i % 2 == 0:
            cars.append(Car(x2, y2))

        x, y = random.randint(10, window_width - 10), random.randint(10, window_height - 10)
        food.append(np.array((x, y), dtype=np.float64))
        # poison.append(np.array((x2, y2), dtype=np.float64))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # 'Space' key
                    debug = not debug

        window.fill((255, 255, 255))

        # Update and draw monsters
        for i in range(len(mon) - 1, -1, -1):
            mon[i].boundaries(window_width, window_height)
            mon[i].update()
            mon[i].behavior(cars)
            mon[i].debug = debug
            mon[i].draw(window)
            new_mon = mon[i].clone()
            if new_mon is not None:
                mon.append(new_mon)
            if mon[i].dead:
                mon.pop(i)

        # Add new food and poison
        if random.randint(1, 1) == 1:
            x, y = random.randint(10, window_width - 10), random.randint(10, window_height - 10)
            food.append(np.array((x, y), dtype=np.float64))

        '''
        if random.randint(1, 200) == 10:
            x, y = random.randint(10, window_width - 10), random.randint(10, window_height - 10)
            poison.append(np.array((x, y), dtype=np.float64))
        '''

        # Draw food and poison
        for item in food:
            x, y = map(int, item)
            pygame.draw.circle(window, (0, 200, 0), (x, y), 4)

        for item in poison:
            x, y = map(int, item)
            pygame.draw.circle(window, (200, 0, 0), (x, y), 4)

        # Update and draw cars
        for i in range(len(cars) - 1, -1, -1):
            dna = cars[i].dna
            attraction_food_values.append(dna[0])
            attraction_poison_values.append(dna[1])
            perception_food_values.append(dna[2])
            perception_poison_values.append(dna[3])

            cars[i].behavior(food, mon_pos)
            cars[i].boundaries(window_width, window_height)
            cars[i].draw(window)
            cars[i].update()
            cars[i].debug = debug

            new_car = cars[i].clone()
            if new_car is not None:
                cars.append(new_car)

            if cars[i].dead:
                food.append(cars[i].position)
                cars.pop(i)

        # Display the counts of cars, food, and monsters
        draw_text(window, font, f"Cars: {len(cars)}", (10, 10), (0, 0, 0))
        draw_text(window, font, f"Food: {len(food)}", (10, 30), (0, 0, 0))
        draw_text(window, font, f"Monsters: {len(mon)}", (10, 50), (0, 0, 0))

        # Record data for the graph
        time_data.append(pygame.time.get_ticks() / 1000)  # Convert to seconds
        mon_data.append(len(mon))
        car_data.append(len(cars))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

    # Calculate and display summary in the console
    print("Summary:")
    print("Average Attraction to Food:", np.mean(attraction_food_values))
    print("Standard Deviation Attraction to Food:", np.std(attraction_food_values))
    print("Average Attraction to Poison:", np.mean(attraction_poison_values))
    print("Standard Deviation Attraction to Poison:", np.std(attraction_poison_values))
    print("Average Perception of Food:", np.mean(perception_food_values))
    print("Standard Deviation Perception of Food:", np.std(perception_food_values))
    print("Average Perception of Poison:", np.mean(perception_poison_values))
    print("Standard Deviation Perception of Poison:", np.std(perception_poison_values))

    # Display the graph
    plt.figure(figsize=(8, 6))
    plt.plot(time_data, mon_data, label="Monsters")
    plt.plot(time_data, car_data, label="Cars")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Count")
    plt.legend()
    plt.title("Number of Monsters and Cars over Time")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
