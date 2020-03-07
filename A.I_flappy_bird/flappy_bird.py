import pygame
import neat
import time
import os
import random

# Constant variables
WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

# Load image files into variables
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
				pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
					pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.jpg")))

pygame.font.init()                                  # initialise font
STAT_FONT = pygame.font.SysFont("comicsans", 50)    # type of font and its size for score board


# Bird class to control bird using different methods
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25               # tilt = 25 degrees rotation 
    ROT_VEL = 20                    # how much it moves per frame
    ANIMATION_TIME = 5              # how long each bird animation
    
    def __init__(self, x, y):
        self.x = x                  # horizontal position of bird
        self.y = y                  # vertical position of bird
        self.tilt = 0               # how much image is titled at start
        self.tick_count = 0
        self.vel = 0                # not moving at start
        self.height = self.y
        self.img_count = 0          # which image of bird we showing
        self.img = self.IMGS[0]     # bird1.png, starting state 
        
    def jump(self):
        self.vel = -10.5            # jump requires negative velocity as moving up vertical axis is lesser in value
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1        # frame went by, keep track how many times moved
        d = self.vel * self.tick_count + (1.5 * self.tick_count**2)     # tick count how many seconds moving, every movement will add tick count. creates an arc for bird jumping as value d reduces
        
        if d >= 16:                 # if d value more than 16, set it to 16 max 
            d = 16
        
        if d < 0:                   # if jump, jump a little higher, looks nicer
            d -= 2
            
        self.y = self.y + d         # add distance moved to bird vertical value
        
        if d < 0 or self.y < self.height + 50:  # if bird jumps, dont tilt too much
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > - 90:                # if bird drops, face down perpendicalarly
                self.tilt -= self.ROT_VEL
        
    def draw(self, win):                                # draw bird on the window
        self.img_count += 1                             # determines how many times image shown
        
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]                     # bird wings flap up
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]                     # bird wings starting position
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]                     # bird wings flap down
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]                     # bird wings starting position
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]                     # bird wings flap up
            self.img_count = 0
            
        if self.tilt <= -80:
           self.img = self.IMGS[1]                      # if bird is falling, wings remain at starting position
           self.img_count = self.ANIMATION_TIME * 2     # looks normal when flying up
              
        rotated_image = pygame.transform.rotate(self.img, self.tilt)        # rotate image, while keeping it in the center
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)    # creates a rectangle box around bird object to keep it centered
        win.blit(rotated_image, new_rect.topleft)       # blit = draw 
        
    def get_mask(self):                                 # collision for objects
        return pygame.mask.from_surface(self.img)

# Pipe class to control pipe
class Pipe:
    GAP = 200
    VEL = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0                                                        # top of pipe
        self.bottom = 0                                                     # bottom of pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)        # flip the pipe image for top pipe
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False                                                 # set bird passed pipe as false
        self.set_height()                                                   # method to define above variables
        
    def set_height(self):
        self.height = random.randrange(50, 450)                             # random value for height of pipe
        self.top = self.height - self.PIPE_TOP.get_height()                 # given height of pipe - constant height of pipe image result in starting position of given height of pipe
        self.bottom = self.height + self.GAP                                # given height of pipe + Gap between top pipe to determine collision point of bottom pipe
    
    def move(self):
        self.x -= self.VEL                                                  # change x position of pipe based on the velocity the pipe should move each frame, negative = move it left
    
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))                         # draw top pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))                   # draw bottom pipe
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))            # difference between positon of bird and collision point of top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))      # difference between positon of bird and collision point of bottom pipe
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)             # see if collide between bird and bottom mask, check using bottom offset
        t_point = bird_mask.overlap(top_mask, top_offset)                   # see if collide between bird and top mask, check using top offset
        
        if b_point or t_point:                                              # if not none,  return collision is true
            return True   
        return False                                                        # if no collision return false
        
# Base class to allow the base to move continuously
class Base:
    VEL = 5                                         # speed of movement
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:                # when end of first base crosses starting point or out of frame, place it behind the 2nd base following it
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:                # vice versa, repeat process to looks like a continuos base
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))       # draw base 1
        win.blit(self.IMG, (self.x2, self.y))       # draw base 2
        
            
    
      

