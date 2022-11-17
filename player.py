from settings import *
from support import *
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction_sprites, soil_layer):
        super().__init__(group)

        # animations (in self.import_assets) (import assets)
        self.animations = {
            'down': [], 'left': [], 'right': [], 'up': [],
            'down_axe': [], 'left_axe': [], 'right_axe': [], 'up_axe': [],
            'down_hoe': [], 'left_hoe': [], 'right_hoe': [], 'up_hoe': [],
            'down_idle': [], 'left_idle': [], 'right_idle': [], 'up_idle': [],
            'down_water': [], 'left_water': [], 'right_water': [], 'up_water': []
        }
        self.import_assets()

        # init status
        self.status = 'down_idle'
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]  # folder, frame
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # get width and height
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        # print("%d %d", self.image_width, self.image_height)

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        # timers 计时器
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }

        # tools
        self.tools = ['axe', 'hoe', 'water']
        self.tools_index = 0
        self.selected_tool = self.tools[self.tools_index]

        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # inventory
        self.item_inventory = {
            'wood': 0,
            'corn': 0,
            'apple': 0,
            'tomato': 0
        }

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.soil_player = soil_layer

        # get_target_pos
        self.target_pos = self.rect.center

    def import_assets(self):
        """
        load graphics (character) to animations (dict)
        """
        for animation in self.animations.keys():
            full_path = "graphics/character/" + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        """
        animation player
        """
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_player.get_hit(self.target_pos)

        if self.selected_tool == 'water':
            pass

        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAY_TOOL_OFFSET[self.status.split('_')[0]]

    def use_seed(self):
        pass

    def input(self):
        """
        move regular: direction, animate
        """
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep:
            # change direction
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0  # recovery

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tools_index += 1
                if self.tools_index >= len(self.tools):
                    self.tools_index = 0
                self.selected_tool = self.tools[self.tools_index]

            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.seed_index = 0

            # change seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]

            # restart a day
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        pass
                    else:
                        self.status = 'left_idle'
                        self.sleep = True

    def get_statues(self):
        # change to idle (if the player in not moving (通过计算欧氏距离))
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        # tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        """
        limit the range of movement
        """
        # normalizing a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        # print(self.direction)

        # horizontal movement 水平
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt):
        self.input()
        self.get_statues()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt)
