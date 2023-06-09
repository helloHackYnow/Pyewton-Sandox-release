#Imports
import argparse
import customtkinter
import tkinter as tk
from PIL import Image
from Body import Body
import Json.json_conf as json_conf
import CTkColorPicker
import tool_tip as tl
import canvas_with_body as cwp
from decimal import Decimal
import json
from copy import deepcopy
from tkinter import filedialog
from simulation import * 
from AppInfoEditingWindow import AppInfoTopWindow
import ctypes
import webbrowser
from typing import Union
import sys
import psutil

argParser = argparse.ArgumentParser()
argParser.add_argument("--na", help="Exécute le programme sans les privilèges administrateurs. (Ne fonctionne que sur Windows)", action="store_true")
args = argParser.parse_args()

if sys.platform == "win32":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
    from gpu_tool import set_gpu_priority


#Niveau de priorité du processus
os_used = sys.platform
process = psutil.Process(os.getpid())
if os_used == "win32":  
    process.nice(psutil.REALTIME_PRIORITY_CLASS)
else:
    process.nice(20)


class App(customtkinter.CTk):

    DICO_UNITS = {"e+0":0, "e+3":3, "e+6":6, "e+9":9, "e+12":12, "e+15":15, "e+18":18}
    

    def __init__(self):
        super().__init__()

        self.path = os.path.dirname(os.path.realpath(__file__))
        
        if sys.platform == "win32":
            self.after(200, lambda: self.iconbitmap(os.path.join(self.path, "Icons", "Icon512.ico")))

            
        self.title("Pyewton Sandox")
        
        self.default_conf_path = os.path.join(self.path, "Json", "Default", "app_info.json")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.bad_values_list = []
        
        self.cleanSpriteFolder()
        
        # Vérifie si le programme à été lancé par l'utilisateur ou est issu d'un rechargement du programme
        # S'il s'agit d'un rechargement, il charge la configuration contenue dans le fichier temporaire, puis le supprime.
        if not self.isAReload():
            self.createEmptyConfiguration()
        else:
            json_temp_path = os.path.join(self.path, "temp.json")
            self.openConfiguration(configuration_path=json_temp_path)
            os.remove(json_temp_path)

        self.createMenuBar()
        

        self.update()
        
    def openConfiguration(self, configuration_path:Union[str, None]=None):
        """
        Ouvre une fenêtre pour sélectionner la configuration à charger
        """
        
        if not configuration_path:
            configuration_path = filedialog.askopenfilename(filetypes=[('Configuration file', '*.json')], 
                                                            initialdir=os.path.join(self.path, 'Json', 'Configurations'))
            self.conf_file_path = configuration_path

        self.bodyList:list[Body] = json_conf.loadBodysList(configuration_path)
        self.app_info = json_conf.loadInfoApp(configuration_path)
        
        #Charger les compute rules
        self.get_compute_rules()
        
        self.createMainInterface()


    def cleanSpriteFolder(self):
        """
        Nettoie  les dossiers de sprites.
        """
        # Nettoyage du dossier Sprite:
        sprite_folder_path = os.path.join(self.path, "Sprits_system", "Images")
        folder_content = os.listdir(sprite_folder_path)
        for item in folder_content:
            if item.endswith(".png"):
                os.remove(os.path.join(sprite_folder_path, item))
        # Nettoyage du dossier pos_sprite:
        sprite_folder_path = os.path.join(self.path, "Sprits_system", "Images", "Pos_sprites")
        folder_content = os.listdir(sprite_folder_path)
        for item in folder_content:
            if item.endswith(".png"):
                os.remove(os.path.join(sprite_folder_path, item))
    
    def createEmptyConfiguration(self):
        """
        Créé un fichier de configuration vide et le charge.
        """
        
        self.bodyList:list[Body] = []
        self.app_info = json_conf.loadInfoApp(self.default_conf_path)
        
        self.conf_file_path = os.path.join(self.path, "Json", "Sans-titre.json")
        
        self.createMainInterface()
    
    def createMainInterface(self):
        """
        Construit l'interface de départ
        """ 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.loadthemePreset()
        customtkinter.set_appearance_mode(self.theme_info['theme'])
        customtkinter.set_default_color_theme(self.theme_info['color'])
        
        self.createPreviewCanvas()
        self.createLeftMenu()
    
    def createPreviewCanvas(self):
        """
        Construit le cadre de prévisualisation
        """
        canvas_height = 540
        canvas_width = 990
        
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        
        self.frame_right.grid_columnconfigure(0, weight=0)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(1, weight=1)
        scale = Decimal(self.app_info["scale"] * 10**App.DICO_UNITS[self.app_info["scale_unit"]])
        
        self.previsual_canvas = cwp.CanvasWithBody(self.frame_right, 
                                                     width=canvas_width, 
                                                     height=canvas_height, 
                                                     show_axis=self.app_info['show_axis'], 
                                                     axis_color=self.app_info['axis_color'],
                                                     scale=scale)
        self.previsual_canvas.grid(row=0, column=0, padx=10, pady=10)
        
        self.previsual_canvas.update()
        
        self.height_offset = Decimal(self.previsual_canvas.cget("height")) /2
        self.width_offset = Decimal(self.previsual_canvas.cget("width")) /2
        
        body_index = 0
        for body in self.bodyList:
            r=body.color[0]
            g=body.color[1]
            b=body.color[2]
            color='#%02x%02x%02x' % (int(r), int(g), int(b))
            velocity = Vecteur2D(body.velocity.x, body.velocity.y*-1)
            self.previsual_canvas.create_body(self.width_offset + (body.pos_x / scale), self.height_offset + (body.pos_y *-1 / scale), 
                                                velocity * (1/scale), color=color, 
                                                on_double_click=lambda event, x=body_index:self.create_body_modification_window(x), size=body.size/2)
            body_index += 1   
    
    def createLeftMenu(self):
        """
        Construit la partie gauche de la fenêtre par défaut, avec : 
        la liste des corps, le bouton pour créer un corps, le bouton de démarrage, et le bouton des paramètres de la fenêtre.
        """
        #Body left_menu_frame
        self.left_menu_frame = customtkinter.CTkFrame(master=self,width=180,corner_radius=0)
        self.left_menu_frame.grid(row=0, column=0, sticky="nswe")
        
        
        #Create add an del button frame
        self.left_menu_frame.grid_columnconfigure(0, weight=1)
        self.left_menu_frame.grid_rowconfigure(0, weight=1)
        self.left_menu_frame.grid_rowconfigure(1, weight=1)
        self.left_menu_frame.grid_rowconfigure(2, weight=0)
        
        #Frame défilable pour la liste de corps
        #============================
        #scrollable frame
        self.list_body_frame = customtkinter.CTkScrollableFrame(master=self.left_menu_frame, width=150)
        self.list_body_frame.grid(row=0, column=0, padx=(15, 15), pady=20, sticky="nsew")

        self.list_button_body = [customtkinter.CTkButton]

        nb_body = len(self.bodyList)


        #Créer chaque boutons un par un
        for body_index in range(nb_body):
            body_name = self.bodyList[body_index].name

            
            button = customtkinter.CTkButton(master=self.list_body_frame, text=body_name,
                                            command=lambda x=body_index:self.create_body_modification_window(x))
            button.grid(row=body_index, columnspan=2, pady=5, padx=5, sticky="s")
            self.list_button_body.append(button)

        #Bouton pour ajouter un corps 
        #===============================
        self.add_button = customtkinter.CTkButton(master=self.left_menu_frame, text="Ajouter un corps",
                                                  command=self.addBody)
        self.add_button.grid(row=1, column=0, sticky="ewn", padx=15)
        
        #Frame pour les boutons
        #======================
        self.left_buttons_frame = customtkinter.CTkFrame(master=self.left_menu_frame, corner_radius=0,
                                                          fg_color="transparent")
        self.left_buttons_frame.grid(row=2, column=0, sticky="swe")
        
        #Bouton paramètres
        #=================
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Icons")
        self.settings_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "settings.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "settings.png")), size=(30, 30))
        self.settings_button = customtkinter.CTkButton(master=self.left_buttons_frame, 
                                                       width=40, height=40, fg_color="transparent", 
                                                       image=self.settings_image, text="", command=self.editAppInfo)   
        self.settings_button.grid(row=0, column=0, sticky="sw", padx=10, pady=10)
        
        #Bouton lancer simulation
        #========================
        
        self.start_button = customtkinter.CTkButton(master=self.left_buttons_frame, height=40,
                                                    text="Démarrer", command=self.startSimulation)
        self.start_button.grid(row=0, column=1, sticky="sew", padx=(0, 10), pady=10)

    def editAppInfo(self):
        """
        Charge les paramètres modifiés grâce la fenêtre des paramètres,
        et applique les modifications aux paramètres de simulation.
        """
        self.saveInfoFromPreviewCanvas()
        self.app_info_window = AppInfoTopWindow(self.app_info)   
        self.app_info = self.app_info_window.get()
        
        self.createPreviewCanvas()
    
    def get_compute_rules(self):
        """
        Obtient les règles de calcul définies dans le fichier 'computation_rules.json'
        """
        comput_path = os.path.join(self.path, "computation_rules", "computation_rules.json")
        with open(comput_path, "r") as compute_json:
            compute_rules = json.load(compute_json)
            self.compute_rule_list = [compute_rule["name"] for compute_rule in compute_rules]
            compute_json.close()
    
    
    def createMenuBar(self):
        """
        Construit la barre des menus.
        """
        self.menu_bar = tk.Menu(master=self)
        self.config(menu=self.menu_bar)
        
        # Menu "fichier"
        #=========
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label="Nouvelle configuration", command=self.createEmptyConfiguration)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Ouvrir configuration", command=self.openConfiguration)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Enregistrer", command=self.saveConfiguration)
        self.file_menu.add_command(label="Enregistrer sous", command=self.saveConfigurationAs)
        
        #Menu "Application"
        #============
        self.program_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.program_menu.add_command(label="Thème de l'application", command=self.create_theme_modification_window)
        self.program_menu.add_separator()
        self.program_menu.add_command(label="Recharger l'application", command=self.reloadProgram)
        
        #Menu "Aide"
        #=========
        self.help_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.help_menu.add_command(label="Page du projet", command=lambda:webbrowser.open("https://github.com/helloHackYnow/Pyewton-Sandox-release", new=2))
        self.help_menu.add_command(label="Documentation", command=lambda:webbrowser.open("https://github.com/helloHackYnow/Pyewton-Sandox-release/wiki", new=2))
        self.help_menu.add_command(label="A propos de nous")
        
        self.menu_bar.add_cascade(label="Fichier", menu=self.file_menu)  
        self.menu_bar.add_cascade(label="Application", menu=self.program_menu)   
        self.menu_bar.add_cascade(label="Aide", menu=self.help_menu)     
    
    
    def create_theme_modification_window(self):
        """
        Construit la fenêtre de modification du thème.
        """
        try:
            self.theme_modification_window.destroy()
        except:
            pass
        
        self.theme_modification_window = customtkinter.CTkToplevel()
        self.theme_modification_window.title("Apparence")
        
        self.theme_var = customtkinter.StringVar()
        self.theme_var.set(self.theme_info['theme'])
        
        self.theme_color_var = customtkinter.StringVar()
        self.theme_color_var.set(self.theme_info['color'])
        
        def on_closing():
            self.theme_modification_window.grab_release()
            self.theme_modification_window.destroy()

        def ok_event():
            on_closing()
            self.changeColorTheme(self.theme_var.get(), self.theme_color_var.get())

            
        self.theme_modification_window.protocol('WM_DELETE_WINDOW', on_closing)
        
        self.theme_modification_window.lift()
        self.theme_modification_frame = customtkinter.CTkFrame(master=self.theme_modification_window,
                                                               width=400,
                                                               height=600)
        self.theme_modification_frame.grid(padx =10, pady=(10, 0))
        
        #Labels
        self.theme_window_title = customtkinter.CTkLabel(master=self.theme_modification_frame,
                                                         text="Apparence", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.theme_window_title.grid(row=0, column=0, pady=10, padx=10)
        
        self.theme_entry_label = customtkinter.CTkLabel(master=self.theme_modification_frame,
                                                        text="Thème de l'application :")
        self.theme_entry_label.grid(row=1, column=0, padx=10, pady=(5, 5))
        
        self.theme_color_entry_label = customtkinter.CTkLabel(master=self.theme_modification_frame,
                                                        text="Couleur de l'application :")
        self.theme_color_entry_label.grid(row=2, column=0, padx=10, pady=(5, 10))
        
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.theme_modification_frame, values=["dark", "light", "system"],
                                                                       variable=self.theme_var)
        self.appearance_mode_optionemenu.grid(row=1, column=1, padx=(5, 5))
        
        self.color_mode_optionemenu = customtkinter.CTkOptionMenu(self.theme_modification_frame, values=["green", "blue", "dark-blue"],
                                                                  variable=self.theme_color_var)
        self.color_mode_optionemenu.grid(row=2, column=1, padx=(5, 5), pady=(5, 10))
        
        self.theme_button_frame = customtkinter.CTkFrame(master=self.theme_modification_window, fg_color="transparent",
                                                         corner_radius=0)
        self.theme_button_frame.grid(row=1, column=0, sticky='E')
        
        self.theme_window_ok_button = customtkinter.CTkButton(master=self.theme_button_frame,
                                                              text="Ok", width=100, command=ok_event)
        self.theme_window_ok_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.theme_window_cancel_button = customtkinter.CTkButton(master=self.theme_button_frame,
                                                                text="Annuler", width=100, command=on_closing)
        self.theme_window_cancel_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.after(20)
        self.theme_modification_window.grab_set()
            
    
    def create_body_modification_window(self, body_index):
        """
        Construit la fenêtre qui permet à l'utilisateur de modifier et de supprimer un corps.
        """
        
        # Détruire la fenêtre si elle est déjà ouverte
        try:
            self.body_modification_window.destroy()
        except:
            pass
        
        self.saveInfoFromPreviewCanvas()
        
        self.current_body_index = body_index

        name:str = self.bodyList[body_index].name
        
        self.body_modification_window = customtkinter.CTkToplevel()
        self.body_modification_window.title(f"Modifier le corps | {name}")
        self.body_modification_window.geometry("730x370")
        
        self.body_modification_window.protocol("WM_DELETE_WINDOW", self.onModificationWindowClose)

        self.body_modification_window.grid_columnconfigure(1, weight=1)

        self.body_modification_window.grid_rowconfigure(0, weight=0)
        self.body_modification_window.grid_rowconfigure(1, weight=1)

        self.left_frame_subWindow = customtkinter.CTkFrame(master=self.body_modification_window, corner_radius=0, width=140)
        self.left_frame_subWindow.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nswe")
        self.left_frame_subWindow.grid_rowconfigure(0, weight=1)
        self.left_frame_subWindow.grid_rowconfigure(1, weight=0)

        self.title_subWindow = customtkinter.CTkLabel(master=self.left_frame_subWindow, text=name.replace(' ', '\n'), 
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.title_subWindow.grid(padx=20, pady=20, sticky="n")

        self.del_body_button = customtkinter.CTkButton(master=self.left_frame_subWindow, text="Supprimer", 
                                                         command=self.deleteBody)
        self.del_body_button.grid(sticky="news", padx=10, pady=10, row=3)
        
        self.right_frame_subWindow = customtkinter.CTkFrame(master=self.body_modification_window)
        self.right_frame_subWindow.grid(row=0, column=1, rowspan=2, padx=15, pady=15, sticky="nswe")
        self.right_frame_subWindow.grid_columnconfigure((0, 1), weight=1)
        self.right_frame_subWindow.grid_rowconfigure((0, 1), weight=0)
        self.right_frame_subWindow.grid_rowconfigure((2), weight=1)

        self.label_modification = customtkinter.CTkLabel(master=self.right_frame_subWindow, 
                                                         text="Modifications", 
                                                         font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_modification.grid(row=0, column=0, sticky="nesw", padx=15, pady=10)
        
        
        # Modification de la masse
        #=======================
        self.mass_modification_frame = customtkinter.CTkFrame(master=self.left_frame_subWindow, width=150)
        self.mass_modification_frame.grid(row=1, padx=10, pady=10, sticky="nwse")
        
        self.label_mass = customtkinter.CTkLabel(master=self.mass_modification_frame,
                                                 text="Masse")
        tl.CreateToolTip(self.label_mass, "Masse du corps (en kg).\nInflue sur sa vitesse et la force que les autres corps exercent sur lui.")
        self.label_mass.grid(row=0, column=0, padx=7, pady=7)
        
        self.mass_var = customtkinter.StringVar()
        self.mass_entry = customtkinter.CTkEntry(master=self.mass_modification_frame, textvariable=self.mass_var)
        self.addContentValidator(self.mass_entry, float)
        self.mass_entry.grid(row=1, column=0, padx=7, pady=7)
        
        
        # Modification de la taille
        #=======================
        self.size_modification_frame = customtkinter.CTkFrame(master=self.left_frame_subWindow, width=150)
        self.size_modification_frame.grid(row=2, padx=10, pady=(0, 10), sticky="nwse")
        
        self.label_size = customtkinter.CTkLabel(master=self.size_modification_frame,
                                                 text="Taille")
        tl.CreateToolTip(self.label_size, "Taille du corps (en pixels).\nPurement esthétique, ne change rien à la simulation")
        self.label_size.grid(row=0, column=0, padx=7, pady=7)
        
        self.size_var = customtkinter.StringVar()
        self.size_entry = customtkinter.CTkEntry(master=self.size_modification_frame, textvariable=self.size_var)
        self.addContentValidator(self.size_entry, int)
        self.size_entry.grid(row=1, column=0, padx=7, pady=7)
        


        # Modification du nom
        #=======================
        self.current_body_name_frame = customtkinter.CTkFrame(master=self.right_frame_subWindow)
        self.current_body_name_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="eswn")
        

        self.label_name = customtkinter.CTkLabel(master=self.current_body_name_frame, 
                                                                font=customtkinter.CTkFont(size=15, weight="bold"), 
                                                                text="Nom")
        tl.CreateToolTip(self.label_name, "Nom du corps.\nAttention, deux corps ne peuvent avoir le même nom !")
        self.label_name.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nw')
        self.name_body_var = customtkinter.StringVar()
        self.name_entry_modification = customtkinter.CTkEntry(master=self.current_body_name_frame, 
                                                              textvariable=self.name_body_var)
        self.name_entry_modification.grid(row=1, column=0, padx=10, pady=(5, 10), sticky='nwes')


        # Modification de la couleur
        #========================
        self.current_body_color_frame = customtkinter.CTkFrame(master=self.right_frame_subWindow)
        self.current_body_color_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="eswn")

        self.current_body_color_label = customtkinter.CTkLabel(master=self.current_body_color_frame, 
                                                    font=customtkinter.CTkFont(size=15, weight="bold"), 
                                                    text="Couleur")
        tl.CreateToolTip( self.current_body_color_label, "Choix de la couleur du corps.")
        self.current_body_color_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nw')
        
        self.pick_color_button = customtkinter.CTkButton(master=self.current_body_color_frame, text="Choisir une couleur",
                                                         command=self.pickAColor)
        self.pick_color_button.grid(row=1, column=0, padx=10, pady=10)
        
        #Opacity slider
        #==============
        self.opacity_var = customtkinter.IntVar()
        self.color_opacity_slider = customtkinter.CTkSlider(master=self.current_body_color_frame, 
                                                            from_=0, to=255, variable=self.opacity_var)
        self.color_opacity_slider.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.color_opacity_label = customtkinter.CTkLabel(master=self.current_body_color_frame,
                                                            font=customtkinter.CTkFont(size=15, weight="bold"),
                                                            text="Opacité")
        tl.CreateToolTip( self.color_opacity_label, "Choix de l'opacité du corps.")
        self.color_opacity_label.grid(row=2, column=0, columnspan=2, padx=(10, 10), pady=5, sticky="w")


        # Modification de la position
        #===========================
        self.current_body_position_frame = customtkinter.CTkFrame(master=self.right_frame_subWindow)
        self.current_body_position_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="eswn")
        
        self.label_starting_position = customtkinter.CTkLabel(master=self.current_body_position_frame, text="Position de départ",
                                                              font=customtkinter.CTkFont(weight="bold"))
        tl.CreateToolTip( self.label_starting_position, "Choix de la position de départ du corps. (en mètres)")
        self.label_starting_position.grid(row=0, column=0, columnspan=2, sticky="ws", padx=15, pady=10)
        
        self.label_position_x = customtkinter.CTkLabel(master=self.current_body_position_frame, text="X :")
        self.label_position_x.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="ws")
        self.label_position_y = customtkinter.CTkLabel(master=self.current_body_position_frame, text="Y :")
        self.label_position_y.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="ws")
        
        self.position_x_var = customtkinter.StringVar()
        self.entry_position_x = customtkinter.CTkEntry(master=self.current_body_position_frame, textvariable=self.position_x_var)
        self.addContentValidator(self.entry_position_x, float)
        self.entry_position_x.grid(row=1, column=1, padx=(5, 10), pady=10)
        
        self.position_y_var = customtkinter.StringVar()
        self.entry_position_y = customtkinter.CTkEntry(master=self.current_body_position_frame, textvariable=self.position_y_var)
        self.addContentValidator(self.entry_position_y, float)
        self.entry_position_y.grid(row=2, column=1, padx=(5, 10), pady=10)


        # Modification de la vitesse
        #===========================
        self.current_body_velocity_frame = customtkinter.CTkFrame(master=self.right_frame_subWindow)
        self.current_body_velocity_frame.grid(row=2, column=2, padx=10, pady=10, sticky="eswn")
        
        self.label_starting_velocity = customtkinter.CTkLabel(master=self.current_body_velocity_frame, text="Velocité de départ", 
                                                              font=customtkinter.CTkFont(weight="bold"))
        tl.CreateToolTip( self.label_starting_velocity, "Choix de la vitesse de départ. (en m/s)")
        self.label_starting_velocity.grid(row=0, column=0, columnspan=2, sticky="ws", padx=15, pady=10)
        
        self.label_velocity_x = customtkinter.CTkLabel(master=self.current_body_velocity_frame, text="X :")
        self.label_velocity_x.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="ws")
        self.label_velocity_y = customtkinter.CTkLabel(master=self.current_body_velocity_frame, text="Y :")
        self.label_velocity_y.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="ws")
        
        self.velocity_x_var = customtkinter.StringVar()
        self.entry_velocity_x = customtkinter.CTkEntry(master=self.current_body_velocity_frame, textvariable=self.velocity_x_var)
        self.addContentValidator(self.entry_velocity_x, float)
        self.entry_velocity_x.grid(row=1, column=1, padx=(5, 10), pady=10)
        
        self.velocity_y_var = customtkinter.StringVar()
        self.entry_velocity_y = customtkinter.CTkEntry(master=self.current_body_velocity_frame, textvariable=self.velocity_y_var)
        self.addContentValidator(self.entry_velocity_y, float)
        self.entry_velocity_y.grid(row=2, column=1, padx=(5, 10), pady=10)
        
        
        # Bouton sauvegarder
        #===========
        self.accept_button_save_changes = customtkinter.CTkButton(self.right_frame_subWindow, text="Sauvegarder",width=60,
                                                                  command=self.saveChangesToBody)
        tl.CreateToolTip(self.accept_button_save_changes, "Sauvegarde les modifications apportées.")
        self.accept_button_save_changes.grid(row=2, column=3, padx=15, pady=15, sticky='es')
        

        #Set variables
        #============
        self.opacity_var.set(self.bodyList[body_index].color[3])
        self.name_body_var.set(name)
        self.velocity_x_var.set(f"{self.bodyList[body_index].velocity.x}")
        self.velocity_y_var.set(f"{self.bodyList[body_index].velocity.y}")
        self.position_x_var.set(f"{self.bodyList[body_index].pos_x}")
        self.position_y_var.set(f"{self.bodyList[body_index].pos_y}")
        self.mass_var.set(f"{self.bodyList[body_index].masse}")
        self.size_var.set(f"{self.bodyList[body_index].size}")
        
        self.body_modification_window.focus_set()
        self.body_modification_window.grab_set()
        
    
    def saveChangesToBody(self):
        """
        Récupère toutes les entrées de l'utilisateur dans la fenêtre de modification du corps et les applique.
        """
        if len(self.bad_values_list) == 0:
            body_index = self.current_body_index
            
            # Formater les changements
            #==============
            v_x=Decimal(self.velocity_x_var.get().replace(',', '.').replace(' ', ''))
            v_y=Decimal(self.velocity_y_var.get().replace(',', '.').replace(' ', ''))
            pos_x=Decimal(self.position_x_var.get().replace(',', '.').replace(' ', ''))
            pos_y=Decimal(self.position_y_var.get().replace(',', '.').replace(' ', ''))
            mass=Decimal(self.mass_var.get().replace(',', '.').replace(' ', ''))
            size=float(self.size_var.get().replace(',', '.').replace(' ', ''))
            
            #Mis à jour des changements
            #==============
            self.bodyList[body_index].name = self.name_body_var.get()
            self.bodyList[body_index].pos_x = pos_x
            self.bodyList[body_index].pos_y = pos_y
            self.bodyList[body_index].velocity.x = v_x
            self.bodyList[body_index].velocity.y = v_y
            self.bodyList[body_index].masse = mass
            self.bodyList[body_index].size = size
            # Changement d'opacité
            r=int(self.bodyList[body_index].color[0])
            g=int(self.bodyList[body_index].color[1])
            b=int(self.bodyList[body_index].color[2])
            new_tuple = (r, g, b, int(self.opacity_var.get()))
            self.bodyList[body_index].color=new_tuple
            
            self.onModificationWindowClose()
        
        else:
            print("Certaines valeurs ne sont pas bonnes !")

    def addContentValidator(self, entry:customtkinter.CTkEntry, type:Union[float, int, bool]):
        """
        Facilite la liaison d'un contentValidator à une entrée.
        """
        entry.bind("<KeyRelease>", lambda x:self.entryContentValidator(entry, type))

    
    def saveTheme(self):
        """
        Sauvegarde les informations du thème dans le fichier 'info.init'.
        """
        text = ''
        for key, value in self.theme.items():
            text = text+key+':'+value+'\n'
        
        
        themePath = os.path.join(self.path, "info.init")
        with open(themePath, 'w') as file:
            file.writelines(text)
            file.close()


    def entryContentValidator(self, entry:customtkinter.CTkEntry, type_:Union[float, int, bool]):
        """
        Permet de modifier dynamiquement la couleur du texte d'une entrée, 
        si l'entrée de l'utilisateur ne correspond pas au type de données attendu. 
        """
        value = entry.get()
        try:
            value = type_(value)
            good_value = True
        except:
            entry.configure(fg_color = "red")
            good_value = False

        if good_value:
            entry.configure(fg_color = customtkinter.ThemeManager.theme["CTkEntry"]["fg_color"])
            try: self.bad_values_list.remove(id(entry))
            except : pass
        else:
            try: self.bad_values_list.remove(id(entry))
            except : pass
            self.bad_values_list.append(id(entry))

    def startSimulation(self):
        """
        Initialise et démarre la simulation avec les paramètres actuels
        """
        self.saveInfoFromPreviewCanvas()
        if sys.platform == "win32":
            gpu_priority_dict = {"Défaut":0, "Efficacité énergétique":1, "Performance":2}
            priority = gpu_priority_dict[self.app_info["gpu_mode"]]
            set_gpu_priority(priority)
        
        
        list_bodys = deepcopy(self.bodyList)
        for body in list_bodys:
            body.CreateSprite()
        WIDTH = self.app_info["width"]
        HEIGHT = self.app_info["height"]
        FULLSCREEN = self.app_info["fullscreen"]
        TIME_MULTIPLIER = self.app_info["time_multiplier"]
        UPDATE_RATE = Decimal(1/self.app_info["reverse_update_rate"])
        ITERATION_MAX = self.app_info["iteration_max"]
        SCALE = self.app_info["scale"] * 10**App.DICO_UNITS[self.app_info["scale_unit"]]
        COMPUTE_RULE = self.app_info["computation_rule"]
        SHOW_MASS_CENTER = self.app_info["show_mass_center"]
        SHOW_AVERAGE_CENTER = self.app_info["show_average_center"]
        SHOW_AXIS = self.app_info["show_axis"]
        MASS_CENTER_COLOR = self.app_info["mass_center_color"]
        AVERAGE_CENTER_COLOR = self.app_info["average_center_color"]
        AXIS_COLOR = self.app_info["axis_color"]
        SHOW_ORBIT = self.app_info["show_orbit"]
        MAX_ORBIT_POINT = self.app_info["max_orbit_point"]
        SHADER_PRESET = self.app_info["shader_preset"]
        
        # Pour le débogage
        print("Trying to start a simulation with the following parameters :")
        print("============================================================")
        print(f"Simulation parameters: ")
        print(f"Screen dimension : {WIDTH}x{HEIGHT}")
        print(f"Is fullscreen : {FULLSCREEN}")
        print(f"Time multiplier : {TIME_MULTIPLIER}")
        print(f"Update rate : {UPDATE_RATE}")
        print(f"Iteration max : {ITERATION_MAX}")
        print(f"Scale : {SCALE}")
        print(f"Compute rule : {COMPUTE_RULE}")
        print(f"Show average center : {SHOW_AVERAGE_CENTER}")
        print(f"Show mass center : {SHOW_MASS_CENTER}")
        print(f"Show axis : {SHOW_AXIS}")
        print(f"Average center color : {AVERAGE_CENTER_COLOR}")
        print(f"Mass center color : {MASS_CENTER_COLOR}")
        print(f"Axis color : {AXIS_COLOR}")
        print(f"Show orbit : {SHOW_ORBIT}")
        print(f"Max orbit point : {MAX_ORBIT_POINT}")
        print(f"Shader preset : {SHADER_PRESET}")

         
        simulation = Simulation(WIDTH, HEIGHT, 
                                list_bodys, 
                                FULLSCREEN, 
                                TIME_MULTIPLIER,
                                UPDATE_RATE, 
                                ITERATION_MAX, 
                                SCALE, 
                                compute_rule=COMPUTE_RULE, 
                                show_average_center=SHOW_AVERAGE_CENTER, 
                                show_mass_center=SHOW_MASS_CENTER,
                                show_axis=SHOW_AXIS,
                                average_center_color=AVERAGE_CENTER_COLOR,
                                mass_center_color=MASS_CENTER_COLOR,
                                axis_color=AXIS_COLOR,
                                show_orbit=SHOW_ORBIT,
                                max_orbit_point=MAX_ORBIT_POINT,
                                shader_preset=SHADER_PRESET)

        self.iconify()
        simulation.setup()
        arcade.run()
        arcade.cleanup_texture_cache()
        arcade.exit()
        simulation = None
        list_bodys = None
        self.reloadProgram()


    def pickAColor(self):
        """
        Ouvre un sélecteur de couleurs et applique la couleur sélectionnée au corps choisi par l'utilisateur.
        """
        index = self.current_body_index

        # Ancienne couleur
        #==============
        r=self.bodyList[index].color[0]
        g=self.bodyList[index].color[1]
        b=self.bodyList[index].color[2]

        colorWindow = CTkColorPicker.AskColor(color=(r, g, b))
        new_color_hex:str = colorWindow.get()
        # Conversion de hex à rgb
        #==================
        new_color = list(int(new_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        self.bodyList[index].color=new_color


    def saveInfoFromPreviewCanvas(self):
        """
        Récupère les infos de position et de vitesse des corps dans le cadre de prévisualisation et met à jour self.bodyList.
        """
        scale = Decimal(self.app_info["scale"] * 10**App.DICO_UNITS[self.app_info["scale_unit"]])
        new_pos_and_velocity = self.previsual_canvas.get_all_positions()
        for body_index in range(len(new_pos_and_velocity)):
            self.bodyList[body_index].pos_x = (new_pos_and_velocity[body_index][0].x - self.width_offset)*scale
            self.bodyList[body_index].pos_y = (new_pos_and_velocity[body_index][0].y - self.height_offset)*-1*scale
            self.bodyList[body_index].velocity.x = new_pos_and_velocity[body_index][1].x *scale 
            self.bodyList[body_index].velocity.y = new_pos_and_velocity[body_index][1].y * -1 *scale 


    def onModificationWindowClose(self):
        """
        Fonction appelée lors de la fermeture de la fenêtre de modification des corps
        """
        
        self.body_modification_window.grab_release()
        self.body_modification_window.destroy()
        self.redrawInterface()
        
        
    def redrawInterface(self):
        """
        Recrée l'interface par défaut.
        """
        self.createMainInterface()


    def addBody(self):
        """
        Ajoute un nouveau corps avec des paramètres par défaut à la liste des corps.
        """
        self.saveInfoFromPreviewCanvas()
        name = f"corp n°{len(self.bodyList) + 1}"
        new_body = deepcopy(Body(name))
        self.bodyList.append(new_body)
        self.redrawInterface()
        self.create_body_modification_window(-1)


    def deleteBody(self):
        """
        Supprime un corps de la liste des corps.
        """
        self.bodyList.pop(self.current_body_index)
        self.onModificationWindowClose()


    def on_closing(self, event=0):
        """
        Ferme la fenêtre et appelle la fonction pour effacer le dossier des sprites.
        """
        self.cleanSpriteFolder()
        self.destroy()
        
        
    def reloadProgram(self):
        """
        Redémarre le programe
        """
        temp_file_path = os.path.join(self.path, "reload.temp")
        with open(temp_file_path, "x") as file:
            file.writelines(self.conf_file_path)
            file.close()
        self.saveConfigurationAs(os.path.join(self.path, "temp.json"))
        self.on_closing()
        os.execv(sys.executable, ['python'] + sys.argv)


    def isAReload(self):
        """
        Vérifie si le programme a été lancé manuellement par l'utilisateur ou s'il a été lancé par le processus de rechargement.
        """
        temp_path = os.path.join(self.path, "reload.temp")
        if os.path.exists(temp_path):
            with open(temp_path, "r") as file:
                self.conf_file_path = file.read()
                file.close()
            os.remove(temp_path)
            return True
        else:
            return False
              
              
    def saveConfigurationAs(self, save_path:str=None):
        """
        Demande à l'utilisateur dans quel fichier il souhaite que la configuration soit enregistrée, puis enregistre la configuration.
        """
        # JSON ne sait pas gérer le type Decimal, il odit donc être converti en float
        if not save_path:
            save_path = filedialog.asksaveasfilename(filetypes=[('Configuration file', '*.json')])
        
        self.saveInfoFromPreviewCanvas()
        app_info_to_save = {}
        for key, value in self.app_info.items():
            if isinstance(value, Decimal):
                value = float(value)
            app_info_to_save[key] = value

        json_conf.saveInfo(save_path, self.bodyList, app_info_to_save)
        
        
    def saveConfiguration(self):
        """
        Enregistre la configuration dans le fichier déjà ouvert.
        """
        # JSON ne sait pas gérer le type Decimal, il odit donc être converti en float
        self.saveInfoFromPreviewCanvas()
        app_info_to_save = {}
        for key, value in self.app_info.items():
            if isinstance(value, Decimal):
                value = float(value)
            app_info_to_save[key] = value
        
        json_conf.saveInfo(self.conf_file_path, self.bodyList, app_info_to_save)
        
    def changeColorTheme(self, theme, color):
        """
        Modifie la couleur et le thème de l'interface
        """
        info_path = os.path.join(self.path, 'info.init')
        with open(info_path, 'w') as file:
            file.write(f"theme:{theme}\n")
            file.write(f"color:{color}")
            file.close()
        
        self.redrawInterface()
    
    def loadthemePreset(self):
        """
        Charge les informations du thème qui sont stockées dans le fichier 'info.init'.
        """
        info_path = os.path.join(self.path, 'info.init')
        with open(info_path, 'r') as file:
            info = file.read().split('\n')
            dict_info = {}
            for char in info:
                char = char.split(':')
                dict_info[char[0]] = char [1]
            file.close()
        self.theme_info = dict_info


def is_admin() -> bool:
    """
    Verifie si python a les privilèges admin
    """
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    return is_admin      

def main(args):
    
    # Verifie l'os.
    # Si le programme est exécuté sous Windows, il demande des privilèges d'administrateur.
    if sys.platform == "win32" and not args.na:
        if is_admin():
            print(f"Executable : {sys.executable}")
            app = App()
            app.mainloop()

        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = App()
        app.mainloop()
        
        
main(args)
