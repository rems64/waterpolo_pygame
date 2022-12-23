import sys
import pygame as pg
from typing import *
import random

Vec2 = pg.math.Vector2
Vec3 = pg.math.Vector3
Vec = Vec2|Vec3

Number = float|int

def to_vec3(v: Vec) -> Vec3:
    if isinstance(v, Vec3):
        return v
    elif isinstance(v, Vec2):
        return Vec3(v.x, v.y, 0.0)
    else:
        raise Exception(f"Attempt to convert {type(v)} to Vec3")

def to_vec2(v: Vec) -> Vec2:
    if isinstance(v, Vec2):
        return v
    elif isinstance(v, Vec3):
        return Vec2(v.x, v.y)
    else:
        raise Exception(f"Attempt to convert {type(v)} to Vec2")

def is_key_down(key):
    keys = pg.key.get_pressed()
    return keys[key]

def normalized(vec):
    if vec.length_squared() <= 0.000001:
        return vec
    return vec.normalize()

def get_directional_vector(key_l, key_r, key_u, key_d):
    v = Vec2(0, 0)
    if is_key_down(key_l): v.x = -1
    if is_key_down(key_r): v.x = 1
    if is_key_down(key_u): v.y = -1
    if is_key_down(key_d): v.y = 1
    return normalized(v)

def get_directional_vector3(key_l, key_r, key_u, key_d):
    return to_vec3(get_directional_vector(key_l, key_r, key_u, key_d))


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    MAGENTA = (255, 0, 255)


class Constants:
    DEFAULT_FRICTION = 100

     
     
class Image:
    def __init__(self, path:str, dimensions=None) -> None:
        self.path = path
        self._image = pg.image.load(path)
        if dimensions:
            self._image = pg.transform.scale(self._image, dimensions)
    
    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, val):
        self._image = val
    
    def draw(self, screen:pg.Surface, x:Vec2|Number, y:Number|None=None):
        if isinstance(x, Vec):
            screen.blit(self._image, x)
        elif isinstance(x, Number) and isinstance(y, Number):
            screen.blit(self._image, (x, y))
        else:
            raise Exception(f"Invalid type given : type(x) = {type(x)}, type(y) = {type(y)}")
    

class Object:
    def __init__(self) -> None:
        self._delete_me = False
        
        
class Actor(Object):
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__()
        self.pos = Vec3(x, y, z)
        self.vel = Vec3(0, 0, 0)
        self.acc = Vec3(0, 0, 0)

        self.friction = Constants.DEFAULT_FRICTION
        self._forces = []
        
        self.image: Image|None = None
    
    def set_image(self, image:Image|str):
        if type(image) == Image:
            self.image = image
        elif type(image) == str:
            self.image = Image(image)
        return self
    
    def update(self, dt: float) -> None:
        # Apply friction
        self.apply_force(-self.vel * self.friction * dt)
        
        self.acc = Vec3()
        for f in self._forces:
            self.acc += f
        
        self._forces.clear()
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        
    def draw(self, screen: pg.Surface) -> None:
        if self.image == None:
            raise Exception("Actor image is not defined")
        self.image.draw(screen, self.pos.x, self.pos.y)
    
    def apply_force(self, force: Vec) -> None:
        assert isinstance(force, Vec), f"Attempt to apply non-vector force: {type(force)}"
        
        direction = to_vec3(force)
        self._forces.append(force)
        return self
        

class Player(Actor):
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__(x, y, z)
        self.movement_force = 300
                
    def update(self, dt):
        dir = get_directional_vector3(pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN)
        self.apply_force(dir * self.movement_force)
        
        self.do_movement(dt)
        # print(self.pos)
        
        super().update(dt)

    def do_movement(self, dt) -> None:
        self.do_diving(dt)

    def do_diving(self, dt) -> None:
        ...

class Game:
    def __init__(self, caption="My Game", width=640, height=480, **flags) -> None:
        self.dimensions = self.width, self.height = width, height
        self.fps = 60
        self._clock = pg.time.Clock()     ## For syncing the FPS
        self._actors: List[Actor] = []
        
        pg.init()
        pg.mixer.init()  ## For sound

        self.is_fullscreen = False
        
        mode = 0
        for k,v in flags.items():
            if k == "fullscreen" and v:
                mode = pg.FULLSCREEN
             
        self.screen: pg.Surface = pg.display.set_mode((width, height), mode)
        pg.display.set_caption(caption)
        
        self.frame = 0
        self.prevdt = 1/self.fps

    def main(self) -> None:
        # Main game loop.
        self.init()
        
        dt = 1/self.fps
        self.prevdt = 1/self.fps
        while True:
            self.update(dt)
            self.draw(self.screen)

            self.prevdt = dt
            dt = self._clock.tick(self.fps) / 1000
            
    def init(self):
        player = Player(30, 30).set_image(Image("./img/player.png", (64, 64)))
        player2 = Player(30, 70).set_image(Image("./img/player.png", (64, 64)))
        player3 = Player(30, 120).set_image(Image("./img/player.png", (64, 64)))
        game.new_actor(player)
        game.new_actor(player2)
        game.new_actor(player3)
        
    def update(self, dt:float) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit() 
                sys.exit() 
        
        i = 0
        while i < len(self._actors):
            a = self._actors[i]
            if a._delete_me:
                self._actors.pop(i)
            else:
                if i%3 == 0: 
                    a.update(dt)
                    print("a", a.acc, "v", a.vel, "p", a.pos)
    
                elif i%3 == 1:
                    if self.frame % 2 == 0:
                        a.update(dt + self.prevdt)
                i += 1
                
        self.frame += 1
                
    def draw(self, screen) -> None:
        screen.fill((0, 0, 0))

        # Draw
        for a in self._actors:
            a.draw(screen)

        # Flip the display so that the things we drew actually show up.
        pg.display.flip()
    
    def new_actor(self, actor:Actor):
        self._actors.append(actor)
        


game = Game("Wow awesome game", 640*2, 480*1.6) 
game.main()
