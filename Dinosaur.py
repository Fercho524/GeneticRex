import numpy as np

import pygame
import random
import time
import os

from Constants import *
from Brain import *
from GA import *

pygame.init()

# GAME PROPERTIES
FONT = pygame.font.SysFont("Press_Start_2P", 10)
SIZE = WIDTH, HEIGHT = (1000, 500)
SCREEN = pygame.display.set_mode(SIZE)

# GAME PERFORMANCE
GAME_FRAMES = 150
FRAME_INTERVAL = 1 / GAME_FRAMES

# GAME SPEED AND HARDNESS
GAME_SPEED = 5
SPEED_GROW = 10
SCORE_INCREASE = 0.1
X_BG = 0

# COLORS
TEXT_COLOR = (20,20,20)
BACKGROUND_COLOR = (255,255,255)
GROUND_COLOR = (253, 203, 110)
CACTUS_COLOR = (22, 160, 133)
COLORS = [
    (246, 229, 141),
    (255, 190, 118),
    (255, 121, 121),
    (186, 220, 88),
    (223, 249, 251),
    (249, 202, 36),
    (240, 147, 43),
    (235, 77, 75),
    (106, 176, 76),
    (199, 236, 238),
    (126, 214, 223),
    (224, 86, 253),
    (104, 109, 224),
    (48, 51, 107),
    (149, 175, 192)
]

# DINO PROPERTIES
GROUND_HEIGHT = 50
NUM_DINOS = 20
LIVE_DINOS = NUM_DINOS
DINO_HEIGHT = 50
DINO_WIDTH = 45
DINO_MIN_X = 40
DINO_MAX_X = 160

# JUMP PROPERTIES
JUMP_DURATION = 150
JUMP_AMPLITUDE = 100

# OBSTACLES OBJECTS
NUM_OBSTACLES = 4
MIN_OBS_WIDTH = 40
MAX_OBS_WIDTH = 120
OBS_HEIGHT = DINO_HEIGHT
MIN_GAP = 400
MAX_GAP = 800
OBSTACLES = []

# ENVIROMENT INFORMATION
LAST_OBSTACLE = WIDTH
OBSTACLES_POSITION = np.array([[0, 0, 0, 0] for k in range(NUM_OBSTACLES)])

# GAME INFORMATION
GLOBAL_SCORE = 0
HIGH_SCORE = 0
RUNNING = True

# GENETIC PROPERTIES
DINO_SELECTED = 3
GENERATION = 1

# SPRITES
RUNNING = [
    pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),(DINO_WIDTH,DINO_HEIGHT)),
    pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png")),(DINO_WIDTH,DINO_HEIGHT))
]

JUMPING = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png")),(DINO_WIDTH,DINO_HEIGHT))

DUCKING = [
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))
]

CACTUS = [
    pygame.transform.scale(pygame.image.load(os.path.join("Assets/Cactus", "1.png")), (MIN_OBS_WIDTH,OBS_HEIGHT)),
    pygame.transform.scale(pygame.image.load(os.path.join("Assets/Cactus", "2.png")), (2*MIN_OBS_WIDTH,OBS_HEIGHT)),
    pygame.transform.scale(pygame.image.load(os.path.join("Assets/Cactus", "3.png")), (3*MIN_OBS_WIDTH,OBS_HEIGHT))
]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


# Quadratic function to update y wth jump time
def jump_function(A, T, t):
    return (-4 * A * t * (t - T)) / (T ** 2)


