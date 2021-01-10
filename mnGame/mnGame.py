#import sys
import pygame
from numpy import random as nprandom
import time
from pygame.locals import *
import spritesheet
#from sprite_strip_anim import SpriteStripAnim


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.surf=pygame.Surface((32, 32))
		#self.surf.fill((250,127,250))
		#self.image=tiles
		self.rect=self.surf.get_rect()
		self.health=100
		self.xpos=STARTX
		self.ypos=STARTY
		self.xvel=6
		self.yvel=6
		self.isHit=0
		self.points=0
		self.umbrellas=5+1
		self.isArmed=0
	def reset(self):
		self.health=100
		self.isHit=0
		self.points=0
		self.xpos=STARTX
		self.ypos=STARTY
		self.umbrellas=5+1
		self.isArmed=0
		
class Drop(pygame.sprite.Sprite):
	def __init__(self, screen, xpos=0, type=0, ypos=0):
		super().__init__()
		self.surf=pygame.Surface((16,16))
		self.rect=self.surf.get_rect()
		self.type=type	#0 for straight, 1 for wavy, 2 for random wavy
		self.xpos=xpos
		self.initxpos=xpos
		self.xvel=0
		if self.type>0:
			self.initxpos+=5 #x''=-x_0 has nontrivial solution for x'_0!=0 or x_0!=0
		self.ypos=ypos
		self.yvel=0
		nprandom.seed(int(time.time()+player1.xpos+player1.ypos))
		self.g=0.4+0.7*nprandom.uniform() #random accelerations
		self.spriteno=1
		#sfxRain.play() NOOOOOO
		self.dmg=5
	def move(self):
		self.yvel+=self.g
		self.ypos+=self.yvel
		if self.type>0:
			if self.type==1:
				self.xvel-=(self.xpos-self.initxpos)
			elif self.type==2:
				nprandom.seed(int(123*time.time()%7+player1.xpos%WIDTH+player1.ypos%HEIGHT))
				self.xvel-=0.6*nprandom.uniform()*(self.xpos-self.initxpos) #random wiggliness
			self.xpos+=self.xvel
		if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
			self.spriteno+=1
			self.spriteno%=len(enem_ss)
	def render(self):
		screen.blit(enem_ss[self.spriteno],(self.xpos, self.ypos))
		#print(self.type)

class Scatter(pygame.sprite.Sprite):
	def __init__(self, screen, xpos, ypos):
		super().__init__()
		self.surf=pygame.Surface((16,16))
		self.rect=self.surf.get_rect()
		self.xpos=xpos
		self.ypos=ypos
		self.spriteno=-1
		self.isDead=0
		sfxSplish2.play()
	def move(self):
		pass
	def render(self):
		if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
			self.spriteno+=1
		try:
			screen.blit(scatter_ss[self.spriteno],(self.xpos, self.ypos))
		except IndexError:
			self.isDead=1
		
class extraUmbrella(pygame.sprite.Sprite):
	def __init__(self, screen, type=0):
		super().__init__()
		self.surf=pygame.Surface((16,16))
		self.rect=self.surf.get_rect()
		self.type=type	#0 for straight, 1 for wavy
		self.xpos=newDropX()
		self.initxpos=self.xpos
		self.xvel=0
		if self.type>0:
			self.initxpos+=50 #x''=-x_0 has nontrivial solution for x'_0!=0 or x_0!=0
		self.ypos=0
		self.yvel=0
		nprandom.seed(int(time.time()+player1.xpos+player1.ypos))
		self.g=0.1
		self.spriteno=1
	def move(self):
		self.yvel+=self.g
		self.ypos+=self.yvel
		if self.type==1:
			self.xvel-=0.07*(self.xpos-self.initxpos)
			self.xpos+=self.xvel
		if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
			self.spriteno+=1
			if self.type==0:
				self.spriteno%=len(item_ss0)
			elif self.type==1:
				self.spriteno%=len(item_ss1)
	def render(self):
		if self.type==0:
			screen.blit(item_ss0[self.spriteno],(self.xpos, self.ypos))
		elif self.type==1:
			screen.blit(item_ss1[self.spriteno],(self.xpos, self.ypos))
		

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT=640, 480
FPS=30 #game fps
SFPS=10 #sprite fps
initdropFPS=16
dropFPS=16 #which-th frame a new drop appears
MAXDROPS=256 #max drops on screen
STARTX=300
STARTY=320
HITSTUN=2
ARMSTIME=4
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Makito\'s Nightmare')
fpsClock=pygame.time.Clock()
gameOn=True
isPlaying='none'
titlechoice=0
init_time=0
isFadingIn='none'
isFadingOut='none'

