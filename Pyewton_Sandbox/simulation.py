import math
import os
import arcade
from arcade.experimental import Shadertoy
from math import sqrt
from Vecteur2D import Vecteur2D
from time import time
from typing import Union
from importlib import import_module
from decimal import Decimal
from Body import Body
from computation_rules import generate_computation_file

def hex_to_rgb(hex:str) -> "tuple[int]":
    return tuple(int(hex.replace("#", "")[i:i+2], 16) for i in (0, 2, 4))


# GLSL code for the background shader
# The code was inspired by this one : https://api.arcade.academy/en/latest/tutorials/shader_toy_particles/index.html
# It was however heavely modified to solve performance issues and to match our specific needs
bg_shader =    """uniform vec2 offset;
                    uniform bool show_axis;
                    uniform vec3 axis_color;
                    uniform int star_count = 300;
                    uniform int volume_steps = 10;
                    const vec3 color = vec3(1.0, 1.0, 0.8);
                    const float DEFAULT_BRIGHTNESS = 0.003;
                    const float TWINKLE_SPEED = 0.9;


                    vec2 RandVec2(float t) {
                    float x = sin(t*89.3) * 937.6;
                    float y = mod(t*x, 9.62);
                    return vec2(x, y);
                    }



                    void mainImage(out vec4 fragColor, in vec2 fragCoord) {

                        // On normalise les coordonées du pixel (de 0 à 1)                        
                        float rapport = 0.0;
                        rapport += iResolution.x/iResolution.y;

                        vec2 uv = fragCoord/iResolution.xy;
                        uv.x *= rapport;
                        vec2 noffset = offset/iResolution.xy;

                        float alpha = 0.0;

                        // On boucle sur chaque layer
                        for(float f= 1.0; f < volume_steps+1; f++){
                            
                            // Boucle sur chaque étoiles du layer
                            for(float i= 0.; i < star_count / volume_steps; i++){

                                float seed = i + f*0.0001;

                                vec2 star_pos = RandVec2(seed);
                                
                                star_pos += (noffset / (f * 0.5));
                                star_pos.x = mod(star_pos.x * rapport, rapport);
                                star_pos.y = mod(star_pos.y, 1);

                                float d = length(uv - star_pos);
                                if(d<0.5){
                                    float t = 1.0/ d;
                                    t *= 0.2;
                                    t = pow(t, 1.2);
                                    float brightness = DEFAULT_BRIGHTNESS * (sin((iTime + i*f) / TWINKLE_SPEED) + 1);

                                    alpha += brightness * t / f;
                                }

                                
                            }
                            
                        }

                        vec3 color = color * alpha;
                        color = 1.0 - exp(-color);
                        
                        
                        // Affichage des lignes de repère
                        if(show_axis){
                            vec2 offseted_fragCoord = fragCoord - offset;

                            if(int(offseted_fragCoord.x) == 0){
                                color = axis_color;
                            }
                            else if(int(offseted_fragCoord.y)==0){
                                color = axis_color;
                            }
                        }
                        // Output
                        fragColor = vec4(color, 1.0);
                        
                    }"""
                    

 
 

