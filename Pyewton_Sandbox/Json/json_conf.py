import json
from Body import Body
from Vecteur2D import Vecteur2D


def loadBodysList(jsonPath) -> list[Body]:
    """
    Charge une liste de corps à partir d'un fichier JSON situé au chemin spécifié.

    Parameters:
        jsonPath (str): Chemin d'accès au fichier JSON contenant les informations sur les corps.

    Returns:
        list[Body]: Une liste d'objets "corps" créés à partir des informations contenues dans le fichier JSON.
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
    Charge les informations relatives à l'application à partir d'un fichier JSON situé dans le chemin spécifié.

    Parameters:
        jsonPath (str): Chemin d'accès au fichier JSON contenant les informations relatives à l'application.

    Returns:
        dict: Un dictionnaire contenant les informations relatives à l'application.
    """
    appInfo = {}
    with open(jsonPath) as file:
        data = json.load(file)
    appInfo = data["app_info"]
    return  appInfo

def saveInfo(jsonPath, bodyList:"list[Body]", appInfo:dict):
    """
    Sauvegarde des corps et des informations sur l'application dans un fichier JSON situé dans le chemin spécifié.

    Parameters:
        jsonPath (str): Chemin d'accès au fichier JSON dans lequel les informations seront enregistrées.
        bodyList (list[Body]): Une liste d'objets 'corps' à enregistrer dans le fichier JSON.
        appInfo (dict): Un dictionnaire contenant des informations sur l'application à enregistrer dans le fichier JSON.
    """
    data = {}
    bodys = []
    for body in bodyList:
        body_info = {}

        #Nom
        body_info['name'] = body.name

        #Position
        body_info['pos_x'] = float(body.pos_x)
        body_info['pos_y'] = float(body.pos_y)
        
        #Vitesse
        velocite = {"x":float(body.velocity.x),
                    "y":float(body.velocity.y)}
        body_info['velocity'] = velocite

        #Masse
        body_info["masse"] = float(body.masse)

        #Couleur
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

        #Taille
        body_info['size'] = float(body.size)
        bodys.append(body_info)
    
    data["app_info"] = appInfo
    data["bodys"] = bodys

    with open(jsonPath, 'w') as f:
        json.dump(data, f, indent=4)