player1=Player()

def newDropX():
	nprandom.seed(int(round(123*time.time())%7+player1.xpos%WIDTH+player1.ypos%HEIGHT)) #some more randomness
	return int(WIDTH*nprandom.uniform())
def coin():
	nprandom.seed(int(time.time()+player1.xpos+player1.ypos))	
	if nprandom.uniform()<0.4:
		return 1
	elif nprandom.uniform()>0.6:
		return 2
	else:
		return 0
drops=[]
extraUmbrellas=[]
titlechooser=[]
sil_time=0


pygame.font.init()
myfont=pygame.font.SysFont('Courier New', 16)
def hud(text, num):
	return myfont.render('{0}: {1}'.format(text, int(num)), False, (0,0,0))

	
def fadein(state, img):
	if isFadingIn==state:
		if img.get_alpha()<254:
			img.set_alpha(img.get_alpha()+15)
		else:
			isFadingIn=='none'
			
def fadeout(state, img):
	if isFadingOut==state:
		if img.get_alpha()>1:
			img.set_alpha(img.get_alpha()-15)
			screen.blit(img,(0,0))
			#time.sleep(1/FPS)
		else:
			isFadingOut=='none'
	else:
		img.set_alpha(255)
			

#def transition(bool1, img1, bool2, img2):
	#i
	
#splashBool=True
#gameBool=False
#gameOverBool=False
gameState='splash'

# def H(x,px):
	# return px**2 + (0.01)*(x-300)**2
# def dHdpx(x,px):
	# return 2*px
# def dHdx(x,px):
	# return (0.02)*(x-300)

#player_x,player_y=300,200
#player_vx=player_vy=2


#noneSprite=image.load('0.png')

#musTitle=pygame.mixer.music.load('res/titletheme.ogg')

sfxGameStart=pygame.mixer.Sound('res/gamestart.wav')
sfxGameStart2=pygame.mixer.Sound('res/gamestart2.wav')
sfxHelp=pygame.mixer.Sound('res/help.wav')
sfxBack=pygame.mixer.Sound('res/back.wav')
sfxArms=pygame.mixer.Sound('res/weapon.wav')
sfxRain=pygame.mixer.Sound('res/rain.wav')
sfxSplish=pygame.mixer.Sound('res/splish.wav')
sfxSplish2=pygame.mixer.Sound('res/splish2.wav')
sfxHurt=pygame.mixer.Sound('res/hurt.wav')
sfxDead=pygame.mixer.Sound('res/dead.wav')

gameIcon=pygame.image.load('res/mnicon.png')
pygame.display.set_icon(gameIcon)

ss1=spritesheet.spritesheet('res/myChar.png')
ss2=spritesheet.spritesheet('res/enem.png')
ss3=spritesheet.spritesheet('res/item.png')
splash=pygame.image.load('res/splash.png').convert()
splash.set_alpha(255)
helpbg=pygame.image.load('res/helpbg.png').convert()
pausebg=pygame.image.load('res/pausebg.png')
dedsplash=pygame.image.load('res/dedsplash.png')
bg1=pygame.image.load('res/bg1.png')

