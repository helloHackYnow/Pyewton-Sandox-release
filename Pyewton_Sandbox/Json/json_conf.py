import json
from Body import Body
from Vecteur2D import Vecteur2D


def loadBodysList(jsonPath) -> list[Body]:
    """
    Load a list of bodys from a JSON file located at the specified path.

    Parameters:
        jsonPath (str): The path to the JSON file containing the body information.

    Returns:
        list[Body]: A list of Body objects created from the information in the JSON file.
    """
    list_bodys = []
    with open(jsonPath) as file:
        data = json.load(file)
        
    for body_info in data['bodys']:

        #Récuperer le nom
        name = body_info['name']

        #Récuperer la position d'origine
        pos_x = body_info['pos_x']
        pos_y = body_info['pos_y']
        pos = (pos_x, pos_y)

        #Récuperer la velocité
        x = body_info['velocity']['x']
        y = body_info['velocity']['y']
        velocite = Vecteur2D(x, y)

        #Récuperer la masse
        mass = body_info['masse']

        #Récuperer la couleur
        r = body_info["color"]['r']
        g = body_info["color"]['g']
        b = body_info["color"]['b']
        a = body_info["color"]['a']
        couleur = (r, g, b, a)

        #Récuperer la taille
        size = body_info['size']

        #Instantcier la planète
        body = Body(name, pos, velocite, mass, couleur, size)
        list_bodys.append(body)
    return list_bodys

def loadInfoApp(jsonPath:str) -> dict:
    """
    Load app information from a JSON file located at the specified path.

    Parameters:
        jsonPath (str): The path to the JSON file containing the app information.

    Returns:
        dict: A dictionary containing the app information.
    """
    appInfo = {}
    with open(jsonPath) as file:
        data = json.load(file)
    appInfo = data["app_info"]
    return  appInfo

def saveInfo(jsonPath, bodyList:"list[Body]", appInfo:dict):
    """
    Save bodys and app informations to a JSON file located at the specified path.

    Parameters:
        jsonPath (str): The path to the JSON file to which the information will be saved.
        bodyList (list[Body]): A list of Body objects to be saved to the JSON file.
        appInfo (dict): A dictionary containing app information to be saved to the JSON file.
    """
    data = {}
    bodys = []
    for body in bodyList:
        body_info = {}

        #Name
        body_info['name'] = body.name

        #Position
        body_info['pos_x'] = float(body.pos_x)
        body_info['pos_y'] = float(body.pos_y)
        
        #Velocity
        velocite = {"x":float(body.velocity.x),
                    "y":float(body.velocity.y)}
        body_info['velocity'] = velocite

        #Mass
        body_info["masse"] = float(body.masse)

        #Color
        r = body.color[0]
        g = body.color[1]
        b = body.color[2]
        a = body.color[3]
        color = {
            "r":r,
            "g":g,
            "b":b,
            "a":a
        }
        body_info["color"] = color

        #Size
        body_info['size'] = float(body.size)
        bodys.append(body_info)
    
    data["app_info"] = appInfo
    data["bodys"] = bodys

    with open(jsonPath, 'w') as f:
        json.dump(data, f, indent=4)