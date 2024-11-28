import pygame, math, random, cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
SIZE = (600, 400)
SCREEN = pygame.display.set_mode(SIZE)
MPH = mp.solutions.hands
hands = MPH.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.2)

class Sprite:
    def __init__(self, x_pos: int, y_pos: int, radius: int, color: tuple[int]):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius  = radius
        self.color = color
        self.visible = True

    def isTouching(self, sprite) -> bool: # type: ignore
        if type(sprite) != Sprite:
            raise TypeError("sprite parameter must be an instance of the Sprite class")
        distance = abs(math.sqrt((sprite.y_pos - self.y_pos)**2 + (sprite.x_pos - self.x_pos)**2))
        if distance < 5:
            return True
        return False
    
    def draw(self, screen: pygame.Surface):
        if self.visible:
            pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos), self.radius)
    
    def getPosition(self) -> tuple[int]:
        return (self.x_pos, self.y_pos)
    
    def setVisible(self):
        self.visible = False
    
    def setVisible(self):
        self.visible = True

class Enemy(Sprite):
    def __init__(self):
        super().__init__(0, 0, 10, (255,000,000))
        self.speed_X = random.randint(-3, 3)
        self.speed_Y = random.randint(-2, 2)

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (self.x_pos + self.speed_X, self.y_pos + self.speed_Y), self.radius)

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
        print(image)
        if landmarks is None:
            self.x_pos = 0
            self.y_pos = 0
            return
        landmarks = landmarks[0].landmark
        self.x_pos = int(SIZE[0]-((landmarks[8].x)*cap_width)*(SIZE[0]/cap_width))
        self.y_pos = int(((landmarks[8].y)*cap_height)*(SIZE[1]/cap_height))
        print(self.x_pos, self.y_pos)
    
running = True
while running:
    success, image = cap.read()
    for event in pygame.event.get():
        if event.type == "QUIT":
            running = False
    SCREEN.fill((255,255,255))

    PLAYER = Player()
    PLAYER.changePosition(image)
    PLAYER.draw(SCREEN)
    enemies: list[Enemy] = []
    pos = PLAYER.getPosition()
    cv2.putText(image, f"({pos[0]},{pos[1]})", (40,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (000,000,000), 1)
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)