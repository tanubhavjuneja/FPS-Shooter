from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from panda3d.core import Filename
from math import atan2, degrees, sqrt
import customtkinter as ctk
import tkfilebrowser
import pygame.mixer
import logging
from functools import wraps
logging.basicConfig(filename='fps_game.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception("%s: %s", func.__name__, e)
            raise
    return wrapper
pygame.mixer.init()
app = Ursina()
window.fullscreen = True
Entity.default_shader = lit_with_shadows_shader
game_started = False
def read_file_location():
    global mfl
    try:
        file=open('file_location.txt', 'r')
        mfl = file.read().strip()
        file.close()
        if not os.path.isfile(os.path.join(mfl, 'iron man.obj')) or not os.path.isfile(os.path.join(mfl, 'jet.obj')) or not os.path.isfile(os.path.join(mfl, 'repulsor.mp3')):
            get_file_location()
    except FileNotFoundError:
        get_file_location()
    home()
def get_file_location():
    global main
    main=ctk.CTk()
    main.geometry("200x50+860+420")
    main.attributes('-topmost', True)
    main.attributes("-alpha",100.0)
    main.lift()
    file_button = ctk.CTkButton(main, text="Select File Location",command=select_file_location,width=1)
    file_button.pack(pady=10)
    main.mainloop()
def select_file_location():
    global main
    mfl = str(tkfilebrowser.askopendirname())+"/"
    mfl = mfl.replace('\\', '/')
    file=open('file_location.txt', 'w')
    file.write(mfl)
    file.close()
    main.destroy()
    read_file_location()
def home():
    map_model_path = mfl + "t3qqxibgic-CenterCitySciFi/Center city Sci-Fi/Center City Sci-Fi.obj"
    panda3d_map_model = loader.loadModel(Filename.fromOsSpecific(map_model_path))
    map_entity = Entity(model=panda3d_map_model,position=(0,-700,0), scale=(1, 1, 1),collider="box") 
    map_width = 574.478
    map_height = 972.816
    map_depth = 893.135
    boundary_thickness = 10
    left_wall = Entity(model='cube', scale=(boundary_thickness, 1000, map_depth), collider='box', position=(-map_width / 2 - boundary_thickness / 2-140, -400, -250), visible=False)
    right_wall = Entity(model='cube', scale=(boundary_thickness, 1000, map_depth), collider='box', position=(map_width / 2 + boundary_thickness / 2-160, -400, -250), visible=False)
    front_wall = Entity(model='cube', scale=(map_width,1000, boundary_thickness), collider='box', position=(-150, -400, map_depth / 2 + boundary_thickness / 2-260), visible=False)
    back_wall = Entity(model='cube', scale=(map_width, 1000, boundary_thickness), collider='box', position=(-150, -400, -map_depth / 2 - boundary_thickness / 2-200), visible=False)
    ambient_light = AmbientLight(color=color.rgb(100, 100, 100))
    ambient_light_entity = Entity(light=ambient_light)
    window.fullscreen = True
    num_lights = 16
    grid_size = 8
    map_size = 64
    average_intensity = 20 * (map_size / 64) 
    grid_count = int(math.sqrt(num_lights))
    spacing = map_size / grid_count
    for row in range(grid_count):
        for col in range(grid_count):
            x = (col - grid_count // 2) * spacing
            z = (row - grid_count // 2) * spacing
            intensity = average_intensity if (abs(x) < map_size / 2 and abs(z) < map_size / 2) else 10
            light = PointLight(color=color.rgb(255, 255, 255), intensity=intensity, range=20)
            light_entity = Entity(light=light, position=(x, 10, z))
    def start_game(str):
        global difficulty
        destroy(home_screen_text)
        destroy(start_button1)
        destroy(start_button2)
        destroy(start_button3)
        destroy(quit_button)
        difficulty=str
        false_start()
    home_screen_text = Text(text='Start Game', scale=6, y=0.3,x=-0.4)
    start_button1 = Button(text='Easy', scale=(0.3, 0.1), y=-0.1,x=-0.5, on_click=lambda:start_game('Easy'))
    start_button2 = Button(text='Medium', scale=(0.3, 0.1), y=-0.1, x=0,on_click=lambda:start_game('Medium'))
    start_button3 = Button(text='Hard', scale=(0.3, 0.1), y=-0.1,x=0.5, on_click=lambda:start_game('Hard'))
    quit_button = Button(text='Quit', scale=(0.3, 0.1), y=-0.3, x=0, on_click=quit_game)
def false_start():
    global shot_sound,mfl,difficulty,editor_camera,no_of_shots,health_bar,player_health,player_hp,enemies,pause_handler,shooting,zombies_killed_text,accuracy_text,gun,player,shootables_parent,sten,game_started,maxen,hp_gain
    if difficulty=='Easy':
        sten=5
        maxen=10
        hp_gain=60
    elif difficulty=='Medium':
        sten=6
        maxen=14
        hp_gain=40
    elif difficulty=='Hard':
        sten=7
        maxen=18
        hp_gain=20
    shot_sound = pygame.mixer.Sound(mfl+'repulsor.mp3')
    editor_camera = EditorCamera(enabled=False, ignore_paused=True)
    panda3d_player_model = loader.loadModel(Filename.fromOsSpecific(mfl+"iron man.obj"))
    player = FirstPersonController(model=panda3d_player_model, z=-10,color=color.dark_gray, origin=(0,-2,1), speed=80, collider='box')
    player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
    player.cursor.scale = 0.005
    gun = Entity(model="cube", parent=camera, position=(0, -0.9, 0), scale=(2, 2, 2), origin_z=-.1, on_cooldown=False,visible=False)
    shootables_parent = Entity()
    mouse.traverse_target = shootables_parent
    player_health=200
    player_hp=200
    no_of_shots=-1
    health_bar = HealthBar(value=player_health, position=(0, -0.495), scale=(1.8, 0.01))
    enemies = [Enemy(x=x * sten) for x in range(4)]
    pause_handler = Entity(ignore_paused=True, input=pause_input)
    shooting = False
    zombies_killed_text = Text(text='Kills: 000', position=(-0.85, 0.45), origin=(-0.5, 0.5), background=True, background_color=(0, 0, 0, 0.5))
    accuracy_text = Text(text='Accuracy: 100%', position=(-0.85, 0.35), origin=(-0.5, 0.5), background=True, background_color=(0, 0, 0, 0.5))
    game_started=True
class HealthBar(Entity):
    def __init__(self, value=1000, position=(0, -0.495), scale=(1.8, 0.01), color=color.rgb(255, 0, 0)):
        super().__init__(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=color,
            position=position,
            scale=scale
        )
        self.value = value
        self.original_scale_x = scale[0]
    def update_value(self, new_value):
        self.value = new_value
        self.scale_x = max(0, min(self.value / 200, 1)) * self.original_scale_x
def spawn_enemies(number_of_enemies):
    for _ in range(number_of_enemies):
        Enemy(x=random.uniform(-8, 8), z=random.uniform(-8, 8) + 8)
def update():
    global shooting,player_health,game_started
    if game_started==True:
        if player.y < -700:
            respawn_player()
        if not shooting and held_keys['left mouse']:
            shooting = True
            shoot()
        elif not held_keys['left mouse']:
            shooting = False
        if held_keys['escape']:
            quit_game()
        health_bar.update_value(player_health)
        update_zombies_killed_text()
def respawn_player():
    player.position = Vec3(0, -2, 0)
def shoot():
    global no_of_shots, player_health, maxen, player_hp
    if shooting and not gun.on_cooldown:
        gun.on_cooldown = True
        if mouse.world_point:
            shot_sound.play()
            direction = (mouse.world_point - player.position).normalized()
            position = player.position + direction * 0.5
            beam_quad = Entity(
                model='sphere',
                color=color.cyan,
                scale=(2000, 0.2, 0.2),
                position=position,
                collider=None,
                two_sided=True
            )
            beam_quad.look_at(mouse.world_point)
            beam_quad.rotation_y += 90
            def destroy_beam():
                beam_quad.disable()
                destroy(beam_quad)
            invoke(destroy_beam, delay=0.2)
        invoke(setattr, gun, 'on_cooldown', False, delay=0.15)
        no_of_shots += 1
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
            if mouse.hovered_entity.hp <= 0:
                Enemy.enemies_destroyed += 1
                if Enemy.enemies_destroyed <= maxen:
                    spawn_enemies(2)
                else:
                    spawn_enemies(1)
                if Enemy.enemies_destroyed % 5 == 0:
                    player_health += hp_gain
                    if player_health > player_hp:
                        player_health = player_hp
                    health_bar.value = player_health
class Bullet(Entity):
    instances = [] 
    def __init__(self, position, direction):
        super().__init__(
            model="sphere",
            color=color.gray,
            scale=1,
            position=position,
        )
        self.direction = direction.normalized()
        self.speed = 10000
        self.max_distance = 30
        self.initial_distance = (self.position - player.position).length()
        Bullet.instances.append(self)  
    def update(self):
        self.position += self.direction * self.speed * time.dt
        current_distance = (self.position - player.position).length()
        if current_distance - self.initial_distance > self.max_distance:
            self.destroy() 
    def destroy(self):
        self.remove_from_instances() 
        destroy(self) 
    @classmethod
    def remove_from_instances(cls):
        if cls in Bullet.instances:
            Bullet.instances.remove(cls)
    @classmethod
    def destroy_all(cls):
        for bullet in cls.instances[:]: 
            bullet.destroy()
class Enemy(Entity):
    enemies_destroyed = 0
    enemy_instances=[]
    def __init__(self, **kwargs):
        panda3d_enemy_model = loader.loadModel(Filename.fromOsSpecific(mfl+"jet.obj"))
        panda3d_enemy_model.setHpr(90,90,0)
        super().__init__(parent=shootables_parent, model=panda3d_enemy_model, scale=(0.2,0.2,0.2), origin_y=1750, color=color.gray, collider='box', **kwargs)
        Enemy.enemy_instances.append(self)  
        self.max_hp = 10
        self.hp = self.max_hp
        self.speed = 100
        map_width = 574.478
        map_length = 893.135
        wall = random.choice(['left','right','front','back'])
        offset = -100
        min_distance_from_player = 200
        while True:
            if wall == 'front':
                self.position = Vec3(random.uniform(-map_width/2 + offset-100, map_width/2 - offset-300), 0, map_length / 2 - offset-350)
            elif wall == 'back':
                self.position = Vec3(random.uniform(-map_width/2 + offset-100, map_width/2 - offset-300), 0, -map_length / 2 + offset)
            elif wall == 'left':
                self.position = Vec3(-map_width / 2 + offset, 0, random.uniform(-map_length / 2 + offset-100, map_length / 2 - offset-400))
            elif wall == 'right':
                self.position = Vec3(map_width / 2 - offset-300, 0, random.uniform(-map_length / 2 + offset-100, map_length / 2 - offset-400))
            distance_to_player = (self.position - player.position).length()
            if distance_to_player >= min_distance_from_player:
                break
    def shoot_at_player(self):
        global player_health
        hit_info = raycast(player.position + Vec3(0, 1, 0), self.forward, 1200, ignore=(self,))
        bullet = Bullet(position=self.world_position + Vec3(0, -350, 0), direction=self.forward)
        if hit_info.entity == player:
            player_health -= 1
            health_bar.value = player_health
            if player_health <= 0:
                player_health = 0
                end_game_screen()
    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 1200:
            return
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 1200, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
        if random.random() < 0.01:  
            self.shoot_at_player()
    @property
    def hp(self):
        return self._hp
    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return
    def destroy(self):
        self.remove_from_instances() 
        destroy(self) 
    @classmethod
    def remove_from_instances(cls1):
        if cls1 in Enemy.enemy_instances:
            Enemy.enemy_instances.remove(cls1)
    @classmethod
    def destroy_all(cls):
        for enemy in cls.enemy_instances[:]: 
            enemy.destroy()
def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
def update_zombies_killed_text():
    zombies_killed_text.text = f'Kills: {Enemy.enemies_destroyed}'
    if no_of_shots!=0:
        accuracy=((Enemy.enemies_destroyed*10000)//no_of_shots)/100
        accuracy_text.text = f'Accuracy: {accuracy}%'
def end_game_screen():
    global end_game_text,score_text,start_button1,start_button2,start_button3,quit_button,accurac_text
    player.enabled = False
    for enemy in enemies:
        enemy.enabled=False
    gun.enabled = False
    health_bar.enabled = False
    zombies_killed_text.enabled = False
    accuracy_text.enabled = False
    accuracy = 0
    if no_of_shots != 0:
        accuracy = ((Enemy.enemies_destroyed * 10000) // no_of_shots) / 100
    end_game_text = Text(text='Game Over', scale=6, y=0.4,x=-0.4)
    score_text = Text(text=f'Kills: {Enemy.enemies_destroyed}', scale=3, y=0.2,x=-0.3)
    accurac_text = Text(text=f'Accuracy: {accuracy}%', scale=3, y=0.1,x=-0.3)
    start_button1 = Button(text='Easy', scale=(0.3, 0.1), y=-0.15,x=-0.5, on_click=lambda:replay_game('Easy'))
    start_button2 = Button(text='Medium', scale=(0.3, 0.1), y=-0.15, x=0,on_click=lambda:replay_game('Medium'))
    start_button3 = Button(text='Hard', scale=(0.3, 0.1), y=-0.15,x=0.5, on_click=lambda:replay_game('Hard'))
    quit_button = Button(text='Quit', scale=(0.3, 0.1), y=-0.35, on_click=quit_game)
def quit_game():
    application.quit()
def replay_game(difficulty):
    global no_of_shots, player_health,sten,maxen,hp_gain
    if difficulty=='Easy':
        sten=5
        maxen=10
        hp_gain=80
    elif difficulty=='Medium':
        sten=6
        maxen=14
        hp_gain=60
    elif difficulty=='Hard':
        sten=7
        maxen=18
        hp_gain=40
    Bullet.destroy_all()
    Enemy.destroy_all()
    no_of_shots = 0
    player_health = player_hp
    health_bar.update_value(player_health)
    for enemy in enemies:
        destroy(enemy)
    enemies.clear()
    Enemy.enemies_destroyed = 0
    player.enabled = True
    gun.enabled = True
    health_bar.enabled = True
    zombies_killed_text.enabled = True
    accuracy_text.enabled = True
    spawn_enemies(sten) 
    destroy(end_game_text)
    destroy(score_text)
    destroy(accurac_text)
    destroy(start_button1)
    destroy(start_button2)
    destroy(start_button3)
    destroy(quit_button)
read_file_location()
app.run()