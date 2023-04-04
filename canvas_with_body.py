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
        
        # Show axis
        if show_axis:
            self.create_line(width/2, 0, width/2, height, fill=axis_color)
            self.create_line(0, height/2, width, height/2, fill=axis_color)
        
        # Scale indicator
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
        Creates a new body, wich is basically a circle with arrow pointing from its center representing its velocity.

        Parameters:
            pos_x (float): The x-coordinate of the body's position (default is 0).
            pos_y (float): The y-coordinate of the body's position (default is 0).
            velocity (Vecteur2D): The velocity of the body (default is Vecteur2D(50, 0)).

        Returns:
            circle_id (int): The ID of the created circle object.
            arrow_id (int): The ID of the created arrow object.
        """
        # Create a circle and arrow at the specified position
        r = Decimal(size/2)
        circle_id = self.create_oval(pos_x - r, pos_y - r, pos_x + r, pos_y + r, fill=color)
        arrow_id = self.create_line(pos_x, pos_y, pos_x + velocity.x, pos_y + velocity.y, arrow=tk.LAST, width=2)
        
        # Bind the start_drag and on_drag functions to the left mouse button press and release events for the new objects
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
        """function that will be called when the user starts dragging the circle or the arrow.

        Parameters:
            event (tkinter event object): The event object representing the situation at the begining of the mouse drag.
        """
        # Remember the starting position of the object
        self.x = event.x
        self.y = event.y


    def on_drag(self, event, arrow_id):
        """This function that will be called when the user moves the mouse while dragging the circle or the arrow.

        Parameters:
            event (tkinter event object): The event object representing the mouse drag.
            arrow_id (int): id of the arrow associate with the circle the user is moving
        """
        # Calculate the distance the mouse has moved
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        # Move the object by the same distance
        self.move(tk.CURRENT, delta_x, delta_y)
        self.move(arrow_id, delta_x, delta_y)
        # Update the starting position for the next time this function is called
        self.x = event.x
        self.y = event.y


    def on_drag_arrow(self, event):
        """This function that will be called when the user drag the arrow.

        Parameters:
            event (tkinter event object): The event object representing the mouse drag.
        """
        # Update the end position of the arrow, keeping the start position fixed at the center of the circle
        first_pos = self.coords(tk.CURRENT)
        self.coords(tk.CURRENT, first_pos[0], first_pos[1], event.x, event.y)
        
    
    def get_all_positions(self):
        """
        function which calculate the positions and velocity vector of each body

        Returns
        -------
        _type_ : list
            _description_ : list containing the position and the velocity vector of each body
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
