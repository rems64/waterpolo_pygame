import sys
import pygame as pg
from typing import *
import random

Vec2 = pg.math.Vector2
Vec3 = pg.math.Vector3
Vec = Vec2|Vec3

Number = float|int

def sqr(x):
    # Actually faster than x*x ! 
    # https://stackoverflow.com/questions/18453771/why-is-x3-slower-than-xxx/18453999#18453999
    return x**2

def cube(x):
    return x*x*x

def pow4(x):
    return x*x*x*x

def hex_to_rgb(code):
    return (code >> 16, (code >> 8) % 256, code % 256)

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

# TODO: use button states (0: released; 1:just pressed; 2:down; 3:just released) 
# and implement is_key_pressed using this & modify is_key_down

def is_key_down(key):
    keys = pg.key.get_pressed()
    return keys[key]


def normalized(vec):
    if vec.length_squared() <= 0.000001:
        return vec
    return vec.normalize()

def get_directional_vector(directions):
    key_l, key_r, key_u, key_d = directions
    
    v = Vec2(0, 0)
    if is_key_down(key_l): v.x += -1
    if is_key_down(key_r): v.x += 1
    if is_key_down(key_u): v.y += -1
    if is_key_down(key_d): v.y += 1
    return normalized(v)

def get_directional_vector3(directions):
    return to_vec3(get_directional_vector(directions))


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
    DEFAULT_FRICTION = 0.01
    DEFAULT_MOVEMENT_FORCE = DEFAULT_FRICTION * 200000

     
     
class Image:
    def __init__(self, path:str, size=None) -> None:
        self.path = path
        self._image = pg.image.load(path)
        if size:
            self._image = pg.transform.scale(self._image, size)
        
        self.size = self.width, self.height = self._image.get_size()
    
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
    
class Controls:
    def __init__(self, dict) -> None:
        self.left = dict["left"]
        self.right = dict["right"]
        self.up = dict["up"]
        self.down = dict["down"]
        self.move = [self.left, self.right, self.up, self.down]
        
        self.dive = dict["dive"]

class Object:
    def __init__(self) -> None:
        self._delete_me = False  
    
    def delete(self) -> None:
        self._delete_me = True
        
        
class Actor(Object):
    """
    Object with a position, velocity and subject to forces.
    """
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__()
        self.pos: Vec3 = Vec3(x, y, z)
        self.vel: Vec3 = Vec3(0, 0, 0)
        self.acc: Vec3 = Vec3(0, 0, 0)

        self.friction: Number = Constants.DEFAULT_FRICTION
        self._forces: List[Vec3] = []
        
        self.image: Image|None = None
    
    def set_image(self, image: Image|str):
        if type(image) == Image:
            self.image = image
        elif type(image) == str:
            self.image = Image(image)
        return self
    
    def update(self, dt: float) -> None:
        # Apply friction
        # self.apply_force(-self.vel * self.friction)
        
        self.acc = Vec3()
        for f in self._forces:
            self.acc += f
        
        self._forces.clear()
        self.vel += self.acc * dt
        self.vel *= self.friction ** dt
        
        self.pos += self.vel * dt
        
    def draw(self, screen: pg.Surface) -> None:
        if self.image:
            self.image.draw(screen, self.pos.x - self.image.width/2, self.pos.y - self.image.height/2)
            # raise Exception("Actor image is not defined")
    
    def apply_force(self, force: Vec) -> None:
        assert isinstance(force, Vec), f"Attempt to apply non-vector force: {type(force)}"
        
        direction = to_vec3(force)
        self._forces.append(force)
        return self


class Collision:
    def __init__(self) -> None:
        pass
    
    def is_touching_sphere_sphere(self, a, b, a_pos: Vec, b_pos: Vec):
        a_pos = to_vec3(a_pos)
        b_pos = to_vec3(b_pos)

        dist_sq = (a_pos.x - b_pos.x)**2 + (a_pos.y - b_pos.y)**2
        return dist_sq <= (a.radius + b.radius)**2


