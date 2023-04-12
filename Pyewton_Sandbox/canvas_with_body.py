import tkinter as tk
from Vecteur2D import Vecteur2D
from typing import Callable
from decimal import Decimal

class CanvasWithBody(tk.Canvas):
    def __init__(self, 
                 master, 
                 width=0, 
                 height=0,
                 show_axis:bool=False,
                 axis_color:str="#000000",
                 scale:str=None):
        
        super().__init__(master, width=width, height=height)
        self.circle_list = []
        self.arrow_list = []
        
        # Montrer les axes
        if show_axis:
            self.create_line(width/2, 0, width/2, height, fill=axis_color)
            self.create_line(0, height/2, width, height/2, fill=axis_color)
        
        # Indicateur d'échelle 
        if scale:
            start = (40,height-40)
            lenght = 150 * scale
            while lenght < 100 or lenght > 200:
                if lenght > 200:
                    lenght /= 2
                else:
                    lenght *= 2
            end = (start[0] + lenght, start[1])
            self.create_line(start[0], start[1], end[0], end[1])
            self.create_line(start[0], start[1], start[0], start[1]-10)
            self.create_line(start[0]+lenght/2, start[1], start[0]+lenght/2, start[1]-5)
            self.create_line(end[0], end[1], end[0], end[1]-10)
            self.create_text(end[0], end[1]+10, text='{:.2e}'.format(int(lenght*scale))+' m')

    def create_body(self, 
                      pos_x:Decimal=Decimal(0), 
                      pos_y:Decimal=Decimal(0), 
                      velocity:Vecteur2D=Vecteur2D(50, 0), 
                      size:int=25, 
                      color="red", 
                      on_double_click:Callable=None
                      ):
        """
        Créé un nouveau corps ( rond coloré avec un flèche pointant de sin centre représentant sa vitesse)

        Parameters:
            pos_x (float): La coordonnée x de la position du corps (0 par défaut).
            pos_y (float): La coordonnée y de la position du corps (0 par défaut).
            velocity (Vecteur2D): La vitesse du corps (Vecteur2D(50, 0) par défaut).

        Returns:
            circle_id (int): L'ID de l'objet cercle créé.
            arrow_id (int): L'ID de l'objet flèche créé.
        """
        # Créer un cercle et une flèche à la position spécifiée
        r = Decimal(size/2)
        circle_id = self.create_oval(pos_x - r, pos_y - r, pos_x + r, pos_y + r, fill=color)
        arrow_id = self.create_line(pos_x, pos_y, pos_x + velocity.x, pos_y + velocity.y, arrow=tk.LAST, width=2)
        
        # Lier les fonctions start_drag et on_drag aux nouveaux objets.
        self.tag_bind(circle_id, '<ButtonPress-1>', self.start_drag)
        self.tag_bind(circle_id, '<B1-Motion>', lambda event, arrow_id=arrow_id:self.on_drag(event, arrow_id))
        self.tag_bind(arrow_id, '<ButtonPress-1>', self.start_drag)
        self.tag_bind(arrow_id, '<B1-Motion>', self.on_drag_arrow)
        
        if on_double_click != None:
            self.tag_bind(circle_id, '<Double-Button-1>', on_double_click)
        
        self.circle_list.append(circle_id)
        self.arrow_list.append(arrow_id)
        
        return circle_id, arrow_id
    

    def start_drag(self, event):
        """
        Fonction appelée lorsque l'utilisateur commencera à faire glisser le cercle ou la flèche.
        """
        # Mémoriser la position initiale de l'objet
        self.x = event.x
        self.y = event.y


    def on_drag(self, event, arrow_id):
        """
        Cette fonction est appelée lorsque l'utilisateur déplace la souris en faisant glisser le cercle ou la flèche.
        
        Parameters:
            arrow_id (int): id of the arrow associate with the circle the user is moving
        """
        # Calculer la distance parcourue par la souris
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        # Déplacer l'objet de la même distance
        self.move(tk.CURRENT, delta_x, delta_y)
        self.move(arrow_id, delta_x, delta_y)
        # Mise à jour de la position de départ en prévision du prochain appel de cette fonction
        self.x = event.x
        self.y = event.y


    def on_drag_arrow(self, event):
        """
        Cette fonction est appelée lorsque l'utilisateur fait glisser la flèche.
        """
        # Mettre à jour la position finale de la flèche, en gardant la position de départ fixée au centre du cercle.
        first_pos = self.coords(tk.CURRENT)
        self.coords(tk.CURRENT, first_pos[0], first_pos[1], event.x, event.y)
        
    
    def get_all_positions(self):
        """
        Fonction qui retourne les positions et le vecteur vitesse de chaque corps.
        
        Returns
        -------
        _type_ : list
            _description_ : liste contenant la position et le vecteur vitesse de chaque corps.
        """
        output_list = []
        for body in range(len(self.circle_list)):
            pos_circle = self.coords(self.circle_list[body])
            pos_arrow = self.coords(self.arrow_list[body])
            
            pos_x = (pos_circle[0] + pos_circle[2]) / 2
            pos_y = (pos_circle[1] + pos_circle[3]) / 2
            
            velocity_x = pos_arrow[2] - pos_arrow[0]
            velocity_y = pos_arrow[3] - pos_arrow[1]

            body_info = (Vecteur2D(pos_x, pos_y), Vecteur2D(velocity_x, velocity_y))

            output_list.append(body_info)

        return output_list
