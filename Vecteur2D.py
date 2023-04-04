from math import hypot, atan, cos, sin, pi
from decimal import Decimal


class Vecteur2D:
    def __init__(self, x:Decimal, y:Decimal):
        """
        Initializes a 2D vector with the given x and y coordinates.

        Parameters:
            x (int or float): The x coordinate of the vector.
            y (int or float): The y coordinate of the vector.
        """
        self.x = Decimal(x)
        self.y = Decimal(y)
        

    def norme(self):
        """
        Calculate the norm (length) of the vector.

        Returns:
            float: The norm of the vector.
        """
        return hypot(self.x, self.y)
    
    def angle_with_X_axis(self):
        """Returns the angle formed by the vector and the x-axis (in radiants)
        
        """
        if self.x != 0:
            m = self.y / self.x
            
            #Angle with X axis
            if self.x < 0:
                angle_x = (pi + atan(m))
            else:
                angle_x = atan(m)
        else:
            if self.y < 0:
                angle_x = -pi/2
            else:
                angle_x = pi/2
                
        return angle_x
    
    def __add__(self, v):
        """
        Overloads the + operator to add two vectors.

        Parameters:
            v (Vecteur2D): The vector to add to the current vector.

        Returns:
            Vecteur2D: The resulting vector after adding the two vectors.
        """
        return Vecteur2D(self.x + Decimal(v.x), self.y + Decimal(v.y))
    

    def __mul__(self, r):
        """
        Overloads the * operator to multiply a vector by a scalar.

        Parameters:
            r (int or float): The scalar to multiply the vector by.

        Returns:
            Vecteur2D: The resulting vector after multiplying it by the scalar.
        """
        return Vecteur2D(self.x * Decimal(r), self.y * Decimal(r))
        
    
    @staticmethod
    def composante_XY(norme, origin_x, origin_y, direction_x, direction_y):
        """
        Calculates the x and y components of the vector with the given infos
        """
        #Leading coefficient of the direction
        diff_x = (direction_x - origin_x)
        diff_y = (direction_y - origin_y)
        
        
        if diff_x != 0:
            m = diff_y / diff_x
            
            #Angle with X axis
            if diff_x < 0:
                angle_x = (pi + atan(m))
            else:
                angle_x = atan(m)
        else:
            if diff_y < 0:
                angle_x = -pi/2
            else:
                angle_x = pi/2
        #Calcul of the x and y of the vectors   
        x = norme * Decimal(cos(angle_x))
        y = norme * Decimal(sin(angle_x))
        return Vecteur2D(x, y)