class SphereCollision(Collision):
    def __init__(self, radius: Number) -> None:
        super().__init__()
        self.radius: Number = radius
        
    def is_touching(self, other, self_pos, other_pos):
        if isinstance(other, SphereCollision):
            return self.is_touching_sphere_sphere(self, other, self_pos, other_pos)
        


class CollidableActor(Actor):
    """
    Actor with a collision. May or may not interact with other CollisionActor.
    """
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__(x, y, z)
        
        self.collision: Collision|None = None
        self.is_solid = False
    
    def set_collision(self, coll: Collision):
        self.collision = coll
        return self
    
    def set_solid(self, val: bool):
        self.is_solid = val
        return self

    def is_touching(self, other: 'CollidableActor'):
        assert self.collision != None, "Collision not defined for self"
        assert isinstance(other, CollidableActor), "other is not CollidableActor"
        assert other.collision != None, "Collision not defined for other"
        
        return self.collision.is_touching(other.collision, self.pos, other.pos)
    
    def on_collision(self, other):
        # To be implemented in subclasses
        # print(f"Collision between {self} and {other}")
        ...
    

class Player(CollidableActor):
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__(x, y, z)
        
        self.controls = Controls({
            "left": pg.K_LEFT,
            "right": pg.K_RIGHT,
            "up": pg.K_UP,
            "down": pg.K_DOWN,
            "dive": pg.K_LSHIFT,
        })
        
        self.swimming_force = Constants.DEFAULT_MOVEMENT_FORCE
        self.diving_force = Constants.DEFAULT_MOVEMENT_FORCE * 2.0
        self.current_force = self.swimming_force
        
        self.is_diving = False

    def update(self, dt):
        self.do_movement(dt)
        
        super().update(dt)
    
    def draw(self, screen):
        pg.draw.circle(screen, (0,80,0,0.5), to_vec2(self.pos), self.collision.radius)
        super().draw(screen)

    def do_movement(self, dt) -> None:
        dir = get_directional_vector3(self.controls.move)
        self.apply_force(dir * self.current_force)

        self.do_diving(dt)

    def do_diving(self, dt) -> None:
        self.is_diving = is_key_down(self.controls.dive)
        
        if self.is_diving:
            self.current_force = self.diving_force
        else:
            self.current_force = self.swimming_force
            
    def on_collision(self, other):
        self.apply_force(other.vel)


class Ball(CollidableActor):
    def __init__(self, x=0, y=0, z=0) -> None:
        super().__init__(x, y, z)
        
        self.radius = 0
    
    def set_radius(self, val):
        self.radius = val
        self.set_collision(SphereCollision(val))
        return self
        
    def draw(self, screen) -> None:
        pg.draw.circle(screen, Colors.GREEN, to_vec2(self.pos), self.radius)


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
        player = Player(30, 30) \
            .set_image(Image("./img/player.png", (64, 64))) \
            .set_collision(SphereCollision(40)) \
            .set_solid(True)
        self.new_actor(player)
        
        ball = Ball(200, 200) \
            .set_radius(30) \
            .set_solid(True)
        self.new_actor(ball)
        
    def update(self, dt:float) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit() 
                sys.exit() 
        
        self.do_collisions(dt)    
        
        # Call update method on all actors
        i = 0
        while i < len(self._actors):
            a = self._actors[i]
            
            # Delete deleted actors
            if a._delete_me:
                self._actors.pop(i)
            
            else:
                a.update(dt)
                i += 1
                            

        self.frame += 1
                
    def do_collisions(self, dt:Number):
        # TODO: This is slow if there are a lot of actors
        # Could be optimized by segmenting the world into chunks 
        for i in range(len(self._actors)):
            for j in range(i+1, len(self._actors)):
                a1 = self._actors[i]
                a2 = self._actors[j]
                if a1.is_touching(a2):
                    a1.on_collision(a2)
                    a2.on_collision(a1)
        
    def draw(self, screen) -> None:
        screen.fill(hex_to_rgb(0x0095e9))

        # Draw
        for a in self._actors:
            a.draw(screen)

        # Flip the display so that the things we drew actually show up.
        pg.display.flip()
    
    def new_actor(self, actor:Actor):
        self._actors.append(actor)
        


game = Game("Wow awesome game", 640*2, 480*1.6) 
game.main()