# Collision Checking between 2 rects
def check_collisions(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


# Draw the ground and baackground
def draw_background(game_screen):
    pygame.draw.rect(
        game_screen, 
        BACKGROUND_COLOR, 
        [0, 0, WIDTH, HEIGHT]
    )


def draw_ground(game_screen):
    global X_BG
    image_width = BG.get_width()
    
    game_screen.blit(BG, (X_BG, HEIGHT - GROUND_HEIGHT -10))
    game_screen.blit(BG, (X_BG+image_width, HEIGHT - GROUND_HEIGHT -10))
    
    if X_BG < -image_width:
        game_screen.blit(BG, (X_BG+image_width, HEIGHT - GROUND_HEIGHT -10))
        X_BG = 0

    X_BG -= GAME_SPEED


# Generate random color
def random_color():
    return COLORS[random.randint(0, len(COLORS))-1]


# The Dino has a brain that gives a behavior
class Dinosaur:

    def __init__(self, id, x, y,brain="random"):
        # Identification
        self.id = id
        self.live = True
        self.score = 0

        # Genetic Properties
        self.genoma = random_genoma(BRAIN_STRUCTURE, N_CONECTIONS)
        self.brain = Brain(self.genoma, BRAIN_STRUCTURE) if brain == "random" else brain
        
        # Position and Size
        self.x = x
        self.y = y
        self.width = DINO_WIDTH
        self.height = DINO_HEIGHT

        # Visual Information
        self.color = random_color()

        # Jump Information
        self.jump = False
        self.jump_time = 0
        self.jump_duration = JUMP_DURATION
        self.jump_amplitude = JUMP_AMPLITUDE

        # Animation
        self.step_index = 0
        self.image = RUNNING[self.step_index // 5]


    def draw(self, game_screen):
        if self.step_index >= 10:
            self.step_index = 0

        if not self.jump:
            self.image = RUNNING[self.step_index // 5]
        else:
            self.image = JUMPING
        
        self.step_index += 1
        game_screen.blit(self.image, (self.x, self.y))

    def update(self,env):
        # The action will be an integer
        action = self.brain.predict(env)

        # Enable Jump
        if action == 1 and self.jump_time == 0:
            self.jump = True

        # Down
        if action == 2:
            self.jump = False
            self.jump_time = 0
            self.y = HEIGHT - self.height - GROUND_HEIGHT

        # Jump Behavior
        if self.jump:
            if self.jump_time < self.jump_duration:
                self.y = (HEIGHT - GROUND_HEIGHT - self.height) - jump_function(self.jump_amplitude, self.jump_duration, self.jump_time)
                self.jump_time += 2
            else:
                self.jump_time = 0
                self.jump_time = False


def draw_dinos(dinos, game_screen):
    for dino in dinos:
        if dino.live:
            dino.draw(game_screen)


# An obstacle is a simple rect, doesnt do nothing :)
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, game_screen):
        if self.width > 40 and self.width < 60:
            self.image = CACTUS[0]
        elif self.width > 60 and self.width < 90:
            self.image = CACTUS[1]
        else:
            self.image = CACTUS[2]

        game_screen.blit(self.image, (self.x, self.y))

    def check_over(self):
        return self.x < 0


class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CLOUD.get_width()
        self.height = CLOUD.get_height()

    def draw(self, game_screen):
        game_screen.blit(CLOUD, (self.x, self.y))

    def update(self):
        self.x -= GAME_SPEED

        if self.x < -self.width:
            self.x = WIDTH + random.randint(1000, 3000)
            self.y = random.randint(50, 300)


# Create a random obstacle positions
def obstacle_bounds():
    return [
        int(LAST_OBSTACLE + MIN_GAP + (MAX_GAP-MIN_GAP)*random.random()),
        int(HEIGHT - GROUND_HEIGHT - DINO_HEIGHT),
        random.randint(MIN_OBS_WIDTH, MAX_OBS_WIDTH),
        OBS_HEIGHT
    ]


# Only draws the obstacles with the OBSTACLES_POSITION information and OBSTACLES array
def draw_obstacles(game_screen):
    global OBSTACLES_POSITION, GAME_SPEED, LAST_OBSTACLE

    for i in range(NUM_OBSTACLES):
        OBSTACLES[i].x = OBSTACLES_POSITION[i][0]
        OBSTACLES[i].draw(game_screen)

        LAST_OBSTACLE -= GAME_SPEED


# Move the obstacles to left with GAME_SPEED
def update_obstacles():
    global OBSTACLES_POSITION
    last = max(OBSTACLES_POSITION[:,0])

    for i in range(NUM_OBSTACLES):
        OBSTACLES_POSITION[i][0] -= GAME_SPEED

        # If the obstacles goes out of screen, the x cord and width will be reseted
        if OBSTACLES_POSITION[i][0] < 0:
            OBSTACLES_POSITION[i][0] += last + int(MIN_GAP + (MAX_GAP-MIN_GAP)*random.random())
            OBSTACLES_POSITION[i][2] = random.randint(MIN_OBS_WIDTH, MAX_OBS_WIDTH)


def handle_events():
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


NUM_CLOUDS = 5
CLOUDS = [ Cloud(random.randint(1000, 3000),random.randint(50, 300)) for k in range(NUM_CLOUDS)]

# DINOSAURS OBJECT ARRAY
DINOS = [Dinosaur(k, random.randint(DINO_MIN_X, DINO_MAX_X), HEIGHT - GROUND_HEIGHT-DINO_HEIGHT) for k in range(NUM_DINOS)]



def init_game():
    global OBSTACLES_POSITION, LAST_OBSTACLE, OBSTACLES, GLOBAL_SCORE, GAME_SPEED, LIVE_DINOS, DINOS

    # RESET SCORE AND DINOS
    LIVE_DINOS = NUM_DINOS
    LAST_OBSTACLE = WIDTH
    GLOBAL_SCORE = 0
    GAME_SPEED = 5

    # RESET OBSTACLES
    for i in range(NUM_OBSTACLES):
        OBSTACLES_POSITION[i] = obstacle_bounds()
        LAST_OBSTACLE = OBSTACLES_POSITION[i][0]

        OBSTACLES.append(
            Obstacle(
                OBSTACLES_POSITION[i][0],
                OBSTACLES_POSITION[i][1],
                OBSTACLES_POSITION[i][2],
                OBSTACLES_POSITION[i][3])
        )

    # RELIVE THE DINOSAURS
    for dino in DINOS:
        dino.live = True


def evolve(scores):
    global GENERATION

    father_ids = scores[:DINO_SELECTED,1]
    
    # Spliting Fathers and Others
    population = []
    fathers = []

    for i in range(NUM_DINOS):
        if i in father_ids:
            fathers.append(DINOS[i].genoma)
        else:
            population.append(DINOS[i].genoma)

    # # Crossing
    reproducted = []
    
    for dino in population:
        reproducted.append(cross(fathers[random.randint(0,DINO_SELECTED-1)],dino))

    # Elitism
    for dino in fathers:
        reproducted.append(dino)
        
    # Mutación aleatoria
    mutated = []

    for dino in reproducted:
        mutated.append(mutate(dino))

    # # Mejora de los dinosaurios
    for i in range(len(mutated)):
        newbrain = Brain(mutated[i],BRAIN_STRUCTURE)
        DINOS[i] = Dinosaur(i, random.randint(DINO_MIN_X, DINO_MAX_X), HEIGHT - GROUND_HEIGHT-DINO_HEIGHT,newbrain) 

    GENERATION += 1


# Checks colisions between dinos and obstacles
def check_dino_colisions():
    global NUM_DINOS,NUM_OBSTACLES,DINOS,OBS_HEIGHT,LIVE_DINOS

    for i in range(NUM_DINOS):
            for j in range(NUM_OBSTACLES):
                if check_collisions(
                    DINOS[i].x,
                    DINOS[i].y,
                    DINOS[i].width,
                    DINOS[i].height,
                    OBSTACLES[j].x,
                    OBSTACLES[j].y,
                    OBSTACLES[j].width,
                    OBSTACLES[j].height,
                ) and DINOS[i].live:
                    DINOS[i].live = False
                    LIVE_DINOS -= 1


def display_game_info():
    img = FONT.render(f'Score : {int(GLOBAL_SCORE)} Alives : {LIVE_DINOS} / {NUM_DINOS}  Generation  {GENERATION} High Score {HIGH_SCORE}', True, TEXT_COLOR)
    SCREEN.blit(img, (20, 20))


def main():
    global GAME_SPEED, GLOBAL_SCORE, LIVE_DINOS,RUNNING,HIGH_SCORE
    
    init_game()
    
    while RUNNING:
        # EVENTS
        handle_events()

        # STAGE
        draw_background(SCREEN)
        draw_ground(SCREEN)

        # OBSTACLES
        draw_obstacles(SCREEN)
        update_obstacles()

        # CLOUDS
        for cloud in CLOUDS:
            cloud.draw(SCREEN)
            cloud.update()
        
        # DINOSAURS
        draw_dinos(DINOS, SCREEN)

        # ENVIROMENT
        nearest_obstacle = OBSTACLES_POSITION[np.argmin(OBSTACLES_POSITION[:,0])]
        
        # We pass the information of obstacles to dinosaurs
        for dino in DINOS:
            distance = nearest_obstacle[0] - dino.x
            owidth = nearest_obstacle[2]
            oheight = nearest_obstacle[3]
            env = [GAME_SPEED,distance,owidth,oheight]

            dino.update(np.array(env))

        # COLISION CHECKING
        check_dino_colisions()

        # WHEN ALL DIES
        if LIVE_DINOS == 0:
            # SCORES TO BE TRAINNED
            scores = [ [int(dino.score), dino.id ] for dino in DINOS]
            scores.sort(reverse=True)
            
            time.sleep(1)
            
            init_game()
            evolve(np.array(scores))

        # SPEED, SCORE UP
        GLOBAL_SCORE += SCORE_INCREASE

        # LIVE DINOS WILL HAVE THE MAX SCORE
        for dino in DINOS:
            if dino.live:
                dino.score = GLOBAL_SCORE

        # WHEN SCORE UP, SPEED UP
        if GLOBAL_SCORE % 10 == 0:
            GAME_SPEED += SPEED_GROW

        if GLOBAL_SCORE > HIGH_SCORE:
            HIGH_SCORE = int(GLOBAL_SCORE)

         # GAME INFORMATION
        display_game_info()

        # UPDATE SCREEN
        time.sleep(FRAME_INTERVAL)
        pygame.display.update()


if __name__ == "__main__":
    main()