# Draw function
def draw_window(win, birds, pipes, base, score, gen):        # draw background image with bird, pipes, base and scoreboard on it
    if gen == 0:
        gen = 1
    win.blit(BG_IMG, (0,0))         # draw bg at position 0,0
    
    for pipe in pipes:
        pipe.draw(win)              # draw every new pipe in pipe list using draw method
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))     # text displayed with color
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))                 # position of score board so will not go out of frame
    
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))         # text displayed with color
    win.blit(text, (10, 10))        # position of score board so will not go out of frame
    
    base.draw(win)                  # draw base object using draw method   
    for bird in birds:
        bird.draw(win)              # draw bird object using draw method above
    pygame.display.update()         # update and refreshes display of game
    
def main(genomes, config):          # act as fitness function by taking all the genomes and evaluate them
    global GEN
    GEN += 1
    nets = []                       # bunch of neural networks controlling birds  
    ge = []                         # control fitness value for bird
    birds = []                      # bird object at position x, y
    
    for __, g in genomes:           # genome is a tuple with id and object, eg: (1, ge)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)            # add net, bird, ge at the same position, each position for one bird
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    
    
    base = Base(730)                # bottom of screen
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))      # create pygame window
    score = 0
    
    clock = pygame.time.Clock()     # set frame rate for bird to move
    
    run = True                      # run program unless quit, run will be set to False
    while run:
        clock.tick(30)              # 30 frames per seconds bird moves
        for event in pygame.event.get():    # keep track of any movement from user, such as click on exit button
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():      # bird passes first pipe
                pipe_ind = 1        # look at 2nd pipe
        else:                       # if not generation left quit game
            run = False
            break
                
        for x, bird in enumerate(birds):
            bird.move()             # bird moves
            ge[x].fitness += 0.1    # REWARD bird by increasing its fitness (0.1 * 30)
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))      # activate nn with inputs: bird y value, distance of bird and top pipe, bottom pipe
            
            if output[0] > 0.5:    # tanh activation function, only 1 output neuron
                bird.jump()
        
        base.move()                 # base to move forward
        
        rem = []                    # pipe remove list
        add_pipe = False
        for pipe in pipes:          # move all the pipes to the left
            for x, bird in enumerate(birds):
                if pipe.collide(bird):      # get rid of bird that collide or died
                    ge[x].fitness -= 1      # minus is fitness by 1, PUNISHMENT, prevent bird from crashing through pipes to increase distance
                    birds.pop(x)    # remove these birds
                    nets.pop(x)
                    ge.pop(x)
            
                if not pipe.passed and pipe.x < bird.x:     # if bird passed pipe
                    pipe.passed = True
                    add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:      # when top pipe exits the screen, add pipe to removed list
                rem.append(pipe)
            
            pipe.move()             # move pipe forward
            
        if add_pipe:                # add 1 pt if pased pipe successfully
            score += 1
            for g in ge:
                g.fitness += 5      # if passed pipe will add 5 fitness score, REWARD
            pipes.append(Pipe(600)) # create new pipe on the screen when passed
        
        for r in rem:
            pipes.remove(r)
        
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:       # if bird touches the base or over the top
                birds.pop(x)        # remove these birds
                nets.pop(x)
                ge.pop(x)
        
        if score > 50:              # bird is winner, stop training
            break
            
        draw_window(win, birds, pipes, base, score, GEN)      # call method to draw bird, pipes, base, scoreboard on window
                
    
def run(config_path):
    # import pickle to store the winner so that dont need retrain model, but code will run one bird instead of array of birds
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)  # add in all the properties, NEAT is assumed have
    
    p = neat.Population(config)     # generate population using config file
    
    p.add_reporter(neat.StdOutReporter(True))        # show stats when running each generations
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main, 50)        # call main function 50 times, passed in all the genomes, config file, run up to 50 generations
    
    print('\nBest genome:\n{!s}'.format(winner))
    
    
    

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)       # path to the current directory to build in config file
    config_path = os.path.join(local_dir, "NEAT_config.txt")    # join current directory to config file, load it
    run(config_path)
    
    
        
       
           
       