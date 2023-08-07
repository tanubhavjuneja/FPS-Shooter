from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
app = Ursina()
random.seed(0)
Entity.default_shader = lit_with_shadows_shader
ground = Entity(model='plane', collider='box', scale=(64, 1, 64), texture='grass', texture_scale=(8, 8))
roof = Entity(model='cube', scale=(64, 1, 64), position=(0, 11, 0), texture="brick", collider='box')
left_wall = Entity(model='cube', scale=(1, 18, 64), position=(-32, 2, 0), texture="brick", collider='box')
right_wall = Entity(model='cube', scale=(1, 18, 64), position=(32, 2, 0), texture="brick", collider='box')
front_wall = Entity(model='cube', scale=(64, 18, 1), position=(0, 2, 32), texture="brick", collider='box')
back_wall = Entity(model='cube', scale=(64, 18, 1), position=(0, 2, -32), texture="brick", collider='box')
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
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
gun = Entity(model="cube", parent=camera, position=(.5, -0.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
shootables_parent = Entity()
mouse.traverse_target = shootables_parent
no_of_shots=0
class HealthBar(Entity):
    def __init__(self, value=100, position=(0, -0.495), scale=(1.8, 0.01), color=color.rgb(255, 0, 0)):
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
        self.scale_x = max(0, min(self.value / 100, 1)) * self.original_scale_x
player_health = 100
health_bar = HealthBar(value=player_health, position=(0, -0.495), scale=(1.8, 0.01))
def spawn_enemies(number_of_enemies):
    for _ in range(number_of_enemies):
        Enemy(x=random.uniform(-8, 8), z=random.uniform(-8, 8) + 8)
def update():
    global shooting,player_health
    if not shooting and held_keys['left mouse']:
        shooting = True
        shoot()
    elif not held_keys['left mouse']:
        shooting = False
    if held_keys['escape']:
        quit_game()
    health_bar.update_value(player_health)
    update_zombies_killed_text()
def shoot():
    global no_of_shots,player_health
    if shooting and not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        no_of_shots+=1
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
            if mouse.hovered_entity.hp <= 0:
                Enemy.enemies_destroyed += 1
                if Enemy.enemies_destroyed <= 20:
                    spawn_enemies(2)
                else:
                    spawn_enemies(1)
                if Enemy.enemies_destroyed % 5 == 0:
                    player_health += 20 
                    if player_health > 100:
                        player_health = 100
                    health_bar.value = player_health
class Bullet(Entity):
    instances = [] 
    def __init__(self, position, direction):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.1,
            position=position,
        )
        self.direction = direction.normalized()
        self.speed = 10
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
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.green, collider='box', **kwargs)
        Enemy.enemy_instances.append(self)  
        self.max_hp = 10
        self.hp = self.max_hp
        self.speed = 10
        map_width = 64 
        map_length = 64 
        wall = random.choice(['top', 'bottom', 'left', 'right'])
        offset = 2
        min_distance_from_player = 30
        while True:
            if wall == 'top':
                self.position = Vec3(random.uniform(-map_width/2+offset, map_width/2-offset), 0, 32 - offset)
            elif wall == 'bottom':
                self.position = Vec3(random.uniform(-map_width/2+offset, map_width/2-offset), 0, -32 + offset)
            elif wall == 'left':
                self.position = Vec3(-32 + offset, 0, random.uniform(-map_length/2+offset, map_length/2-offset))
            elif wall == 'right':
                self.position = Vec3(32 - offset, 0, random.uniform(-map_length/2+offset, map_length/2-offset))
            distance_to_player = (self.position - player.position).length()
            if distance_to_player >= min_distance_from_player:
                break
    def shoot_at_player(self):
        global player_health
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 120, ignore=(self,))
        bullet = Bullet(position=self.world_position + Vec3(0, 1, 0), direction=self.forward)
        if hit_info.entity == player:
            player_health -= 1
            health_bar.value = player_health
            if player_health <= 0:
                player_health = 0
                print("yes")
                end_game_screen()
    def update(self):
        distance_to_player = (self.position - player.position).length()
        min_distance = 15
        max_distance = 50
        min_speed = 8
        max_speed = 20
        if distance_to_player < min_distance:
            speed_adjustment = 1.0
        elif distance_to_player > max_distance:
            speed_adjustment = max_speed / self.speed
        else:
            speed_adjustment = (max_speed - min_speed) / (max_distance - min_distance) * (distance_to_player - min_distance) + min_speed / self.speed
        self.speed *= speed_adjustment
        dist = distance_xz(player.position, self.position)
        if dist > 120:
            return
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 120, ignore=(self,))
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
enemies = [Enemy(x=x * 4) for x in range(4)]
def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
pause_handler = Entity(ignore_paused=True, input=pause_input)
shooting = False
zombies_killed_text = Text(text='Zombies Killed: 000', position=(-0.85, 0.45), origin=(-0.5, 0.5), background=True, background_color=(0, 0, 0, 0.5))
accuracy_text = Text(text='Accuracy: 100%', position=(-0.85, 0.35), origin=(-0.5, 0.5), background=True, background_color=(0, 0, 0, 0.5))
def update_zombies_killed_text():
    zombies_killed_text.text = f'Zombies Killed: {Enemy.enemies_destroyed}'
    if no_of_shots!=0:
        accuracy=((Enemy.enemies_destroyed*10000)//no_of_shots)/100
        accuracy_text.text = f'Accuracy: {accuracy}%'
def end_game_screen():
    global end_game_text,score_text,replay_button,quit_button,accurac_text
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
    score_text = Text(text=f'Final Score: {Enemy.enemies_destroyed}', scale=3, y=0.2,x=-0.2)
    accurac_text = Text(text=f'Accuracy: {accuracy}%', scale=3, y=0.1,x=-0.2)
    replay_button = Button(text='Replay', scale=(0.3, 0.2), y=-0.25, x=-0.3, on_click=replay_game)
    quit_button = Button(text='Quit', scale=(0.3, 0.2), y=-0.25, x=0.3, on_click=quit_game)
def quit_game():
    application.quit()
def replay_game():
    global no_of_shots, player_health
    Bullet.destroy_all()
    Enemy.destroy_all()
    no_of_shots = 0
    player_health = 100
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
    spawn_enemies(4) 
    destroy(end_game_text)
    destroy(score_text)
    destroy(accurac_text)
    destroy(replay_button)
    destroy(quit_button)
app.run()