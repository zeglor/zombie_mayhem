import os, pygame
import math
import numpy as np

if not pygame.font: print('Warning, fonts disabled!')
if not pygame.mixer: print('Warning, sound disabled!')

def rotate_round_point(vertices, point, angle, angleInRadians=False):
	if not angleInRadians: angle = math.radians(angle)
	rotMatrix = np.array([[math.cos(angle), -math.sin(angle)],
		[math.sin(angle), math.cos(angle)]])
	
	vertices = vertices - point
	vertices = np.dot(vertices, rotMatrix) + point
	return vertices

def get_drawing_point_after_rotation(vertices, point, angle, angleInRadians=False):
	vertices = rotate_round_point(vertices, point, angle, angleInRadians)
	return np.amin(vertices, axis=0)

class Bullet():
	def __init__(self, start_pos, speed, angle):
		self.pos = [float(pos_item) for pos_item in start_pos] #keeping pos int enables funny bug
		self.speed = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))]) * speed
		self.collRect = pygame.Rect(start_pos-[1,1], [3,3])
	
	def update(self):
		self.pos += self.speed
		self.collRect = pygame.Rect(self.pos - [1,1], [3,3])

class Player():
	def __init__(self, start_pos=np.array([0,0]),rotate_center_offset=np.array([0,0]), speed=0, image_path=""):
		self.pos = start_pos
		self.rotate_center_offset = rotate_center_offset
		self.speed = speed
		self.image = pygame.image.load(image_path)
		self.img_vertices_relative = np.array([
			[0,0],
			[0,self.image.get_size()[1]],
			self.image.get_size(),
			[self.image.get_size()[0], 0]
		])
		self.__image = self.image
		self.WEAPON_COOLDOWN = 150
		self.weapon_cooldown = self.WEAPON_COOLDOWN
		self.shooting = False
		self.shooting_start_time = 0
	
	def rotate(self, toPos):
		dist = [b - a for a,b in zip(self.pos, toPos)]
		try:
			self.angle = math.degrees(math.atan2(float(dist[1]), float(dist[0]))) % 360
			self.image = pygame.transform.rotate(self.__image, -self.angle)
			self.drawing_point = get_drawing_point_after_rotation(
				self.img_vertices_relative,
				self.rotate_center_offset,
				360 - self.angle
			) + self.pos - self.rotate_center_offset
		except ZeroDivisionError as e:
			pass
	
	def move(self, speed):
		self.pos += np.array(speed) * self.speed
	
	def shootStart(self, bullets):
		#bullets.append(Bullet(self.pos+[0,0], 7, self.angle+0))
		self.shooting = True
		self.shooting_start_time = pygame.time.get_ticks()
	
	def shootStop(self, bullets):
		self.shooting = False
		self.weapon_cooldown = self.WEAPON_COOLDOWN
	
	def update(self, bullets):
		if self.shooting:
			time = pygame.time.get_ticks()
			self.weapon_cooldown -= time - self.shooting_start_time
			if self.weapon_cooldown < 0:
				bullets.append(Bullet(self.pos+[0,0], 15, self.angle+0))
				self.weapon_cooldown = self.WEAPON_COOLDOWN
				self.shooting_start_time = time

def main():
	pygame.init()
	screen = pygame.display.set_mode((640, 480,))
	bg_color = 255, 255, 255
	
	player = Player(np.array([100, 100]), np.array([6, 9]), 5, "character.png")
	speed = np.array([0,0])
	
	clock = pygame.time.Clock()
	bullets = []
	mapRect = pygame.Rect([0,0], [600, 400])
	
	while 1:
		
		clock.tick(60)
		mouse_x, mouse_y = pygame.mouse.get_pos() 
		#print(clock.get_fps())
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			if event.type == pygame.KEYDOWN:
				if event.unicode == 'w':
					speed[1] = -1
				if event.unicode == 's':
					speed[1] = 1
				if event.unicode == 'd':
					speed[0] = 1
				if event.unicode == 'a':
					speed[0] = -1
			if event.type == pygame.KEYUP:
				if event.key in (119, 115):
					speed[1] = 0
				if event.key in (100, 97):
					speed[0] = 0
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					player.shootStop(bullets)
			if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1:
				player.shootStart(bullets)
		
		player.rotate((mouse_x, mouse_y))
		player.move(speed)
		
		for bullet in bullets:
			bullet.update()
		player.update(bullets)
		bullets[:] = [bullet for bullet in bullets if mapRect.contains(bullet.collRect)]
					
		screen.fill(bg_color)
		pygame.draw.circle(screen, (0,0,255,), player.pos, 2)
		pygame.draw.line(screen, (255,0,0,), player.pos, (mouse_x, mouse_y))
		for bullet in bullets[:]:
			pygame.draw.rect(screen, (255,0,0,), bullet.collRect, 5)
		screen.blit(player.image, player.drawing_point)
		pygame.display.flip()

if __name__ == '__main__': main()
