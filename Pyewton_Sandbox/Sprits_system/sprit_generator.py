from PIL import Image, ImageDraw
import os

def generateCircle(diameter, color, sprit_Name, rgb_mode='RGBA', directorieFolder='image') -> str:
    """
    Generates a circle image and saves it to the specified directory.
    
    Parameters:
        diameter (int): The diameter of the circle in pixels.
        color (tuple): The color to use to fill the circle, in the format (red, green, blue, alpha).
        sprit_Name (str): The name to use for the output image file.
        rgb_mode (str): The RGB mode to use for the image (default is 'RGBA').
        directorieFolder (str): The directory to save the image file in (default is 'image').
    
    Returns:
        str: The file path of the generated image.
    """
    height, width = int(diameter), int(diameter)
    image = Image.new(rgb_mode, (height, width), (0,0,0,0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, diameter-1, diameter-1), fill=color)
    outputPath = f"{directorieFolder}/{sprit_Name}.png"
    image.save(outputPath)

    return outputPath
