import Sprits_system.sprit_generator as sprit_generator
from Vecteur2D import Vecteur2D
from decimal import Decimal

class Body:
    def __init__(self, 
                 name: str, 
                 pos=(0, 0), 
                 velocity:Vecteur2D=Vecteur2D(0,0), 
                 masse: float=100,
                 color=(255, 0, 255, 255), 
                 size=70,
                 is_fixed_point:bool=False):
        
        self.name=name
        self.pos_x=Decimal(pos[0])
        self.pos_y=Decimal(pos[1])
        self.velocity = velocity
        self.masse = Decimal(masse)
        self.color=color
        self.size = size
        self.is_fixed_point = is_fixed_point
        self.CreateSprite()

    def CreateSprite(self):
        """
        Create the sprites for the body (main sprite and trajectorie sprite).
        """
        self.spritePath = sprit_generator.generateCircle(self.size, self.color, self.name, directorieFolder="Sprits_system/image")
        self.pos_SpritePath = sprit_generator.generateCircle(3.5, self.color, self.name + "pos", directorieFolder="Sprits_system/image/Pos_sprites")