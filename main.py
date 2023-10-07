import pygame
import sys
import random
import time
from collections import namedtuple

pygame.init()

clock = pygame.time.Clock()
WIDTH, HEIGHT = 1200,800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Floppy cat")
WHITE = (255,255,255)

transparency_background = pygame.Surface((WIDTH,HEIGHT))
transparency_background.set_alpha(150)
transparency_background.fill((255,255,255))

PAUSE_BUTTON_SIZE = 64
BORDER = 10
MIN_HOLE_POSITION = HEIGHT-HEIGHT/2+100 # hauteur minimal du trou

t_const = namedtuple('TUYAUX', ['GAP', 'WIDTH','DISTANCE','COLOR','MIN_HEIGHT','SPEED']) # Dictionnaire de constante pour les tuyaux, accessible via le nom des champs
TUYAUX_CONST = t_const(250, 80, 400, (0, 255, 0), 50, 6) # Ecart entre tuyau du haut et du bas, Largeur d'un tuyau, Distance entre 2 tuyaux
b_const = namedtuple('BIRDS', ['INIT_Y','GRAVITY','SPEED','IMG_NEUTRAL', 'IMG_RISE','IMG_FALL','SIZE']) # Dictionnaire de constante pour les oiseaux, accessible via le nom des champs
BIRDS_CONST = b_const(HEIGHT // 2, 0.5, -9, pygame.image.load("bird.png"), pygame.image.load("bird_rise.png"), pygame.image.load("bird_fall.png"),64) 

bg = pygame.image.load("background.jpg")
pause_button=pygame.image.load("button_pause.png")
bg_list = [[bg,0],[bg,WIDTH-10]]

font = pygame.font.Font('freesansbold.ttf', 64)
loose_text = font.render(" Vous avez perdu ", True, (10,10,10), (240,240,240)) # S'affiche quand tout les joueurs ont perdu
loose_textRect = loose_text.get_rect()
loose_textRect.center = (WIDTH // 2, HEIGHT // 2)
pause_text = font.render(" Pause ", True, (10,10,10), (240,240,240)) # S'affiche quand le jeu est en pause
pause_textRect = pause_text.get_rect()
pause_textRect.center = (WIDTH // 2, HEIGHT // 2)

pause = False

def switchPause(event):
	if event.type == pygame.MOUSEBUTTONDOWN:
		mouse_pos=pygame.mouse.get_pos()
		return WIDTH-BORDER>mouse_pos[0]>WIDTH-PAUSE_BUTTON_SIZE-BORDER and BORDER+PAUSE_BUTTON_SIZE>mouse_pos[1]>BORDER 
		
def fermeture(event):
	if event.type == pygame.QUIT:
		pygame.quit()
		sys.exit()

class Pipe:
    def __init__(self, x):
    	self.top_size = random.randint(TUYAUX_CONST.MIN_HEIGHT, HEIGHT - TUYAUX_CONST.MIN_HEIGHT - TUYAUX_CONST.GAP) # Calcule la hauteur minimum des tuyaux en fonction de la taille de la fenêtre
    	self.top_tuyau = pygame.Rect((x,0),(TUYAUX_CONST.WIDTH,self.top_size))
    	self.bottom_tuyau = pygame.Rect((x,self.top_size + TUYAUX_CONST.GAP),(TUYAUX_CONST.WIDTH,HEIGHT - self.top_size - TUYAUX_CONST.GAP))

    def draw(self): # Dessine la partie haute et basse du tuyau
    	pygame.draw.rect(screen, TUYAUX_CONST.COLOR,self.top_tuyau)
    	pygame.draw.rect(screen, TUYAUX_CONST.COLOR, self.bottom_tuyau)

    def update(self): # Déplace les tuyaux
    	self.top_tuyau.x -= TUYAUX_CONST.SPEED
    	self.bottom_tuyau.x -= TUYAUX_CONST.SPEED

class Bird:
    def __init__(self,x):
        self.x = x
        self.y = BIRDS_CONST.INIT_Y
        self.speed = 0
        self.gravity = BIRDS_CONST.GRAVITY
        self.rect_bird = pygame.Rect((self.x,self.y),((BIRDS_CONST.SIZE,BIRDS_CONST.SIZE))) # Crée un rectangle pour la collision de l'oiseau
        self.bird_current=BIRDS_CONST.IMG_NEUTRAL

    def flap(self):
        self.speed = BIRDS_CONST.SPEED

    def update(self):
        self.speed += BIRDS_CONST.GRAVITY
        self.y += self.speed
        self.rect_bird.y = self.y # Update rect position
        if self.speed < -5:
            self.bird_current=BIRDS_CONST.IMG_RISE
        elif self.speed > 5 :
            self.bird_current=BIRDS_CONST.IMG_FALL
        else :
            self.bird_current=BIRDS_CONST.IMG_NEUTRAL

    def draw(self):
        screen.blit(self.bird_current,(self.x, int(self.y)))

birds = [Bird(100),Bird(200)]
birds_event = [pygame.K_SPACE,pygame.K_p]
pipes = [Pipe(TUYAUX_CONST.DISTANCE*i+WIDTH) for i in range(4)] # Les premiers tuyaux arrivent de l'extérieur de la fenêtre

perdu = False

while True:
	if pause :
		screen.blit(pause_button,(WIDTH-PAUSE_BUTTON_SIZE - BORDER,BORDER))
		screen.blit(pause_text, pause_textRect)
		pygame.display.update()
		for event in pygame.event.get():
			if switchPause(event):
				pause = not pause
			fermeture(event)
		continue
	elif perdu :
		for event in pygame.event.get():
			fermeture(event)
		continue
		
	for event in pygame.event.get():
		if switchPause(event):
			pause = not pause
	
        #gestion fermeture fenetre
		fermeture(event)
		if event.type == pygame.KEYDOWN:
			for i in range(len(birds_event)):
				if event.key == birds_event[i]:
					birds[i].flap()

	screen.fill(WHITE)
	for i in range(len(bg_list)): # Le background se déplace vers la gauche
		bg_list[i][1] -= 4
		screen.blit(bg_list[i][0],(bg_list[i][1],0))
	if bg_list[0][1] <= -WIDTH:
		bg_list.reverse()
		bg_list[1][1] = bg_list[0][1]+WIDTH
		
	# Dessiner les tuyaux
	for pipe in pipes:
		pipe.update()
		pipe.draw()
	
	# Retirer les tuyaux et en ajouter de nouveaux
	if pipes[0].top_tuyau.x < -TUYAUX_CONST.WIDTH:
		pipes.pop(0)
		
	if pipes[len(pipes)-1].top_tuyau.x <= WIDTH-TUYAUX_CONST.DISTANCE :
		pipes.append(Pipe(WIDTH))
	
	# Dessiner les oiseaux
	for i in range(len(birds)):
		birds[i].update()
		pygame.draw.rect(screen, (240,20,20), birds[i].rect_bird)
		birds[i].draw()
		for pipe in pipes :
			if pygame.Rect.colliderect(birds[i].rect_bird,pipe.top_tuyau) or pygame.Rect.colliderect(birds[i].rect_bird,pipe.bottom_tuyau) :
				perdu = True
				screen.blit(transparency_background, (0,0))
				screen.blit(loose_text, loose_textRect)
	
	screen.blit(pause_button,(WIDTH-PAUSE_BUTTON_SIZE - BORDER,BORDER))
	pygame.display.update()
	clock.tick(60)
