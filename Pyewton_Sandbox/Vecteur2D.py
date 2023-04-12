from math import hypot, atan, cos, sin, pi
from decimal import Decimal


class Vecteur2D:
    def __init__(self, x:Decimal, y:Decimal):
        """
        Initialise un vecteur 2d avec les coordonnées x et y données

        Parameters:
            x (Decimal): La coordonnées x du vecteur.
            y (Decimal): La coordonnées y du vecteur.
        """
        self.x = Decimal(x)
        self.y = Decimal(y)
        

    def norme(self):
        """
        Calcul la norme du vecteur.

        Returns:
            float: The norm of the vector.
        """
        return hypot(self.x, self.y)
    
    def angle_with_X_axis(self):
        """
        Retourne l'angle formé par le vecteur et l'axe des abcisses (en radians)
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
        Réécrit l'opérateur + pour l'addition de deux vecteurs.

        Parameters:
            v (Vecteur2D): Le vecteur à ajouter au vecteur actuel.

        Returns:
            Vecteur2D: Le vecteur résultant de l'addition des deux vecteurs.
        """
        return Vecteur2D(self.x + Decimal(v.x), self.y + Decimal(v.y))
    

    def __mul__(self, r):
        """
        Réécrit l'opérateur * pour la multiplication d'un vecteur par un réél.

        Parameters:
            r (int or float): Le réél par lequel le vecteur doit être multiplié.

        Returns:
            Vecteur2D: Le vecteur résultant de la multiplication.
        """
        return Vecteur2D(self.x * Decimal(r), self.y * Decimal(r))
        
    
    @staticmethod
    def composante_XY(norme, origin_x, origin_y, direction_x, direction_y):
        """
        Calcule les composantes x et y du vecteur avec les informations données.
        """
        # Coefficient directeur
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
        #Calcule du x et du y 
        x = norme * Decimal(cos(angle_x))
        y = norme * Decimal(sin(angle_x))
        return Vecteur2D(x, y)