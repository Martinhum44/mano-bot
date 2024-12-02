import pygame, math, random, cv2
import mediapipe as mp
from pygame import font
import os

cap = cv2.VideoCapture(0)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(cap_width, cap_height)
SIZE = (600, 400)
SCREEN = pygame.display.set_mode(SIZE)
MPH = mp.solutions.hands
hands = MPH.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.2)
pygame.init()

class Sprite:
    def __init__(self, x_pos: int, y_pos: int, radius: int, color: tuple[int]):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius  = radius
        self.color = color
        self.visible = True

    def isTouching(self, sprite) -> bool: # type: ignore
        if not isinstance(sprite, Sprite):
            raise TypeError("sprite parameter must be an instance of the Sprite class")
        distance = abs(math.sqrt((sprite.y_pos - self.y_pos)**2 + (sprite.x_pos - self.x_pos)**2))
        if distance < 20:
            return True
        return False
    
    def draw(self, screen: pygame.Surface):
        if self.visible:
            pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos), self.radius)
    
    def getPosition(self) -> tuple[int]:
        return (self.x_pos, self.y_pos)
    
    def setInvisible(self):
        self.visible = False
    
    def setVisible(self):
        self.visible = True

class Enemy(Sprite):
    def __init__(self):
        super().__init__(random.randint(0, SIZE[0]), random.randint(0, SIZE[1]), 10, (255,000,000))
        self.speed_X = random.randint(-10, 10)
        self.speed_Y = random.randint(-8, 8)

    def draw(self, screen: pygame.Surface):
        if self.x_pos > 600 or self.x_pos < 0:
            self.speed_X *= -1
        if self.y_pos > 400 or self.y_pos < 0:
            self.speed_Y *= -1
        
        self.x_pos += self.speed_X
        self.y_pos += self.speed_Y
            
        pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos), self.radius)

class Reward(Sprite):
    def __init__(self):
        super().__init__(200, 400, 10, (000,255,000))
        self.speed_X = random.randint(-5, 5)
        self.speed_Y = random.randint(-10, -5)
    
    
    def changePosition(self, image) -> None:
        res = hands.process(image)
        image = cv2.flip(image, 1)
        landmarks = res.multi_hand_landmarks
        if landmarks is None:
            return
        landmarks = landmarks[0].landmark
        self.x_pos = int(SIZE[0]-((landmarks[8].x)*cap_width)*(SIZE[0]/cap_width))
        self.y_pos = int(((landmarks[8].y)*cap_height)*(SIZE[1]/cap_height))

    def draw(self, screen: pygame.Surface):
        if self.visible:
            self.x_pos += self.speed_X
            self.y_pos += self.speed_Y
            
            pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos), self.radius)
    


class Player(Sprite):
    def __init__(self):
        super().__init__(300, 200, 10, (000,000,000))
    
    def willDie(self, sprites: list[Enemy]) -> bool: # type: ignore
        for enemy in sprites:
            if self.isTouching(enemy):
                return True
        return False
    
    
    def changePosition(self, image) -> None:
        res = hands.process(image)
        image = cv2.flip(image, 1)
        landmarks = res.multi_hand_landmarks
        if landmarks is None:
            return
        landmarks = landmarks[0].landmark
        self.x_pos = int(SIZE[0]-((landmarks[8].x)*cap_width)*(SIZE[0]/cap_width))
        self.y_pos = int(((landmarks[8].y)*cap_height)*(SIZE[1]/cap_height))
    
    def getsReward(self, rewards: list[Reward]) -> bool:
        for r in rewards:
            if self.isTouching(r) and r.visible:
                r.setInvisible()
                return True
        return False
    
if not "best_score.txt" in os.listdir():
    with open("best_score.txt", "w") as f:
        f.write("0")
numberOf = 5
running = True
state = True
enemies: list[Enemy] = []
rewards: list[Enemy] = []
PLAYER = Player()
ct = 0
score = 0
inc = True
beat = False
for i in range(numberOf):
    enemies.append(Enemy())
best_score = 0
try: 
    with open("best_score.txt", "r") as f:
        best_score = f.read()
except Exception:
    pass
while running:
    success, image = cap.read()
    for event in pygame.event.get():
        if event.type == "QUIT":
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and state == False:
                state = True
                score = 0
                PLAYER.setVisible()
                ct = 0
                inc = True
                for i in range(numberOf):
                    enemies.append(Enemy())
                beat = False
    SCREEN.fill((255,255,255))

    if ct % 20 == 0:
        enemies.append(Enemy())
    
    if ct % 60 == 0 and ct > 0:
        rewards.append(Reward())

    PLAYER.changePosition(image)
    PLAYER.draw(SCREEN)
    
    for e in enemies:
        e.draw(SCREEN)
    
    for r in rewards:
        r.draw(SCREEN)
    
    if PLAYER.getsReward(rewards):
        score += 100

    if PLAYER.willDie(enemies):
        PLAYER.setInvisible()
        inc = False
        ct = 0.5
        enemies = []
        rewards = []
        state = False
        try:
            with open("best_score.txt", "w") as f:
                print(best_score)
                if int(best_score) < score:
                    print("Lester")
                    f.write(str(score))
                    best_score = score
                    beat = True
                else:
                    f.write(str(best_score))
        except FileNotFoundError:
            print("OH NO")


    if inc:
        score += 1
    
    if not state:
        fonty = font.SysFont(None, 40)
        text_surface = fonty.render(f"YOU LOSE! Press Space to try again.", True, (000,000,000))
        if beat:
            fontyz = font.SysFont(None, 40)
            text_surfacezz = fontyz.render(f"New Best Score!", True, (000,000,000))
            SCREEN.blit(text_surfacezz, (50,250))
        SCREEN.blit(text_surface, (50,200))

    pos = PLAYER.getPosition()
    ct += 1
    fonty = font.SysFont(None, 36)
    text_surface = fonty.render(f"score: {score}", True, (000,000,000))

    fontz = font.SysFont(None, 36)
    text_surface2 = fontz.render(f"best score: {best_score}", True, (000,000,000))
    SCREEN.blit(text_surface, (50,40))
    SCREEN.blit(text_surface2, (200,40))
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)