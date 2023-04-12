from PIL import Image, ImageDraw
import os

def generateCircle(diameter, color, sprit_Name, rgb_mode='RGBA', directorieFolder='image') -> str:
    """
    Génère une image circulaire et l'enregistre dans le répertoire spécifié.
    
    Parameters:
        diameter (int): Le diamètre du cercle (en pixel)
        color (tuple): La couleur à utiliser dans le format : (rouge, vert, bleu, alpha).
        sprit_Name (str): Le nom du fichier.
        rgb_mode (str): Le mode de couleur à utiliser pour l'image (défaut est 'RGBA').
        directorieFolder (str): Le dossier dans lequel sauvegarder le fichier (défaut est 'image').
    
    Returns:
        str: Le chemin d'accès au fichier de l'image générée.
    """
    height, width = int(diameter), int(diameter)
    image = Image.new(rgb_mode, (height, width), (0,0,0,0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, diameter-1, diameter-1), fill=color)
    outputPath = os.path.join(directorieFolder, f"{sprit_Name}.png")
    image.save(outputPath)

    return outputPath
