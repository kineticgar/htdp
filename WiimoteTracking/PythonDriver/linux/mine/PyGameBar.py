import pygame
 


class Dots:
	def __init__(self):
		self.bgcolor = 255, 255, 255
		self.linecolor = 0, 0, 0
		self.screen = pygame.display.set_mode((1000, 800))
		pygame.draw.circle(self.screen, self.linecolor, (10,10), 30)
		self.screen.fill(self.bgcolor)
		
		self.x1,self.y1,self.x2,self.y2,self.z,self.az,=0,0,0,0,0,0
	
	def refresh(self,(x,y,z),(ax,ay,az)):
	    x1,y1=1000-x,800-y

	    self.draw(	(self.x1,self.y1),5,
	    			(self.x2,self.y2),5,	self.bgcolor)	
	    
	    self.x1,self.y1 = x1, y1
	    self.x2,self.y2 = x1+ax,y1-ay
	    self.z,self.az = z,az

	    self.draw((x1, y1), 5,(x1+ax,y1-ay),5,self.linecolor)
	    pygame.display.flip()
	 
	 
	def draw(self,(x1,y1),r1,(x2,y2),r2,colour):
		pygame.draw.circle(self.screen,colour,(x1,y1),r1)	
		pygame.draw.circle(self.screen,colour,(x2,y2),r2)
