
  
import pygame
 


while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEMOTION:
        x, y = event.pos

    screen.fill(bgcolor)
    pygame.draw.circle(screen, linecolor, (x, y), 10)
    pygame.draw.line(screen, linecolor, (0, y), (639, y))
    pygame.display.flip()

class LightSaber:
	bgcolor = 0, 0, 0
	linecolor = 255, 255, 255
	x = y = 0
	running = 1
	screen = pygame.display.set_mode((640, 400))
	
	def animate(self,(x1,y1,z1),(ax,xy,xz)):
	    event = pygame.event.poll()
	    

	    screen.fill(bgcolor)
	    pygame.draw.circle(screen, linecolor, (x1, y1), 10)
	    pygame.draw.circle(screen, linecolor, (x1+ax,y1+ay,z1+az))
	    pygame.display.flip()