class Simulation(arcade.Window):
    
    MAX_ZOOM_INDICATOR_LENTGH = 200 #max length of the zoom indicator (in px)
    MIN_ZOOM_INDICATOR_LENTGH = 100 #min length of the zoom indicator (in px)
    
    time_dict = {"s":1, "min":60, "h":60, "j":24, "ans":Decimal(365.25)}
    
    shader_parameters_list = {"Epuré":(0, 0), "Beau":(100, 5), "Magnifique":(300, 15), "Performance killer":(600, 30)}
    
    def __init__(self, 
                 width:int,               
                 height:int, 
                 bodyList: "list[Body]", 
                 fullscreen:bool=False, 
                 time_multiplier:Decimal=1, 
                 update_rate:Decimal=1/120, 
                 iteration_max:int=-1, 
                 
                 scale:Decimal=1, 
                 
                 show_mass_center:bool=True, 
                 show_average_center:bool=True,
                 show_axis:bool=True,
                 mass_center_color:str="#ffffff",
                 average_center_color:str="#ffffff",
                 axis_color:str="#ffffff",
                 
                 compute_rule:str="Sans distance",
                 gpu_mode:int=0,
                 show_orbit:bool=False,
                 max_orbit_point:int=10000,
                 shader_preset:str="Performance killer"):
        """Initialize the simulation class

        Arguments:
            :width -- Largeur (en pixels) de la fenêtre  
            :height -- Hauteur (en pixels) de la fenêtre  
            :bodyList -- Liste contenant toutes les instances des planètes de la simulation  

        Keyword Arguments:
            fullscreen -- Configure la fenêtre en plein écran (default: {False})
            time_multiplier -- Nombre de secondes simulations par secondes réelles (default: {1})
            update_rate -- Inverse du nombre d'itérations de calcul par secondes simulation (default: {1/120})
            iteration_max -- Nombre d'itérations de calcul après lequel la simulation s'arrète (default: {-1})
            scale -- _description_ (default: {1})
            show_mass_center -- _description_ (default: {True})
            show_average_center -- _description_ (default: {True})
            show_axis -- _description_ (default: {True})
            mass_center_color -- _description_ (default: {"#ffffff"})
            average_center_color -- _description_ (default: {"#ffffff"})
            axis_color -- _description_ (default: {"#ffffff"})
            compute_rule -- _description_ (default: {"No distance"})
            gpu_mode -- _description_ (default: {0})
        """
    
        #Initialisation de la fenêtre
        super().__init__(width, height, resizable=False)
        
        #Assignation of different values   
        if fullscreen:
            arcade.Window.set_fullscreen(self)
        else:
            self.height = height
            self.width = width 
        
        #Camera's creation
        self.camera_bodys = arcade.Camera(self.width, self.height)
        self.camera_background = arcade.Camera(self.width, self.height)
        
            
        self.path = os.path.dirname(os.path.realpath(__file__))                                                            
        self.bodyList = bodyList
        self.time_multiplier = Decimal(time_multiplier)
        self.iteration = 0
        self.iteration_max = iteration_max
        self.scale = Decimal(scale)
        self.spriteOffset = Vecteur2D(0, 0)
        self.ratio = Decimal(self.width / self.height)
        self.compute_rule = compute_rule
        self.time = Decimal(0.0)
        self.zoom_indicator_parameter = Decimal(150) * self.scale
        self.zoom_increasing = False
        self.zoom_decreasing = False
        self.body_scale = self.scale
        self.update_rate = Decimal(update_rate)
        self.show_mass_center = show_mass_center
        self.show_average_center = show_average_center
        self.show_axis = show_axis
        self.mass_center_color = mass_center_color
        self.average_center_color = average_center_color
        self.show_orbit = show_orbit
        self.max_orbit_point = max_orbit_point
        self.shader_preset = shader_preset
        self.tmp_trigo = []
        self.tmp_autre = []
        
        #Conversion d'axis_color en un tuple (255, 255, 255)
        if type(axis_color) == str:
            self.axis_color = hex_to_rgb(axis_color)
        else:
            self.axis_color = axis_color
            
        self.on_stop = False
        if self.show_orbit:
            self.orbit_points_SpriteList = arcade.SpriteList()
            self.orbit_points_list = []
            
        self.vector_force_list = []
        self.mouse_coord = 0, 0
        self.index_body_selected = None
        self.body_on_focus = None
        self.last_click_time = 0
        self.last_click_coord = (0, 0)
        self.text_time = "0 s"
        self.vectors_scale = 1
        
        #Compute rule
        #Regénérer les scripts de calcul de norme
        generate_computation_file.generate_code(os.path.join(self.path, 'computation_rules', 'computation_rules.json'))
        
        script_path = "computation_rules."+self.compute_rule.replace(" ", "_")
        try:
            self.calcul_norme = import_module(script_path)
        except Exception as e:
            print("Error while load the compute script !")
            print(e)
            quit()
        
        self.scale_as_changed = True

        

    def setup(self):
        """
        Set the parameters before starting the simulation
        """ 
        #Background color
        arcade.set_background_color(arcade.color.BLACK)
        
        #Modify the update rate
        self.set_update_rate(float(self.update_rate /self.time_multiplier))

        #Fixing a delta time
        self.delta_time = Decimal(self.update_rate)
        
        self.simulation_time = 0
            
        #Sprites list creation
        self.spriteList = arcade.SpriteList()
        
        #Centring the simulation
        self.spriteOffset.x = self.width / 2
        self.spriteOffset.y = self.height / 2
                
        #Creation and set of the camera which monitor the bodys show
        
        self.camera_bodys.move((-self.spriteOffset.x, -self.spriteOffset.y))

        #Creation and set of the camera which monitor the background show
        
        #self.camera_background.move((-self.spriteOffset.x, -self.spriteOffset.y))
        
        #Creation of camera for scale indicator scale
        self.ui_camera = arcade.Camera(self.width, self.height)
        
        #Center mass sprite initialization 
        if self.show_mass_center:
            self.mass_centerSprite = arcade.SpriteCircle(10, self.mass_center_color)
        #whole system mass
        self.total_masse = 0
        for body in self.bodyList:
            self.total_masse+=body.masse
        
        #Average's center mass sprite's initialization
        if self.show_average_center:
            self.center_sprite = arcade.SpriteCircle(10, self.average_center_color)
            
        #Shaders
        shader_parameters_list = {"Epuré":(0, 0), "Beau":(100, 5), "Magnifique":(300, 15)} #keys : name of the preset, value : (star_count, volume_steps)
        
        self.background_shader = Shadertoy(size=self.get_size(),
                                   main_source=bg_shader)
        self.background_shader.program['show_axis'] = self.show_axis
        self.background_shader.program['axis_color'] = self.axis_color[0] / 255, self.axis_color[1] / 255, self.axis_color[2] / 255
        self.background_shader.program['star_count'] = Simulation.shader_parameters_list[self.shader_preset][0]
        self.background_shader.program['volume_steps'] = Simulation.shader_parameters_list[self.shader_preset][1]
        
        

        #Instantiating the positioning of the bodys
        for body in self.bodyList:
            body_sprite = arcade.Sprite(body.spritePath)
            body_sprite.center_x = float(body.pos_x * self.scale)
            body_sprite.center_y = float(body.pos_y * self.scale)
            self.spriteList.append(body_sprite)
        
        self.updateScaleIndicator()
        self.updateSpriteScale()

    
    def on_draw(self):
        """
        Function called every frame to calculate the image
        (built-in function of the arcade module)
        """
        # Update the sprite position
        #============================
        indexPlanet = 0
        for sprite in self.spriteList:
            # Set the sprite's x and y position to the corresponding body's x and y position
            # multiplied by the scale
            sprite.center_x = float((self.bodyList[indexPlanet].pos_x) / self.scale)
            sprite.center_y = float((self.bodyList[indexPlanet].pos_y) / self.scale)
            # Increment the index to move to the next body in the list
            indexPlanet += 1

        self.clear()
        # Clear the screen and draw the sprites
        self.camera_background.use()
        # Mettre à jour les uniforms dans le shader
        self.background_shader.program['offset'] = Decimal(self.spriteOffset.x), Decimal(self.spriteOffset.y)
        #print(f"Scale : {self.scale}")

        # Run the GLSL code
        self.background_shader.render(time=self.time)
        
        #Update the body's scale
        if self.zoom_increasing == True or self.zoom_decreasing == True :
            self.updateSpriteScale()
        
        self.camera_bodys.use()
        self.spriteList.draw()
        
        if self.show_orbit:
            
            i=0
            if self.scale_as_changed and not (self.zoom_increasing or self.zoom_decreasing):
                for i in range(len(self.orbit_points_list)):
                    self.orbit_points_SpriteList[i].center_x = self.orbit_points_list[i][0] / self.scale
                    self.orbit_points_SpriteList[i].center_y = self.orbit_points_list[i][1] / self.scale
                    i+=1
                self.scale_as_changed = False
            if not (self.zoom_increasing or self.zoom_decreasing):
                self.orbit_points_SpriteList.draw()
        
        
        #Draw the force vectors applied to the selected body 
        self.drawForceVector()
        
        # Draw the mass center and center sprites if the corresponding flags are set
        if self.show_mass_center:
            self.mass_centerSprite.draw()
        if self.show_average_center:
            self.center_sprite.draw()

        
        self.ui_camera.use()
        self.updateScaleIndicator()       
        
        arcade.draw_text(self.zoom_indicator_text, float(self.scale_indicator_end.x), float(self.scale_indicator_end.y -20))

        #Main indicator line
        arcade.draw_line(self.scale_indicator_start.x, self.scale_indicator_start.y, self.scale_indicator_end.x, self.scale_indicator_end.y, arcade.color.WHITE, 2)
              
        #Mid vertical separator
        arcade.draw_line((self.scale_indicator_end.x+self.scale_indicator_start.x)/2, self.scale_indicator_start.y+6,
                         (self.scale_indicator_end.x+self.scale_indicator_start.x)/2, self.scale_indicator_start.y, arcade.color.WHITE, 1)
        
        #First vertical separator
        arcade.draw_line(self.scale_indicator_start.x, self.scale_indicator_start.y,
                         self.scale_indicator_start.x, self.scale_indicator_start.y+10, color=arcade.color.WHITE, line_width=2)
        
        #Last vertical separator
        arcade.draw_line(self.scale_indicator_end.x, self.scale_indicator_end.y,
                         self.scale_indicator_end.x, self.scale_indicator_end.y+10, color=arcade.color.WHITE, line_width=2)
        
        
        self.updateTimeText()
        arcade.draw_text(self.text_time, self.width - 100, self.height - 50)
        

        

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        """
        Function called when the mouse is dragged.
        (built-in function of the arcade module)

        Parameters:
            x (int): The current x-coordinate of the mouse.
            y (int): The current y-coordinate of the mouse.
            dx (int): The change in x-coordinate of the mouse.
            dy (int): The change in y-coordinate of the mouse.
            buttons (int): An integer representing the buttons that are pressed.
            modifiers (int): An integer representing any keyboard modifiers that are pressed.
        """
        # Update the sprite offset by the change in x and y position of the mouse
        self.spriteOffset.x += dx
        self.spriteOffset.y += dy
        # Move the camera by the opposite of the sprite offset
        self.camera_bodys.move((-self.spriteOffset.x, -self.spriteOffset.y))


    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """
        Function called when the mouse is moved.
        (built-in function of the arcade module)

        Parameters:
            x (int): The current x-coordinate of the mouse.
            y (int): The current y-coordinate of the mouse.
            dx (int): The change in x-coordinate of the mouse.
            dy (int): The change in y-coordinate of the mouse.
        """
        self.mouse_coord = (x, y)


    def drawForceVector(self):
        """
        This function draws all the vectors representing a force applied to the body pointed by self.index_body_selected.
        """
        vectors_to_draw = [vector for vector in self.vector_force_list if vector[0]==self.index_body_selected]
        for current_vector in vectors_to_draw:
            body_origin = self.spriteList[current_vector[0]]
            body_direction = self.spriteList[current_vector[1]]
            
            vector_to_draw = Vecteur2D.composante_XY(current_vector[2], body_origin.center_x, body_origin.center_y, body_direction.center_x, body_direction.center_y) *( self.vectors_scale / self.scale)
            
            arcade.draw_line(body_origin.center_x, body_origin.center_y, 
                            Decimal(body_origin.center_x) + vector_to_draw.x, Decimal(body_origin.center_y) + vector_to_draw.y,
                            color = self.bodyList[current_vector[1]].color, line_width=2)
            
            vector_lenght = vector_to_draw.norme()
            if vector_lenght > 10:
                vector_angle = vector_to_draw.angle_with_X_axis()
                
                arcade.draw_line(Decimal(body_origin.center_x) + vector_to_draw.x, Decimal(body_origin.center_y) + vector_to_draw.y, 
                                 Decimal(body_origin.center_x) + vector_to_draw.x - Decimal(math.cos(vector_angle + (math.pi/6)))*20, 
                                 Decimal(body_origin.center_y) + vector_to_draw.y - Decimal(math.sin(vector_angle + (math.pi/6)))*20,
                                 color=self.bodyList[current_vector[1]].color, line_width=2)

                arcade.draw_line(Decimal(body_origin.center_x) + vector_to_draw.x, Decimal(body_origin.center_y) + vector_to_draw.y, 
                                 Decimal(body_origin.center_x) + vector_to_draw.x -Decimal(math.cos(vector_angle - (math.pi/6)))*20, 
                                 Decimal(body_origin.center_y) + vector_to_draw.y - Decimal(math.sin(vector_angle - (math.pi/6)))*20,
                                 color=self.bodyList[current_vector[1]].color, line_width=2)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Function called when the mouse is pressed.
        (built-in function of the arcade module)

        Parameters:
            x (int): The current x-coordinate of the mouse.
            y (int): The current y-coordinate of the mouse.
            buttons (int): An integer representing the buttons that are pressed.
            modifiers (int): An integer representing any keyboard modifiers that are pressed.
        """
        if button == arcade.MOUSE_BUTTON_LEFT:
            click_time = time()
            
            #verifie if double_clic
            if click_time - self.last_click_time < 0.5 and Vecteur2D(x - self.last_click_coord[0], y - self.last_click_coord[1]).norme() < 20:
                self.body_on_focus = self.get_sprite_indice_at_point(x, y)
            else: 
                self.index_body_selected = self.get_sprite_indice_at_point(x, y)
                
                
            self.last_click_coord = x, y
            self.last_click_time = click_time
                
    def get_sprite_indice_at_point(self, x:int, y:int) -> Union[int, None]:
        """
        This function return the indice of the body ( and the body's sprite ) at a given point of the screen.

        :param x: x coordinate of the point
        :type x: int
        :param y: y coordinate of the point
        :type y: int
        :return: Indice of the body. if there isn't a body at the givent point, None is return
        :rtype: int | None
        """
        sprite_index = None
        sprite_under_mouse = arcade.get_sprites_at_point((x - self.spriteOffset.x, y - self.spriteOffset.y), self.spriteList)
        if len(sprite_under_mouse) != 0:
            sprite_index = self.spriteList.index(sprite_under_mouse[0])
        return sprite_index
    
    def on_key_press(self, symbol: int, modifiers: int):
        """
        Called whenever a key is pressed

        Parameters
        ----------
        symbol : int
            symbols on the keyboard
        modifiers : int
            modifiers of the keyboard
        """
        #zoom monitoring
        if symbol == arcade.key.DOWN:
            self.zoom_increasing = True
            
        elif symbol == arcade.key.UP:
            self.zoom_decreasing = True
            
        elif symbol == arcade.key.C:
            self.spriteOffset.x = self.width / 2
            self.spriteOffset.y = self.height / 2
            self.camera_bodys.move((-self.spriteOffset.x, -self.spriteOffset.y))
            
        elif symbol == arcade.key.ESCAPE:
            self.on_close()
            
        elif symbol == arcade.key.P:
            self.on_stop = not self.on_stop
            
        elif symbol == arcade.key.V:
            self.updateVectorsScale()

    def on_close(self):
        """
        Close the simulation window
        """
        self.t2 = time()
        print(f"Temps réel écoulé : {self.t2 - self.t1}s")
        print(f"Temps simulé : {self.iteration * self.delta_time}s")
        print(f"Multiplicateur visé : x{self.time_multiplier}")
        print(f"Multiplicateur obtenu : x{self.iteration * self.delta_time / Decimal(self.t2 - self.t1)}")
        
        self.has_exit = True
        arcade.close_window()
        arcade.cleanup_texture_cache()
        arcade.exit()


    def on_key_release(self, symbol: int, modifiers: int):
        """
        Stop the zoom/dezoom if the keys aren't pressed
        Parameters
        ----------
        symbol : int
            Symbols of the keyboard
        modifiers : int
            Modifiers of the keyboard
        """
        self.zoom_decreasing = False
        self.zoom_increasing = False
    
    
    def update(self, delta_time):
        """
        Function called at a regular time defined by the variable "update_rate"
        (built-in function of the arcade module)
        """
        if self.iteration == 0:
            self.t1 = time()
        
        if not self.on_stop:
            body_indice = 0
            self.vector_force_list = []
            for body in self.bodyList:
                for i in range(len(self.bodyList)):
                    if i != body_indice:
                        
                        
                        #Calcul of the norm of the force's vector 
                        norme = self.calcul_norme.computeNorme(body, self.bodyList[i])
                        
                        attraction = Vecteur2D.composante_XY(norme, body.pos_x, body.pos_y, self.bodyList[i].pos_x, self.bodyList[i].pos_y)
                        
                        force_to_append = body_indice, i, norme
                        self.vector_force_list.append(force_to_append)
                        
                        
                        #Setting of the values
                        body.velocity.x += attraction.x * self.delta_time / body.masse
                        body.velocity.y += attraction.y * self.delta_time / body.masse
                    i += 1
                    
                body_indice += 1
                    
            #Update position of the bodys
            for body in self.bodyList:
                
                body.pos_x += (body.velocity.x) * self.delta_time
                body.pos_y += (body.velocity.y) * self.delta_time
                #Update the orbit list
                if self.show_orbit:                   
                    
                    pos = body.pos_x, body.pos_y
                    self.orbit_points_list.append(pos)
                    
                    pos_sprite = arcade.Sprite(body.pos_SpritePath)
                    pos_sprite.center_x = pos[0] / self.scale
                    pos_sprite.center_y = pos[1] / self.scale
                    self.orbit_points_SpriteList.append(pos_sprite)
                    
                    if len(self.orbit_points_SpriteList) > self.max_orbit_point:
                        self.orbit_points_SpriteList.pop(0)           
                        self.orbit_points_list.pop(0)           

            
            
            if self.show_mass_center: 
                
                #Update position of the center of mass
                average_mass_center = Vecteur2D(0, 0)
                for body in self.bodyList:
                    average_mass_center.x += body.pos_x*body.masse
                    average_mass_center.y += body.pos_y*body.masse
                average_mass_center.x /= self.total_masse
                average_mass_center.y /= self.total_masse
                
                #Update mass center sprite position
                self.mass_centerSprite.center_x = average_mass_center.x / self.scale
                self.mass_centerSprite.center_y = average_mass_center.y / self.scale

            
            if self.show_average_center:
                
                #Update position of the average center
                average_pos = Vecteur2D(0, 0)
                for body in self.bodyList:
                    average_pos.x += body.pos_x
                    average_pos.y += body.pos_y
                    
                #Update position of the average center sprite
                average_pos.x /= len(self.bodyList)
                average_pos.y /= len(self.bodyList)
                
                self.center_sprite.center_x = average_pos.x / self.scale
                self.center_sprite.center_y = average_pos.y / self.scale

            #Update the number of time the function update() has been called
            self.iteration += 1

            #Stop the simulation if the number of iteration reach the max
            if self.iteration_max==self.iteration:          
                arcade.close_window()

            delta_time = Decimal(delta_time)
            self.time += delta_time
            self.simulation_time += self.time_multiplier
            
        #Increasting/decreasting of the zoom
        if self.zoom_increasing:
            self.scale *=Decimal(1.01)
            self.scale_as_changed = True
        if self.zoom_decreasing:
            self.scale /=Decimal(1.01)
            self.scale_as_changed = True    
        
        #Stay focus on the body point by self.body_on_focus
        if self.body_on_focus != None:
            pos_x = float(self.bodyList[self.body_on_focus].pos_x)
            pos_y = float(self.bodyList[self.body_on_focus].pos_y)
            self.spriteOffset.x = -pos_x / float(self.scale) + (self.width/2)
            self.spriteOffset.y = -pos_y / float(self.scale) + (self.height/2)
            self.camera_bodys.move((-self.spriteOffset.x, -self.spriteOffset.y))
        
        self.updateTimeText()
        

        
    def updateTimeText(self):
        """
        Update the time shown
        """
        current_time = self.iteration * self.delta_time
        value = current_time
        text_time = f"{value} s"
        for item in Simulation.time_dict.items():
            value = value // item[1]
            if not value < 1:
                text_time = f"{value} {item[0]}"
                
        self.text_time = text_time
            
    
    
    def updateSpriteScale(self):
        """
        Updating the sprite's scale depending on the zoom
        """
        if self.scale > 0.2 and self.scale < 5:
            self.body_scale = Decimal(1/self.scale)
        elif self.scale < 0.2:
            self.body_scale = 5
        else:
            self.body_scale = 0.2

        for body_sprit in self.spriteList:
            body_sprit.scale = float(self.body_scale)
        self.spriteList.update()



    def updateScaleIndicator(self):
        """
        Update the scale indicator depending on the zoom
        """
        self.scale_indicator_lenght = self.zoom_indicator_parameter / self.scale
        if self.scale_indicator_lenght > Simulation.MAX_ZOOM_INDICATOR_LENTGH:
            self.zoom_indicator_parameter /= 2
            self.scale_indicator_lenght = self.zoom_indicator_parameter / self.scale
        elif self.scale_indicator_lenght < Simulation.MIN_ZOOM_INDICATOR_LENTGH:
            self.zoom_indicator_parameter *= 2
            self.scale_indicator_lenght = self.zoom_indicator_parameter / self.scale
        
        self.scale_indicator_start = Vecteur2D(50, 50)
        self.scale_indicator_end = self.scale_indicator_start + Vecteur2D(self.scale_indicator_lenght, 0)
        
        #affichage des distance avec e+x 
        integer_part_len = len(str(int(self.zoom_indicator_parameter))) - 1
        exposant  = (integer_part_len // 3) * 3
        self.zoom_indicator_text = (f"{str(int(self.zoom_indicator_parameter/10**exposant))} e+{exposant} m")


    def updateVectorsScale(self):
        """
        Update the vectors depending on the zoom
        """
        #Find the longest vector:
        normes = [vector[2] for vector in self.vector_force_list if vector[0]==self.index_body_selected]
        norme_max = max(normes)
        
        #Calcul the value so this vector doesn't exceed the third of the screen diagonal
        screen_diagonal = Decimal(sqrt(self.height**2 + self.height**2)) / 3
        self.vectors_scale = screen_diagonal * self.scale / norme_max
        
                

#For tests purpose
if __name__ == "__main__":
    body_list = [Body("Saturne", pos=(100, 100), color=(255, 0, 0)), Body("Nice", pos=(-100, -100), velocity=Vecteur2D(0, 50), color=(0, 0, 255))]
    simulation = Simulation(900, 900, body_list, shader_preset="Epuré", show_orbit=True, max_orbit_point=2000)
    simulation.setup()
    arcade.run()