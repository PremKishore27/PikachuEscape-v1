import pygame
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils import seeding
import time

# Initialize Pygame
pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Set display mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define constants for the grid size
GRID_SIZE = 7
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define positions for the "hell" states and the "goal" state
HELL_STATES = [(2, 1), (1, 4), (4, 3), (5,5)]
GOAL_STATE = (6, 6)

# Initialize score
score = 0

class Player(pygame.sprite.Sprite):
    """Player class representing the agent in the game."""
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, dx, dy):
        """Update the player position based on the change in x and y."""
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        if 0 <= new_x <= SCREEN_WIDTH - CELL_SIZE and 0 <= new_y <= SCREEN_HEIGHT - CELL_SIZE:
            self.rect.x = new_x
            self.rect.y = new_y

def draw_grid(screen):
    """Draw the grid lines on the screen."""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))

def display_score(screen, score):
    """Display the current score on the screen."""
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

class PikachuEscape(gym.Env):
    """Gym environment for the Pikachu Escape game."""
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Discrete(GRID_SIZE * GRID_SIZE)
        self.seed()
        self.viewer = None
        self.state = None
        self.player = Player()
        self.goal_reached = False
        self.hell_entered = False

    def seed(self, seed=None):
        """Set the seed for the environment's random number generator."""
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        """Take a step in the environment based on the action."""
        global score
        
        if action == 0:
            self.player.update(0, -CELL_SIZE)
        elif action == 1:
            self.player.update(0, CELL_SIZE)
        elif action == 2:
            self.player.update(-CELL_SIZE, 0)
        elif action == 3:
            self.player.update(CELL_SIZE, 0)

        self.state = (self.player.rect.x // CELL_SIZE, self.player.rect.y // CELL_SIZE)

        living_reward = -0.2

        if self.state in HELL_STATES:
            reward = -2
            score += reward
            print("Team rocket captured Pikachu")
            self.hell_entered = True
            self.render()
            time.sleep(1.5)  # Display the player captured image for 1.5 seconds
            self.hell_entered = False
            self.state = (0, 0)
            self.player.rect.x = 0
            self.player.rect.y = 0
        elif self.state == GOAL_STATE:
            reward = 10
            score += reward
            print("Pikachu is safe! You win 10 points")
            self.goal_reached = True
        else:
            reward = living_reward
            score += reward

        done = self.state == GOAL_STATE or self.state in HELL_STATES

        if done:
            print(f"Final Score: {score}")

        return self.state, reward, done, {}

    def reset(self):
        """Reset the environment to the initial state."""
        self.state = (0, 0)
        self.player.rect.x = 0
        self.player.rect.y = 0
        global score
        score = 0
        self.goal_reached = False
        self.hell_entered = False
        return self.state

    def render(self, mode='human', close=False):
        """Render the environment."""
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        if self.viewer is None:
            self.viewer = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Pokemon Grid")

        background_image = pygame.image.load("background.png").convert()
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.viewer.blit(background_image, (0, 0))

        draw_grid(self.viewer)

        for i, hell_state in enumerate(HELL_STATES):
            hell_image = pygame.image.load(f"hell{i+1}.png").convert_alpha()
            hell_image = pygame.transform.scale(hell_image, (CELL_SIZE, CELL_SIZE))
            self.viewer.blit(hell_image, (hell_state[0] * CELL_SIZE, hell_state[1] * CELL_SIZE))

        goal_image = pygame.image.load("goal.png").convert_alpha()
        goal_image = pygame.transform.scale(goal_image, (CELL_SIZE, CELL_SIZE))
        self.viewer.blit(goal_image, (GOAL_STATE[0] * CELL_SIZE, GOAL_STATE[1] * CELL_SIZE))

        self.viewer.blit(self.player.image, self.player.rect)

        display_score(self.viewer, score)

        if self.goal_reached:
            goal_reached_image = pygame.image.load("goal_reached.png").convert_alpha()
            goal_reached_rect = goal_reached_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.viewer.blit(goal_reached_image, goal_reached_rect)
            pygame.display.flip()
            time.sleep(2)  # Display the goal reached image for 2 seconds

        if self.hell_entered:
            player_captured_image = pygame.image.load("player_captured.jpeg").convert_alpha()
            player_captured_rect = player_captured_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.viewer.blit(player_captured_image, player_captured_rect)
        
        pygame.display.flip()

        return self.viewer

    def close(self):
        """Close the Pygame environment."""
        pygame.quit()

if __name__ == "__main__":
    env = PikachuEscape()
    env.reset()
    done = False
    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action = 0
                elif event.key == pygame.K_DOWN:
                    action = 1
                elif event.key == pygame.K_LEFT:
                    action = 2
                elif event.key == pygame.K_RIGHT:
                    action = 3
                else:
                    action = None
                
                if action is not None:
                    state, reward, done, _ = env.step(action)
                    print(f"State: {state}, Reward: {reward}, Done: {done}")
        
        env.render()
        clock.tick(10)
    env.close()