player_ss=[]
player_ss_width=3
player_ss = ss1.images_at(((0, 0, 42, 46), (42,0,42,46), (84,0,42,46),    (0,46,42,46), (42,46,42,46), (84,46,42,46)), colorkey=(255,174,201))
player_ssA = ss1.images_at(((0+126, 0, 42, 55), (42+126,0,42,55), (84+126,0,42,55),    (0+126,55,42,55), (42+126,55,42,55), (84+126,55,42,55)), colorkey=(255,174,201))
playerspriteno=0
pfbsno=0
j=0
enem_ss=[]
enem_ss=ss2.images_at(((0,0,16,16),(16,0,16,16)),colorkey=(0,0,0))
timeWhenHit=0
timeWhenArmed=0
scatter_ss=[]
scatter_ss=ss2.images_at(((0,16,16,16),(16,16,16,16),(32,16,16,16)),colorkey=(0,0,0))
item_ss=[]
item_ss0=ss3.images_at(((0,32,32,32),(32,32,32,32)),colorkey=(255,255,255))
item_ss1=ss3.images_at(((0,0,32,32),(32,0,32,32),(64,0,32,32),(96,0,32,32)),colorkey=(255,255,255))

states=['splash','help','game','paused','gameOver']
imgs=[splash,helpbg,bg1,pausebg,dedsplash]
while gameOn:
	#dx=dHdpx(x,px)
	#dpx=-1*dHdx(x,px)
	#x+=dx
	#px+=dpx
	screen.fill((133,159,192))
	
	if gameState=='splash' or gameState=='help':
		if isPlaying!='titletheme':
			if (time.time()-sil_time)>0.9:
				pygame.mixer.music.load('res/titletheme.ogg')
				isPlaying='titletheme'
				pygame.mixer.music.play(-1)
	if gameState=='game' or gameState=='paused':
		if isPlaying!='gametheme1':
			if (time.time()-sil_time)>1.3:
				pygame.mixer.music.load('res/gametheme1.ogg')
				isPlaying='gametheme1'
				pygame.mixer.music.play(-1)
		
	if gameState=='splash':
		for thing in states:
			if thing!='splash':
				fadeout(thing, imgs[states.index(thing)])
		fadein('splash',splash)
		screen.blit(splash, (0, 0))
		titlechooser.append(Drop(screen, 269, 0, 274))
		if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
			titlechooser[0].spriteno=1-titlechooser[0].spriteno
		titlechooser[0].ypos=274+titlechoice*37
		titlechooser[0].render()
		
	elif gameState=='help':
		for thing in states:
			if thing!='help':
				fadeout(thing, imgs[states.index(thing)])
		fadein('help', helpbg)
		screen.blit(helpbg, (0,0))
		
	elif gameState=='game':
		for thing in states:
			if thing!='game':
				fadeout(thing, imgs[states.index(thing)])
		fadein('game',bg1)
		
		if player1.health<=0:
			sfxDead.play()
			isFadingOut='game'
			gameState='gameOver'
			isFadingIn='gameOver'
			dedsplash.set_alpha(0)
			pygame.mixer.music.fadeout(500)
			sil_time=time.time()
			
		screen.blit(bg1, (0,0))
		screen.blit(hud('Health', player1.health), (0,0))
		if (int(pygame.time.get_ticks()-init_time)*FPS/10)%SFPS==0:
			player1.points+=1
		screen.blit(hud('Points', player1.points),(0,16))
		screen.blit(hud('Umbrellas', player1.umbrellas),(0,32))
		
		if time.time()-timeWhenHit>HITSTUN:
			player1.isHit=0
			
		if player1.isHit==0:
			if player1.isArmed==0:
				screen.blit(player_ss[playerspriteno],(player1.xpos%WIDTH, player1.ypos%HEIGHT))
			elif player1.isArmed==1:
				if time.time()-timeWhenArmed>0.7*ARMSTIME and int(pygame.time.get_ticks()*FPS/1000)%int(FPS/(1*SFPS/2))==0:
					screen.blit(player_ss[playerspriteno],(player1.xpos%WIDTH, player1.ypos%HEIGHT))
				else:
					screen.blit(player_ssA[playerspriteno],(player1.xpos%WIDTH, -9+player1.ypos%HEIGHT)) #-9 is because armed sprite is taller, so need to blit it a bit lower
		else:
			if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/(3*SFPS/4))==0:
				if player1.isArmed==0:
					screen.blit(player_ss[playerspriteno],(player1.xpos%WIDTH, player1.ypos%HEIGHT))
				elif player1.isArmed==1:
					screen.blit(player_ssA[playerspriteno],(player1.xpos%WIDTH, -9+player1.ypos%HEIGHT))
		
		if time.time()-timeWhenArmed>ARMSTIME:
			player1.isArmed=0
		
		dropFPS-=(2**(-9))*dropFPS #exponentially faster-appearing drops
		try:
			if int(pygame.time.get_ticks()*FPS/1000)%int(dropFPS)==0:
				#print(len(drops))
				if len(drops)<=MAXDROPS:
					pass
					drops.append(Drop(screen, newDropX(), coin()))
					drops.append(Drop(screen, player1.xpos, coin())) #to force you to move around! :p
				else:
					for drop in drops:
						if drop.ypos>HEIGHT:
							j=drops.index(drop) # replacing those drops that fall offscreen
					drops[j]=Drop(screen, newDropX(), coin())
					
					if j<MAXDROPS-1 and int(pygame.time.get_ticks()*FPS/1000)%int(dropFPS*5)==0:
						drops[j+1]=Drop(screen, player1.xpos, coin())
		
		except ZeroDivisionError:
			dropFPS=initdropFPS
		
		if nprandom.uniform()<2**-7:
			extraUmbrellas.append(extraUmbrella(screen, int(nprandom.uniform()<0.5)))
		if extraUmbrellas!=[]:
			extraUmbrellas[0].move()
			extraUmbrellas[0].render()
			if extraUmbrellas[0].ypos>HEIGHT:
				extraUmbrellas=[]
		
		
		keys=pygame.key.get_pressed()
		if keys[K_x]:
			isFadingOut='game'
			gameState='paused'
			isFadingIn='paused'
			pausebg.set_alpha(0)
			sfxBack.play()
		if keys[K_RIGHT]:
			player1.xpos+=player1.xvel
			player1.xpos=player1.xpos%WIDTH
			if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
				pfbsno=0
				playerspriteno+=1
				playerspriteno%=player_ss_width
		if keys[K_UP]:
			player1.ypos-=player1.yvel
			player1.ypos=player1.ypos%HEIGHT
		if keys[K_LEFT]:
			player1.xpos-=player1.xvel
			player1.xpos=player1.xpos%WIDTH
			if int(pygame.time.get_ticks()*FPS/1000)%int(FPS/SFPS)==0:
				pfbsno=player_ss_width
				playerspriteno+=1
				playerspriteno%=player_ss_width
				playerspriteno+=player_ss_width
		if keys[K_DOWN]:
			player1.ypos+=player1.yvel
			player1.ypos=player1.ypos%HEIGHT
		if not keys[K_UP] and not keys[K_DOWN] and not keys[K_LEFT] and not keys[K_RIGHT]:
			playerspriteno=pfbsno
		
		for drop in drops:
			if (player1.surf.get_rect(topleft=(player1.xpos%WIDTH,player1.ypos%HEIGHT)).inflate(-10,-10)).colliderect(drop.surf.get_rect(topleft=(drop.xpos,drop.ypos))) and type(drop)==Drop: #a slightly smaller player hitbox
				if player1.isHit==0 and player1.isArmed==0:
					player1.health-=drop.dmg
					player1.isHit=1
					sfxHurt.play()
					timeWhenHit=time.time()
					#print('die!')
				if player1.isArmed==1:
					drops[drops.index(drop)]=Scatter(screen, drop.xpos, -11+drop.ypos) #offset on y to make it splash on tall umbrella
					
		for eu in extraUmbrellas:
			if (player1.surf.get_rect(topleft=(player1.xpos%WIDTH,player1.ypos%HEIGHT)).inflate(-8,-8)).colliderect(eu.surf.get_rect(topleft=(eu.xpos,eu.ypos))):
				player1.umbrellas+=1
				extraUmbrellas=[]
		
		for drop in drops:
			drop.move()
			drop.render()
		
	elif gameState=='gameOver':
		if isPlaying!='dedtheme':
			if (time.time()-sil_time)>1.3:
				pygame.mixer.music.load('res/dedtheme.ogg')
				isPlaying='dedtheme'
				pygame.mixer.music.play()
		for thing in states:
			if thing!='gameOver':
				fadeout(thing, imgs[states.index(thing)])
		fadein('gameOver',dedsplash)
		screen.blit(dedsplash, (0, 0))
	
	elif gameState=='paused':
		for thing in states:
			if thing!='paused':
				fadeout(thing, imgs[states.index(thing)])
		fadein('paused',pausebg)
		screen.blit(pausebg, (0,0))
	
	
	
	for event in pygame.event.get():
	
		if event.type==KEYDOWN:
			if gameState=='splash':
				if event.key==K_UP or event.key==K_DOWN:
					sfxBack.play()
					titlechoice=1-titlechoice
				if event.key==K_z:
					if titlechoice==0:
						sfxGameStart2.play()
						#time.sleep(0.4)
						#sfxGameStart.stop()
						init_time=pygame.time.get_ticks()
						titlechooser=[]
						isFadingOut='splash'
						gameState='game'
						isFadingIn='game'
						bg1.set_alpha(0)
						pygame.mixer.music.fadeout(500)
						sil_time=time.time()
					elif titlechoice==1:
						sfxHelp.play()
						#time.sleep(0.4)
						#sfxHelp.stop()
						titlechooser=[]
						isFadingOut='splash'
						gameState='help'
						isFadingIn='help'
						helpbg.set_alpha(0)
			
			if gameState=='help':
				if event.key==K_x:
					sfxBack.play()
					isFadingOut='help'
					gameState='splash'
					isFadingIn='splash'
			
			if gameState=='game':
				if event.key==K_z:
					if player1.umbrellas>0:
						player1.umbrellas-=1
						sfxArms.play()
						player1.isArmed=1
					timeWhenArmed=time.time()
			
			if gameState=='paused':
				if event.key==K_c:
					sfxBack.play()
					init_time=pygame.time.get_ticks()
					isFadingOut='paused'
					gameState='game'
					isFadingIn='game'
					bg1.set_alpha(0)
				elif event.key==K_r:
					sfxBack.play()
					player1.reset()
					drops=[]
					dropFPS=initdropFPS
					playerspriteno=0
					isFadingOut='paused'
					gameState='splash'
					isFadingIn='splash'
					splash.set_alpha(0)
					pygame.mixer.music.fadeout(500)
					sil_time=time.time()
					
			if gameState=='gameOver':
				#sfxDead.play()
				screen.blit(dedsplash,(0,0))
				if event.key==K_z:
					player1.reset()
					drops=[]
					dropFPS=initdropFPS
					playerspriteno=0
					init_time=pygame.time.get_ticks()
					isFadingOut='gameOver'
					gameState='game'
					isFadingIn='game'
					bg1.set_alpha(0)
					
			if event.key==K_ESCAPE:
				gameOn=False
		elif event.type==QUIT:
			gameOn=False
	pygame.display.update()
	fpsClock.tick(FPS)
		
pygame.quit()