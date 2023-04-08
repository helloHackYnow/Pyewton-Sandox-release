import customtkinter
from copy import deepcopy
import json
import tool_tip as tl
import sys
import CTkColorPicker
from typing import Union
import os

class AppInfoTopWindow(customtkinter.CTkToplevel):
    
    DICO_UNITS = {"e+0":0, "e+3":3, "e+6":6, "e+9":9, "e+12":12, "e+15":15, "e+18":18}

    
    def __init__(self, appInfo:dict):
        """Creates a window that allows the user to edit the simulation parameters with a graphical interface.

        :param appInfo: The dictionnary containing the parameters to edit
        :type appInfo: dict
        """
        super().__init__()
        
        current_dir  = os.path.dirname(os.path.realpath(__file__))
        
        
        if sys.platform == "win32":
            self.after(200, lambda: self.iconbitmap(os.path.join(current_dir, "Icons", "settings.ico")))
        
        
        self.title("Modifier les paramètres")
        self.attributes("-topmost", False)
        self.lift()
        self.after(10)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.appInfo = deepcopy(appInfo)
        
        #Variables
        #=========
        #Liste contenant les variables non-valides
        self.bad_values_list = []
        
        #Récupérer la liste des compute rules
        computation_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "computation_rules", "computation_rules.json")
        with open(computation_path, 'r') as file:
            compute_file = json.load(file)
            file.close()
        self.compute_rule_list = [rule['name'] for rule in compute_file]
        

        #Affichage
        self.width_var                  = customtkinter.StringVar()
        self.height_var                 = customtkinter.StringVar()
        self.fullscreen_var             = customtkinter.BooleanVar()
        self.scale_var                  = customtkinter.StringVar()
        self.scale_unit_var             = customtkinter.StringVar()
        self.gpu_var                    = customtkinter.StringVar()

        #Simulation
        self.computation_rule_var       = customtkinter.StringVar()
        self.reverse_update_rate_var    = customtkinter.StringVar()
        self.time_multiplier_var        = customtkinter.StringVar()
        self.iteration_max_var          = customtkinter.StringVar()
        
        #Markers
        self.show_average_center_var    = customtkinter.BooleanVar()
        self.show_mass_center_var       = customtkinter.BooleanVar()
        self.show_axis_var              = customtkinter.BooleanVar()
        
        #Effects
        self.show_orbit_var             = customtkinter.BooleanVar()
        self.max_orbit_point_var        = customtkinter.StringVar()
        self.shader_preset_var          = customtkinter.StringVar()
        
        #Set variables
        #=============
        self.width_var      .set(str(self.appInfo["width"]))
        self.height_var     .set(str(self.appInfo["height"]))
        self.fullscreen_var .set(bool(self.appInfo["fullscreen"]))
        self.scale_var      .set(str(self.appInfo["scale"]))
        self.scale_unit_var .set(str(self.appInfo["scale_unit"]))
        self.gpu_var        .set(str(self.appInfo["gpu_mode"]))
        
        self.computation_rule_var   .set(self.appInfo["computation_rule"])
        self.reverse_update_rate_var.set(str(self.appInfo["reverse_update_rate"]))
        self.time_multiplier_var    .set(str(self.appInfo["time_multiplier"]))
        self.iteration_max_var      .set(str(self.appInfo["iteration_max"]))
        
        self.show_average_center_var.set(bool(self.appInfo["show_average_center"]))
        self.show_mass_center_var   .set(bool(self.appInfo["show_mass_center"]))
        self.show_axis_var          .set(bool(self.appInfo["show_axis"]))
        
        self.average_center_color = self.appInfo["average_center_color"]
        self.mass_center_color = self.appInfo["mass_center_color"]
        self.axis_color = self.appInfo["axis_color"]
        
        self.show_orbit_var.set(bool(self.appInfo["show_orbit"]))
        self.max_orbit_point_var.set(int(self.appInfo["max_orbit_point"]))
        self.shader_preset_var.set(self.appInfo["shader_preset"])

            
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.appInfoEditTabView = customtkinter.CTkTabview(master=self)
        self.appInfoEditTabView.grid(padx=10, pady=10, sticky="wsen")
        
        self.appInfoEditTabView.add("Affichage")
        self.appInfoEditTabView.add("Simulation")
        self.appInfoEditTabView.add("Marqueurs")
        self.appInfoEditTabView.add("Effets")
        
        #Boutons appliquer et annuler
        self.bottom_frame = customtkinter.CTkFrame(master=self)
        self.bottom_frame.grid(row=1, column=0, sticky="e", padx=10, pady=(0, 10))
        
        self.ok_button = customtkinter.CTkButton(master=self.bottom_frame, text="Appliquer", width=50, command=self._ok_event)
        self.ok_button.grid(column=1, sticky="e")
        
        self.cancel_button = customtkinter.CTkButton(master=self.bottom_frame, text="Annuler", width=50)
        self.cancel_button.grid(row=0,column=0, sticky="e", padx=(0, 5))
        
       



        #============================================================================================================
        #Display parameters
        
        #Frames
        self.appInfoEditTabView.tab("Affichage").grid_columnconfigure(0, weight=1)
        self.display_label_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Affichage"),
                                                          corner_radius=0, 
                                                          fg_color="transparent")
        self.display_entry_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Affichage"),
                                                          corner_radius=0,
                                                          fg_color="transparent")

        self.window_dimension_label_frame = customtkinter.CTkFrame(master=self.display_label_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        self.fullscreen_label_frame = customtkinter.CTkFrame(master=self.display_label_frame,
                                                             corner_radius=0,
                                                             fg_color="transparent")
        self.scale_label_frame = customtkinter.CTkFrame(master=self.display_label_frame, 
                                                        corner_radius=0, 
                                                        fg_color="transparent")
        self.gpu_selecter_label_frame = customtkinter.CTkFrame(master=self.display_label_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")

        self.window_dimension_entry_frame = customtkinter.CTkFrame(master=self.display_entry_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        self.fullscreen_entry_frame = customtkinter.CTkFrame(master=self.display_entry_frame,
                                                             corner_radius=0,
                                                             fg_color="transparent")
        self.scale_entry_frame = customtkinter.CTkFrame(master=self.display_entry_frame, 
                                                        corner_radius=0, 
                                                        fg_color="transparent")
        self.gpu_selecter_entry_frame = customtkinter.CTkFrame(master=self.display_entry_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")
        
        self.display_entry_frame.grid(row=1, column=1, sticky="e", padx = 20)
        self.display_label_frame.grid(row=1, column=0, sticky="w", padx = 10)
        
        self.window_dimension_label_frame.grid(row=1, column=0, sticky="w", pady=5, padx = 10)
        self.fullscreen_label_frame.grid(row=2, column=0, sticky="w", pady=5, padx = 10)
        self.scale_label_frame.grid(row=3, column=0, sticky="w", pady=5, padx = 10)
        self.gpu_selecter_label_frame.grid(row=4, sticky="w", pady=5, padx = 10)
        
        self.window_dimension_entry_frame.grid(row=1, column=0, sticky="e", pady=5, padx = 20)
        self.fullscreen_entry_frame.grid(row=2, column=0, sticky="e", pady=5, padx = 20)
        self.scale_entry_frame.grid(row=3, column=0, sticky="e", pady=5, padx = 20)
        self.gpu_selecter_entry_frame.grid(row=4, column=0, sticky="e", pady=5, padx = 20)


        #Title

        self.window_settings_frame_title = customtkinter.CTkLabel(master=self.appInfoEditTabView.tab("Affichage"), 
                                                      text="Affichage", 
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.window_settings_frame_title.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")


        #Labels

        self.window_dimension_label = customtkinter.CTkLabel(master=self.window_dimension_label_frame,
                                                             text="Resolution :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.window_dimension_label, "Dimensions de la fenêtre de simulation en px.\nEst écrasée par \"plein écran\"")
        self.window_fullscreen_label = customtkinter.CTkLabel(master=self.fullscreen_label_frame,
                                                              text="Plein écran :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.window_fullscreen_label, "Lancer la fenêtre de simulation en plein écran.")
        self.scale_label = customtkinter.CTkLabel(master=self.scale_label_frame,
                                                  text="1 pixel =", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.scale_label, "Définie quelle longueur représente un pixel.")
        self.gpu_selecter_label = customtkinter.CTkLabel(master=self.gpu_selecter_label_frame,
                                                         text="GPU :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.gpu_selecter_label, "Si vous avez deux gpu, permet de selectionner celui utilisé.\nNe fonctionne que sur windows")
        
                
        self.window_dimension_label.grid(row=0, column=0, padx=5)
        self.window_fullscreen_label.grid(row=0, column=0, padx=5)
        self.scale_label.grid(row=0, column=0, padx=5)
        self.gpu_selecter_label.grid(row=0, column=0, padx=5)

        
        
        #Entrys

        self.simulation_windows_height_entry = customtkinter.CTkEntry(master=self.window_dimension_entry_frame,
                                                                      width=50,
                                                                      textvariable=self.height_var)
        self.addContentValidator(self.simulation_windows_height_entry, int)
        self.window_dimension_x_label = customtkinter.CTkLabel(master=self.window_dimension_entry_frame,
                                                               text="x")
        self.simulation_windows_width_entry = customtkinter.CTkEntry(master=self.window_dimension_entry_frame, 
                                                                    width=50,
                                                                    textvariable=self.width_var)
        self.addContentValidator(self.simulation_windows_width_entry, int)
        
        self.fullscreen_checkbox = customtkinter.CTkCheckBox(master=self.fullscreen_entry_frame,
                                                             text="", width=24, 
                                                             variable=self.fullscreen_var)
        
        self.scale_entry = customtkinter.CTkEntry(master=self.scale_entry_frame, width=40, textvariable=self.scale_var)
        self.addContentValidator(self.scale_entry, float)
        unit_list = [key for key in AppInfoTopWindow.DICO_UNITS.keys()]
        self.scale_unit_optionmenu = customtkinter.CTkOptionMenu(master=self.scale_entry_frame,
                                                                 dynamic_resizing=True, values=unit_list,
                                                                 width=70, variable=self.scale_unit_var)
        self.scale_m_label = customtkinter.CTkLabel(master=self.scale_entry_frame,
                                                    text="m")
        tl.CreateToolTip(self.scale_m_label, "Exprimé en mètres")

        self.gpu_selecter_optionmenu = customtkinter.CTkOptionMenu(master=self.gpu_selecter_entry_frame,
                                                                   dynamic_resizing=True,
                                                                   values=["Défaut", "Efficacité énergétique", "Performance"],
                                                                   variable=self.gpu_var)
        
        self.simulation_windows_width_entry.grid(row=0, column=0)
        self.window_dimension_x_label.grid(row=0, column=1, padx=2)
        self.simulation_windows_height_entry.grid(row=0, column=2)
    
        self.fullscreen_checkbox.grid(row=0, column=0)

        self.scale_entry.grid(row=0, column=0)
        self.scale_unit_optionmenu.grid(row=0, column=1, padx=5)
        self.scale_m_label.grid(row=0, column=2, sticky="e")

        self.gpu_selecter_optionmenu.grid(padx=5)
        os_used = sys.platform
        if os_used != "win32":
            self.gpu_selecter_optionmenu.configure(state="disabled")
        




        #============================================================================================================
        #Simulation
        
        
        #Frames

        self.appInfoEditTabView.tab("Simulation").grid_columnconfigure(0, weight=1)
        
        self.simulation_label_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Simulation"),
                                                          corner_radius=0, 
                                                          fg_color="transparent")
        self.simulation_entry_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Simulation"),
                                                          corner_radius=0,
                                                          fg_color="transparent")
        
        self.time_multiplier_label_frame = customtkinter.CTkFrame(master=self.simulation_label_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        self.reverse_update_rate_label_frame = customtkinter.CTkFrame(master=self.simulation_label_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        self.iteration_max_label_frame = customtkinter.CTkFrame(master=self.simulation_label_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        self.computation_rule_label_frame = customtkinter.CTkFrame(master=self.simulation_label_frame, 
                                                                   corner_radius=0, 
                                                                   fg_color="transparent")
        
        self.time_multiplier_entry_frame = customtkinter.CTkFrame(master=self.simulation_entry_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")
        self.reverse_update_rate_entry_frame = customtkinter.CTkFrame(master=self.simulation_entry_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")
        self.iteration_max_entry_frame = customtkinter.CTkFrame(master=self.simulation_entry_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")
        self.computation_rule_optionmenu_frame = customtkinter.CTkFrame(master=self.simulation_entry_frame,
                                                               corner_radius=0,
                                                               fg_color="transparent")
        
        self.simulation_entry_frame.grid(row=1, column=1, sticky="e", padx = 20)
        self.simulation_label_frame.grid(row=1, column=0, sticky="w", padx = 10)

        self.time_multiplier_label_frame.grid(row=1, column=0, sticky="w", pady=5, padx = 10)
        self.reverse_update_rate_label_frame.grid(row=2, column=0, sticky="w", pady=5, padx = 10)
        self.iteration_max_label_frame.grid(row=3, column=0, sticky="w", pady=5, padx = 10)
        self.computation_rule_label_frame.grid(row=4, column=0, sticky="w", pady=5, padx = 10)

        self.time_multiplier_entry_frame.grid(row=1, column=0, sticky="e", pady=5, padx = 20)
        self.reverse_update_rate_entry_frame.grid(row=2, column=0, sticky="e", pady=5, padx = 20)
        self.iteration_max_entry_frame.grid(row=3, column=0, sticky="e", pady=5, padx = 20)
        self.computation_rule_optionmenu_frame.grid(row=4, column=0, sticky="e", pady=5, padx = 20)
        

        #Title

        self.simulation_settings_frame_title = customtkinter.CTkLabel(master=self.appInfoEditTabView.tab("Simulation"), 
                                                      text="Simulation", 
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.simulation_settings_frame_title.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")
        
        
        #Labels

        self.time_multiplier_label = customtkinter.CTkLabel(master=self.time_multiplier_label_frame,
                                                            text="Multiplicateur temporel :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.time_multiplier_label, "Nombre cible de secondes de simulation par secondes réelles.\nUn processeur peu perfomant peut avoir des difficultés\nà satisfaire cette cible si elle est élevée et que le nombre\nd'iterations par secondes de simulation l'est aussi.")
        
        self.reverse_update_rate_label = customtkinter.CTkLabel(master=self.reverse_update_rate_label_frame,
                                                                text="Iterations par ut :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.reverse_update_rate_label, "Nombre de fois les positions des corps sont recalculés chaques secondes de simulation.")
        
        self.iteration_max_label = customtkinter.CTkLabel(master=self.iteration_max_label_frame,
                                                                text="Iterations max :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.iteration_max_label, "Nombre d'iterations de calcul après lequel la simulation s'arrête.\nFixé à -1, la simulation continue indéfiniment.")
        
        self.computation_rule_label = customtkinter.CTkLabel(master=self.computation_rule_label_frame,
                                                                text="Type de simulation :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.computation_rule_label, "Règle de calcul appliqué pour la simulation")
                
        self.computation_rule_label.grid(row=0, sticky="w")
        self.reverse_update_rate_label.grid(row=1, sticky="w")
        self.time_multiplier_label.grid(row=2, sticky="w")
        self.iteration_max_label.grid(row=3, sticky="w")
        
        
        #Entrys
        
        self.time_multiplier_entry = customtkinter.CTkEntry(master=self.time_multiplier_entry_frame,
                                                            width=100, textvariable=self.time_multiplier_var)
        self.addContentValidator(self.time_multiplier_entry, float)
        
        self.reverse_update_rate_entry = customtkinter.CTkEntry(master=self.reverse_update_rate_entry_frame,
                                                                width=100, textvariable=self.reverse_update_rate_var)
        self.addContentValidator(self.reverse_update_rate_entry, float)
        
        self.iteration_max_entry = customtkinter.CTkEntry(master=self.iteration_max_entry_frame,
                                                          width=100, textvariable=self.iteration_max_var)
        self.addContentValidator(self.iteration_max_entry, int)

        self.computation_rule_optionmenu = customtkinter.CTkOptionMenu(master=self.computation_rule_optionmenu_frame,
                                                            dynamic_resizing=True,
                                                            values = self.compute_rule_list,
                                                            variable=self.computation_rule_var)
        
        self.computation_rule_optionmenu.grid(row=0, sticky="e")
        self.reverse_update_rate_entry.grid(row=1, sticky="e")
        self.time_multiplier_entry.grid(row=2, sticky="e")
        self.iteration_max_entry.grid(row=3, sticky="e")
        
        
        


        #============================================================================================================
        #Marqueurs

        self.appInfoEditTabView.tab("Marqueurs").grid_columnconfigure(0, weight=1)


        #Frames

        self.marker_label_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Marqueurs"),
                                                          corner_radius=0, 
                                                          fg_color="transparent")
        
        self.marker_entry_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Marqueurs"),
                                                          corner_radius=0,
                                                          fg_color="transparent")
        
        
        self.average_center_label_frame = customtkinter.CTkFrame(master=self.marker_label_frame,
                                                                 corner_radius=0,
                                                                 fg_color="transparent")
        
        self.mass_center_label_frame = customtkinter.CTkFrame(master=self.marker_label_frame,
                                                              corner_radius=0,
                                                              fg_color="transparent")
        
        self.axis_label_frame = customtkinter.CTkFrame(master=self.marker_label_frame,
                                                       corner_radius=0,
                                                       fg_color="transparent")
        
        self.average_center_entry_frame = customtkinter.CTkFrame(master=self.marker_entry_frame,
                                                                 corner_radius=0,
                                                                 fg_color="transparent")
        self.mass_center_entry_frame = customtkinter.CTkFrame(master=self.marker_entry_frame,
                                                              corner_radius=0,
                                                              fg_color="transparent")
        self.axis_entry_frame = customtkinter.CTkFrame(master=self.marker_entry_frame,
                                                       corner_radius=0, 
                                                       fg_color="transparent")
        
        self.marker_label_frame.grid(row=1, sticky="w", padx = 10)
        self.average_center_label_frame.grid(row=0,column=0, pady=5, sticky="w", padx = 10)
        self.mass_center_label_frame.grid(row=1,column=0, pady=5, sticky="w", padx = 10)
        self.axis_label_frame.grid(row=2,column=0, pady=5, sticky="w", padx = 10)
        
        self.marker_entry_frame.grid(row=1, column=1, sticky="e", padx = 20)
        self.average_center_entry_frame.grid(sticky="e", pady=5, padx = 20)
        self.mass_center_entry_frame.grid(row=1, sticky="e", pady=5, padx = 20)
        self.axis_entry_frame.grid(row=2, sticky="e", pady=5, padx = 20)
        

        #Title

        self.marker_frame_title = customtkinter.CTkLabel(master=self.appInfoEditTabView.tab("Marqueurs"), 
                                                      text="Marqueurs", 
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.marker_frame_title.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")
        

        #Labels
        
        self.show_average_center_label = customtkinter.CTkLabel(master=self.average_center_label_frame,
                                                                text="Centre moyen :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.show_average_center_label, "Permet d'afficher la position moyenne des corps")
        
        self.show_mass_center_label = customtkinter.CTkLabel(master=self.mass_center_label_frame,
                                                             text="Centre de masse :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.show_mass_center_label, "Permet d'afficher le centre de masse du système")

        self.show_axis_label = customtkinter.CTkLabel(master=self.axis_label_frame,
                                                      text="Axes :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.show_axis_label, "Permet d'afficher les axes d'abscisse et d'ordonnée")

        self.show_average_center_label.grid(sticky="w")
        self.show_mass_center_label.grid(sticky="w")
        self.show_axis_label.grid(sticky="w")
        
        
        #Entrys
        
        self.average_center_color_indicator = customtkinter.CTkLabel(master=self.average_center_label_frame,
                                                                    text="", fg_color="#ffffff", width=20,
                                                                    height=20, corner_radius=10)
        self.mass_center_color_indicator = customtkinter.CTkLabel(master=self.mass_center_label_frame,
                                                                    text="", fg_color="#ffffff", width=20,
                                                                    height=20, corner_radius=10)
        self.axis_color_indicator = customtkinter.CTkLabel(master=self.axis_label_frame,
                                                                    text="", fg_color="#ffffff",
                                                                    height=20, width=20, corner_radius=10)
        
        self.show_average_center_checkbox = customtkinter.CTkCheckBox(master=self.average_center_entry_frame,
                                                                    width=24,
                                                                    text="", variable=self.show_average_center_var)
        self.show_mass_center_checkbox = customtkinter.CTkCheckBox(master=self.mass_center_entry_frame,
                                                                    width=24,
                                                                    text="", variable=self.show_mass_center_var)
        self.show_axis_checkbox = customtkinter.CTkCheckBox(master=self.axis_entry_frame,
                                                                    text="", width=24,
                                                                    variable=self.show_axis_var)
        
        self.axis_color_button = customtkinter.CTkButton(master=self.axis_entry_frame,
                                                                    text="couleur",
                                                                    width=50,
                                                                    command=lambda x="axis_color":self.selectColor(x))
        self.mass_center_color_button = customtkinter.CTkButton(master=self.mass_center_entry_frame,
                                                                    text="couleur",
                                                                    width=50,
                                                                    command=lambda x="mass_center_color":self.selectColor(x))
        self.average_center_color_button = customtkinter.CTkButton(master=self.average_center_entry_frame,
                                                                    text="couleur",
                                                                    width=50,
                                                                    command=lambda x="average_center_color":self.selectColor(x))
        
        self.average_center_color_indicator.grid(column=1, row=0, padx=5)
        self.mass_center_color_indicator.grid(column=1, row=0, padx=5)
        self.axis_color_indicator.grid(row=0, column=1, padx=5)

        self.show_average_center_checkbox.grid(row=0, column=0)
        self.show_mass_center_checkbox.grid(row=0, column=0)
        self.show_axis_checkbox.grid(row=0, column=0)

        self.average_center_color_button.grid(row=0, column=1)
        self.mass_center_color_button.grid(row=0, column=1)
        self.axis_color_button.grid(row=0, column=1)





        #============================================================================================================
        #Effets

        self.appInfoEditTabView.tab("Effets").grid_columnconfigure(0, weight=1)


        #Frames

        self.effects_label_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Effets"),
                                                          corner_radius=0, 
                                                          fg_color="transparent")
        self.effects_entry_frame = customtkinter.CTkFrame(master=self.appInfoEditTabView.tab("Effets"),
                                                          corner_radius=0,
                                                          fg_color="transparent")
        
        self.show_orbit_label_frame = customtkinter.CTkFrame(master=self.effects_label_frame,
                                                             corner_radius=0,
                                                             fg_color="transparent")
        self.max_orbit_point_label_frame = customtkinter.CTkFrame(master=self.effects_label_frame,
                                                                            corner_radius=0,
                                                                            fg_color="transparent")
        self.shader_label_frame = customtkinter.CTkFrame(master=self.effects_label_frame,
                                                         corner_radius=0, 
                                                         fg_color="transparent")
        

        self.show_orbit_entry_frame = customtkinter.CTkFrame(master=self.effects_entry_frame,
                                                             corner_radius=0,
                                                             fg_color="transparent")
        self.max_orbit_point_entry_frame = customtkinter.CTkFrame(master=self.effects_entry_frame,
                                                                            corner_radius=0,
                                                                            fg_color="transparent")
        self.shader_optionmenu_frame = customtkinter.CTkFrame(master=self.effects_entry_frame,
                                                              corner_radius=0,
                                                              fg_color="transparent")
        self.shader_optionmenu = customtkinter.CTkOptionMenu(master=self.shader_optionmenu_frame,
                                                             values=["Epuré", "Beau", "Magnifique", "Performance killer"],
                                                             variable=self.shader_preset_var)
        
        self.effects_label_frame.grid(row=1, sticky="w", padx = 10)
        self.effects_entry_frame.grid(row=1, column=1, sticky="e", padx = 20)
        
        self.show_orbit_label_frame.grid(row=0, column=0, sticky="w", pady=5, padx = 10)
        self.max_orbit_point_label_frame.grid(sticky="w", pady=5, padx = 10)
        self.shader_label_frame.grid(row=2, column=0, sticky="w", padx = 10)

        self.show_orbit_entry_frame.grid(row = 0, sticky ="e", padx = 20 )
        self.max_orbit_point_entry_frame.grid(sticky="e", pady=5, padx = 20)
        self.shader_optionmenu_frame.grid(row=2, column=0, padx = 20)

        
        #Title

        self.effects_frame_title = customtkinter.CTkLabel(master=self.appInfoEditTabView.tab("Effets"), 
                                                      text="Effets", 
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.effects_frame_title.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")
        

        #Labels

        self.show_orbit_label = customtkinter.CTkLabel(master=self.show_orbit_label_frame,
                                                       text="Orbites :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.show_orbit_label, "Permet d'afficher les orbites des corps.")
        
        self.max_orbit_point_label = customtkinter.CTkLabel(master=self.max_orbit_point_label_frame,
                                                                      text="Particules d'orbite :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.max_orbit_point_label, "Nombres maximum de positions d'orbite affichées en même temps.\nUn nombre trop élevé peut affecter significativement les performances,\nspécifiquement lors des zooms / dé-zooms.")
        
        self.shader_label = customtkinter.CTkLabel(master=self.shader_label_frame,
                                                   text="Arrière-plan :", font=customtkinter.CTkFont(size=15))
        tl.CreateToolTip(self.shader_label, "Défini le nivau de graphismedes shaders.")
        
        self.show_orbit_label.grid()
        self.max_orbit_point_label.grid() 
        self.shader_label.grid(sticky="w")
        

        #Entrys

        self.show_orbit_checkbox = customtkinter.CTkCheckBox(master=self.show_orbit_entry_frame, text="", width=24, variable=self.show_orbit_var)
        
        self.max_orbit_point_entry =customtkinter.CTkEntry(master=self.max_orbit_point_entry_frame, textvariable=self.max_orbit_point_var) 
        self.addContentValidator(self.max_orbit_point_entry, int)

        self.shader_optionmenu = customtkinter.CTkOptionMenu(master=self.shader_optionmenu_frame,
                                                             values=["Epuré", "Beau", "Magnifique", "Pyewton Gigachad"],
                                                             variable=self.shader_preset_var)
        
        self.show_orbit_checkbox.grid(sticky="e")
        self.max_orbit_point_entry.grid()
        self.shader_optionmenu.grid(sticky="e")
        
        self.focus_set()
        self.grab_set()
        
        self.updateColor()




    def addContentValidator(self, entry:customtkinter.CTkEntry, type:Union[float, int, bool]):
        """Makes it easy to bind a contentValidator to a entry

        :param entry: The widget whose content is to be checked
        :type entry: customtkinter.CTkEntry
        :param type: Data type the value should matchs
        :type type: Union[float, int, bool]
        """
        
        entry.bind("<KeyRelease>", lambda x:self.entryContentValidator(entry, type))
    
    
    def entryContentValidator(self, entry:customtkinter.CTkEntry, type_:Union[float, int, bool]):
        """Allows to change the color of an input dynamically, if the user input does not match
        the expected data type.

        :param entry: The widget whose content is to be checked
        :type entry: customtkinter.CTkEntry
        :param type_: Data type the value should matchs
        :type type_: Union[float, int, bool]
        """
        value = entry.get()
        try:
            new_value = type_(value)
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
            
    
    def selectColor(self, key:str):
        """Opens a color picker and sets self.appInfo[key] to the selected color.

        :param key: the key to update in self.appInfo
        :type key: str
        """
        color = CTkColorPicker.AskColor().get()
        if not color == None:
            self.appInfo[key] = color
        
        self.updateColor()

    def updateColor(self):
        """Updates the color of the color indicators.
        """
        mass_center_color = self.appInfo["mass_center_color"]
        average_center_color = self.appInfo["average_center_color"]
        axis_color = self.appInfo["axis_color"]

        self.mass_center_color_indicator.configure(fg_color=mass_center_color)
        self.average_center_color_indicator.configure(fg_color=average_center_color)
        self.axis_color_indicator.configure(fg_color=axis_color)
        
    def _ok_event(self):
        """This function is called whenever the "apply" button is pressed.\n
        Update self.appInfo with the values of all the fields then destroy the window, wich returns self.appInfo.\n
        If one of the value isn't valid (the field is red), it prints a message in the console.
        """
        if len(self.bad_values_list) == 0:
            self.appInfo["width"]               = int(self.width_var.get())
            self.appInfo["height"]              = int(self.height_var.get())
            self.appInfo["fullscreen"]          = self.fullscreen_var.get()
            self.appInfo["scale"]               = float(self.scale_var.get())
            self.appInfo["scale_unit"]          = self.scale_unit_var.get()
            self.appInfo["gpu_mode"]            = self.gpu_var.get()
            self.appInfo["computation_rule"]    = self.computation_rule_var.get()
            self.appInfo["reverse_update_rate"] = float(self.reverse_update_rate_var.get())
            self.appInfo["time_multiplier"]     = float(self.time_multiplier_var.get())
            self.appInfo["iteration_max"]       = int(self.iteration_max_var.get())
            self.appInfo["show_average_center"] = self.show_average_center_var.get()
            self.appInfo["show_mass_center"]    = self.show_mass_center_var.get()
            self.appInfo["show_axis"]           = self.show_axis_var.get()
            self.appInfo["show_orbit"]          = self.show_orbit_var.get()
            self.appInfo["max_orbit_point"]     = int(self.max_orbit_point_var.get())
            self.appInfo["shader_preset"]       = self.shader_preset_var.get()
            
            self.grab_release()
            self.destroy()

        else:
            print("Entrée(s) invalide(s), ne peut pas fermer !")
            
    def _on_closing(self):
        """This function is called whenever the cross button on the title bar is pressed.
        """
        self.grab_release()
        self.destroy()
    
    def get(self) -> dict:
        """When called, this function waits for the window to be destroy, then returns an updated appInfo dictionnary.

        :return: a dict containing all the simulation parameters
        :rtype: dict
        """
        self.master.wait_window(self)
        return self.appInfo