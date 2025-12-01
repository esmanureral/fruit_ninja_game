import pygame
import math
import random
import os
from typing import List, Tuple, Optional
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
IMAGES_FOLDER = "images"
FRUIT_SIZE = 80  # Meyve resimlerinin hedef boyutu (piksel)
FRUIT_MIN_SIZE = 70  # Meyve resimlerinin minimum boyutu (piksel)
SLICED_FRUIT_SIZE = 90  # Kesilmiş meyve resimlerinin genişliği
GRAVITY = 0.35  # Meyve ve bombalar için yerçekimi

# Colors
BROWN = (101, 67, 33)
DARK_BROWN = (69, 39, 19)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)  # Açık mavi üst şerit için
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# UI Constants
TOP_BAR_HEIGHT = 80
BOTTOM_BAR_HEIGHT = 60
GAME_AREA_Y = TOP_BAR_HEIGHT
GAME_AREA_HEIGHT = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
MAX_LIVES = 3

class Fruit:
    def __init__(self, x, y, fruit_type="apple", image=None, sliced_image=None):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        self.image = image
        self.sliced_image = sliced_image
        self.radius = 30
        self.color = RED  # Fallback color if no image
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.angle = 0
        self.rotation_speed = random.uniform(-5, 5)
        
        # If image exists, get size from image
        if self.image:
            self.radius = max(self.image.get_width(), self.image.get_height()) // 2
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.angle += self.rotation_speed
        
        # Kenardan çok çıkmasın diye yatay konumu sınırla
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))

    def is_missed(self):
        """Meyve oyun alanının altına düştüyse can kaybettirir."""
        return self.y - self.radius > GAME_AREA_Y + GAME_AREA_HEIGHT
        
    def draw(self, screen):
        if self.image:
            # Draw the fruit image directly (resimler zaten gölgeli olduğu için ekstra gölge gerekmez)
            rotated_image = pygame.transform.rotate(self.image, -self.angle)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            # Fallback: Draw circle if no image
            shadow_offset = 3
            shadow_color = (30, 30, 30)
            pygame.draw.circle(screen, shadow_color, 
                              (int(self.x + shadow_offset), int(self.y + shadow_offset)), 
                              self.radius)
            pygame.draw.circle(screen, self.color, 
                              (int(self.x), int(self.y)), 
                              self.radius)
            highlight = (min(255, self.color[0] + 50), 
                        min(255, self.color[1] + 50), 
                        min(255, self.color[2] + 50))
            pygame.draw.circle(screen, highlight, 
                              (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3)), 
                              int(self.radius * 0.4))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class SlicedFruit:
    """Represents a sliced fruit with two halves that fly apart"""
    def __init__(self, x, y, fruit_type="apple", sliced_image=None):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        self.sliced_image = sliced_image
        self.life = 60  # Frames until removal (artırıldı - daha uzun görünecek)
        
        # Two halves fly in opposite directions
        self.half1_x = x
        self.half1_y = y
        self.half2_x = x
        self.half2_y = y
        
        # Velocities for halves
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 6)
        self.half1_vx = math.cos(angle) * speed
        self.half1_vy = math.sin(angle) * speed - 2  # Slight upward
        self.half2_vx = -math.cos(angle) * speed
        self.half2_vy = -math.sin(angle) * speed - 2
        
        self.rotation1 = 0
        self.rotation2 = 0
        self.rotation_speed1 = random.uniform(-10, 10)
        self.rotation_speed2 = random.uniform(-10, 10)
        
    def update(self):
        # Update positions
        self.half1_x += self.half1_vx
        self.half1_y += self.half1_vy
        self.half2_x += self.half2_vx
        self.half2_y += self.half2_vy
        
        # Gravity
        self.half1_vy += 0.5
        self.half2_vy += 0.5
        
        # Rotation
        self.rotation1 += self.rotation_speed1
        self.rotation2 += self.rotation_speed2
        
        self.life -= 1
        
    def draw(self, screen):
        if self.sliced_image:
            # Draw two halves
            # Split the image in half
            img_width = self.sliced_image.get_width()
            img_height = self.sliced_image.get_height()
            
            # Create left and right halves
            try:
                left_half = self.sliced_image.subsurface((0, 0, img_width // 2, img_height))
                right_half = self.sliced_image.subsurface((img_width // 2, 0, img_width // 2, img_height))
                
                # Rotate halves
                rotated_left = pygame.transform.rotate(left_half, -self.rotation1)
                rotated_right = pygame.transform.rotate(right_half, -self.rotation2)
                
                # Draw halves
                rect1 = rotated_left.get_rect(center=(int(self.half1_x), int(self.half1_y)))
                rect2 = rotated_right.get_rect(center=(int(self.half2_x), int(self.half2_y)))
                
                screen.blit(rotated_left, rect1)
                screen.blit(rotated_right, rect2)
            except Exception as e:
                # Fallback if slicing fails
                print(f"Hata sliced resim çizimi: {e}")
                pygame.draw.circle(screen, RED, (int(self.half1_x), int(self.half1_y)), 15)
                pygame.draw.circle(screen, RED, (int(self.half2_x), int(self.half2_y)), 15)
        else:
            # Fallback: Draw two semicircles
            pygame.draw.circle(screen, RED, (int(self.half1_x), int(self.half1_y)), 15)
            pygame.draw.circle(screen, RED, (int(self.half2_x), int(self.half2_y)), 15)
    
    def is_alive(self):
        return self.life > 0

class Bomb:
    """Bomb that causes game over when sliced"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.angle = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.pulse_timer = 0  # For pulsing effect
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.8
        self.angle += self.rotation_speed
        self.pulse_timer += 1
        
        # Kenardan aşırı taşmasın
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))

    def is_off_screen(self):
        """Bomba oyun alanından tamamen çıktıysa temizle."""
        return self.y - self.radius > GAME_AREA_Y + GAME_AREA_HEIGHT + 60
    
    def draw(self, screen):
        # Pulsing effect
        pulse = math.sin(self.pulse_timer * 0.2) * 3
        current_radius = self.radius + int(pulse)
        
        # Draw black bomb body
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), current_radius)
        # Draw fuse (red)
        fuse_length = 8
        fuse_angle = self.angle * math.pi / 180
        fuse_x = int(self.x + math.cos(fuse_angle) * current_radius)
        fuse_y = int(self.y + math.sin(fuse_angle) * current_radius)
        pygame.draw.circle(screen, RED, (fuse_x, fuse_y), 5)
        
        # Draw warning lines
        for i in range(3):
            angle = self.angle + i * 120
            angle_rad = angle * math.pi / 180
            start_x = int(self.x + math.cos(angle_rad) * (current_radius - 5))
            start_y = int(self.y + math.sin(angle_rad) * (current_radius - 5))
            end_x = int(self.x + math.cos(angle_rad) * (current_radius + 10))
            end_y = int(self.y + math.sin(angle_rad) * (current_radius + 10))
            pygame.draw.line(screen, YELLOW, (start_x, start_y), (end_x, end_y), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        # Normalize color to ensure it's a valid RGB tuple
        if isinstance(color, (tuple, list)) and len(color) >= 3:
            try:
                self.color = tuple(max(0, min(255, int(c))) for c in color[:3])
            except (ValueError, TypeError):
                self.color = (255, 0, 0)  # Default to red if invalid
        else:
            self.color = (255, 0, 0)  # Default to red if invalid
        self.size = random.randint(3, 8)
        self.life = 30
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.3  # Gravity
        
    def draw(self, screen):
        # Fade out particles as they age
        alpha_ratio = max(0.0, min(1.0, self.life / 30.0))  # Clamp between 0 and 1
        
        # Calculate faded color (self.color is already normalized in __init__)
        faded_color = tuple(max(0, min(255, int(c * alpha_ratio))) for c in self.color)
        pygame.draw.circle(screen, faded_color, (int(self.x), int(self.y)), self.size)
    
    def is_alive(self):
        return self.life > 0

class FruitNinja:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fruit Ninja")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.fruits: List[Fruit] = []
        self.bombs: List[Bomb] = []
        self.sliced_fruits: List[SlicedFruit] = []
        self.particles: List[Particle] = []
        self.score = 0
        self.best_score = 0
        self.lives = MAX_LIVES
        self.game_over = False
        
        # Combo system
        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 120
        self.show_title_screen = True  # Start with title screen
        
        self.swipe_path: List[Tuple[int, int]] = []
        self.swiping = False
        self.title_sliced = False
        
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames between spawns
        self.bomb_spawn_timer = 0
        self.bomb_spawn_interval = 300  # Bomb spawns less frequently
        
        # Load fruit images
        self.fruit_images = self.load_fruit_images()
        
        # Set random seed for consistent wood texture
        random.seed(42)
        # Create wooden background texture
        self.wood_texture = self.create_wood_texture()
        # Reset random seed after texture creation
        random.seed()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 48)
        
        # Load best score from file if exists
        self.load_best_score()
        
    def load_fruit_images(self):
        """Load fruit images from images folder"""
        fruit_images = {}
        
        # Check if images folder exists
        if not os.path.exists(IMAGES_FOLDER):
            print(f"'{IMAGES_FOLDER}' klasörü bulunamadı. Renkli daireler kullanılacak.")
            return fruit_images
        
        # Automatically detect all fruit images in the folder
        # Scan all PNG files
        all_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith('.png')]
        
        # Extract fruit types from filenames
        fruit_type_map = {}  # Maps fruit type to file paths
        
        for filename in all_files:
            name_lower = filename.lower().replace('.png', '')
            
            # Check if it's a sliced image
            if '_sliced' in name_lower:
                # Extract fruit type (before _sliced)
                fruit_type = name_lower.split('_sliced')[0]
                # Remove any numbers at the end (like pineapple_sliced1 -> pineapple)
                fruit_type = ''.join([c for c in fruit_type if not c.isdigit()])
                
                if fruit_type not in fruit_type_map:
                    fruit_type_map[fruit_type] = {"whole": None, "sliced": []}
                
                # Handle multiple sliced images (like pineapple_sliced1, pineapple_sliced2)
                fruit_type_map[fruit_type]["sliced"].append(filename)
            else:
                # This is a whole fruit image
                fruit_type = name_lower
                
                if fruit_type not in fruit_type_map:
                    fruit_type_map[fruit_type] = {"whole": None, "sliced": []}
                
                fruit_type_map[fruit_type]["whole"] = filename
        
        # Load all detected fruit images
        for fruit_type, files in fruit_type_map.items():
            whole_img = None
            sliced_img = None
            
            # Load whole fruit image
            if files["whole"]:
                whole_path = os.path.join(IMAGES_FOLDER, files["whole"])
                try:
                    loaded_img = pygame.image.load(whole_path).convert_alpha()
                    original_width, original_height = loaded_img.get_size()
                    
                    # Calculate scale to fit FRUIT_SIZE while maintaining aspect ratio
                    max_dimension = max(original_width, original_height)
                    scale = FRUIT_SIZE / max_dimension
                    
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    
                    # Ensure minimum size - if scaled image is too small, scale up to minimum
                    final_max_dimension = max(new_width, new_height)
                    if final_max_dimension < FRUIT_MIN_SIZE:
                        # Scale up to minimum size
                        scale = FRUIT_MIN_SIZE / max_dimension
                        new_width = int(original_width * scale)
                        new_height = int(original_height * scale)
                        print(f"  ⚠ {fruit_type} çok küçüktü, minimum boyuta ölçeklendi")
                    
                    whole_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))
                    print(f"✓ Yüklendi: {fruit_type} ({files['whole']}) {original_width}x{original_height} -> {new_width}x{new_height}")
                except Exception as e:
                    print(f"✗ Hata yükleme {whole_path}: {e}")
            
            # Load sliced fruit image (use first one if multiple exist)
            if files["sliced"]:
                sliced_filename = files["sliced"][0]  # Use first sliced image
                sliced_path = os.path.join(IMAGES_FOLDER, sliced_filename)
                try:
                    loaded_img = pygame.image.load(sliced_path).convert_alpha()
                    original_width, original_height = loaded_img.get_size()
                    scale = SLICED_FRUIT_SIZE / original_width
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    
                    sliced_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))
                    print(f"✓ Yüklendi: {fruit_type} sliced ({sliced_filename}) {original_width}x{original_height} -> {new_width}x{new_height}")
                except Exception as e:
                    print(f"✗ Hata yükleme {sliced_path}: {e}")
            
            # Only add if we have BOTH whole and sliced images
            if whole_img and sliced_img:
                fruit_images[fruit_type] = {
                    "whole": whole_img,
                    "sliced": sliced_img
                }
                print(f"  ✓ {fruit_type} oyuna eklendi (hem tam hem kesilmiş resmi var)")
            elif whole_img:
                print(f"  ⚠ {fruit_type} atlandı (kesilmiş resmi yok)")
            elif sliced_img:
                print(f"  ⚠ {fruit_type} atlandı (tam resmi yok)")
        
        print(f"\n🎮 Toplam {len(fruit_images)} meyve tipi yüklendi: {', '.join(fruit_images.keys())}")
        
        if not fruit_images:
            print(f"⚠ '{IMAGES_FOLDER}' klasöründe meyve resmi bulunamadı. Renkli daireler kullanılacak.")
        
        return fruit_images
    
    def get_random_fruit_type(self):
        """Get a random fruit type, prioritizing those with images"""
        if self.fruit_images:
            return random.choice(list(self.fruit_images.keys()))
        return "apple"  # Default
    
    def load_best_score(self):
        """Load best score from file"""
        try:
            if os.path.exists("best_score.txt"):
                with open("best_score.txt", "r") as f:
                    self.best_score = int(f.read().strip())
        except:
            self.best_score = 0
    
    def save_best_score(self):
        """Save best score to file"""
        try:
            with open("best_score.txt", "w") as f:
                f.write(str(self.best_score))
        except:
            pass
    
    def create_wood_texture(self):
        """Create a simple wood texture surface"""
        texture = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        texture.fill(BROWN)
        
        # Draw vertical wood grain lines for more realistic look
        for i in range(0, SCREEN_WIDTH, 3):
            # Create variation in wood grain
            intensity = random.randint(0, 30)
            line_color = (
                max(0, BROWN[0] - intensity),
                max(0, BROWN[1] - intensity),
                max(0, BROWN[2] - intensity)
            )
            pygame.draw.line(texture, line_color, (i, 0), (i, SCREEN_HEIGHT), 1)
        
        # Add some horizontal grain variations
        for i in range(0, SCREEN_HEIGHT, 8):
            if random.random() > 0.7:  # Random horizontal lines
                pygame.draw.line(texture, DARK_BROWN, (0, i), (SCREEN_WIDTH, i), 1)
        
        return texture
    
    def spawn_bomb(self):
        """Bombalar da aşağıdan fırlayıp yukarı sıçrasın"""
        x = random.randint(80, SCREEN_WIDTH - 80)
        y = GAME_AREA_Y + GAME_AREA_HEIGHT + 30  # ekranın biraz altı
        vx = random.uniform(-4, 4)
        vy = random.uniform(-10, -8)  # yukarı doğru

        bomb = Bomb(x, y)
        bomb.vx = vx
        bomb.vy = vy
        self.bombs.append(bomb)
    
    def spawn_fruit(self):
        """Spawn a new fruit at a random edge"""
        side = random.randint(0, 3)
        center_x = SCREEN_WIDTH // 2
        center_y = GAME_AREA_Y + GAME_AREA_HEIGHT // 2
        
        if side == 0:  # Top
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = GAME_AREA_Y
            # Velocity towards center with some randomness
            dx = center_x - x + random.uniform(-50, 50)
            dy = center_y - y + random.uniform(0, 100)
        elif side == 1:  # Right
            x = SCREEN_WIDTH
            y = random.randint(50, SCREEN_HEIGHT - 50)
            dx = center_x - x + random.uniform(-100, 0)
            dy = center_y - y + random.uniform(-50, 50)
        elif side == 2:  # Bottom
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = GAME_AREA_Y + GAME_AREA_HEIGHT
            dx = center_x - x + random.uniform(-50, 50)
            dy = center_y - y + random.uniform(-100, 0)
        else:  # Left
            x = 0
            y = random.randint(50, SCREEN_HEIGHT - 50)
            dx = center_x - x + random.uniform(0, 100)
            dy = center_y - y + random.uniform(-50, 50)
        
        # Normalize velocity
        speed = random.uniform(2, 4)
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed
        else:
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
        
        # Get fruit type and images
        fruit_type = self.get_random_fruit_type()
        whole_img = None
        sliced_img = None
        
        if fruit_type in self.fruit_images:
            whole_img = self.fruit_images[fruit_type]["whole"]
            sliced_img = self.fruit_images[fruit_type]["sliced"]
        
        fruit = Fruit(x, y, fruit_type, whole_img, sliced_img)
        fruit.vx = vx
        fruit.vy = vy
        self.fruits.append(fruit)
    
    def point_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return math.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
        
        dx = px - xx
        dy = py - yy
        return math.sqrt(dx * dx + dy * dy)
    
    def check_slice(self, fruit):
        """Check if fruit is sliced by the swipe path"""
        if len(self.swipe_path) < 2:
            return False
            
        for i in range(len(self.swipe_path) - 1):
            x1, y1 = self.swipe_path[i]
            x2, y2 = self.swipe_path[i + 1]
            
            distance = self.point_line_distance(fruit.x, fruit.y, x1, y1, x2, y2)
            
            if distance < fruit.radius:
                return True
        
        return False
    
    def check_bomb_slice(self, bomb):
        """Check if bomb is sliced by the swipe path"""
        if len(self.swipe_path) < 2:
            return False
            
        for i in range(len(self.swipe_path) - 1):
            x1, y1 = self.swipe_path[i]
            x2, y2 = self.swipe_path[i + 1]
            
            distance = self.point_line_distance(bomb.x, bomb.y, x1, y1, x2, y2)
            
            if distance < bomb.radius:
                return True
        
        return False
    
    def slice_fruit(self, fruit):
        """Slice a fruit and create particles and sliced fruit halves"""
        # Create sliced fruit halves FIRST (before particles so it appears on top)
        if fruit.sliced_image:
            sliced_fruit = SlicedFruit(fruit.x, fruit.y, fruit.fruit_type, fruit.sliced_image)
            self.sliced_fruits.append(sliced_fruit)
            print(f"🍎 {fruit.fruit_type} kesildi - sliced resim eklendi ({fruit.sliced_image.get_width()}x{fruit.sliced_image.get_height()})")
        else:
            print(f"⚠ {fruit.fruit_type} kesildi ama sliced resmi yok!")
        
        # Create particles (will appear behind sliced fruit) - reduced amount
        for _ in range(5):  # 15'ten 5'e düşürüldü
            self.particles.append(Particle(fruit.x, fruit.y, fruit.color))
        
        # Create yellow fragments (half circles) - reduced amount
        for _ in range(1):  # 3'ten 1'e düşürüldü
            fragment_x = fruit.x + random.randint(-20, 20)
            fragment_y = fruit.y + random.randint(-20, 20)
            for _ in range(2):  # 5'ten 2'ye düşürüldü
                self.particles.append(Particle(fragment_x, fragment_y, YELLOW))
        
        # Update combo
        self.combo += 1
        self.combo_timer = self.combo_timeout
        
        # Score with combo multiplier
        combo_multiplier = max(1, self.combo - 1)
        points = 1 + combo_multiplier
        self.score += points
        
        print(f"💥 Combo: {self.combo}x - Kazanılan puan: {points}")
        
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.swiping = True
                    self.swipe_path = [event.pos]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.swiping = False
                    self.swipe_path = []
            elif event.type == pygame.MOUSEMOTION:
                if self.swiping:
                    self.swipe_path.append(event.pos)
                    
                    # Check if title screen is being sliced
                    if self.show_title_screen:
                        if self.check_title_slice():
                            self.show_title_screen = False
                            self.title_sliced = True
                            print("🎮 Oyun başlıyor!")
                    
                    if not self.game_over and not self.show_title_screen:
                        # Check for bomb slices (GAME OVER!)
                        for bomb in self.bombs:
                            if self.check_bomb_slice(bomb):
                                self.game_over = True
                                print("💣 BOMBA PATLADI! GAME OVER!")
                                return
                        
                        # Check for fruit slices
                        fruits_to_remove = []
                        for fruit in self.fruits:
                            if self.check_slice(fruit):
                                self.slice_fruit(fruit)
                                fruits_to_remove.append(fruit)
                        
                        for fruit in fruits_to_remove:
                            self.fruits.remove(fruit)
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_SPACE:
                    # Restart game
                    self.reset_game()
    
    def reset_game(self):
        """Reset game to start new game"""
        self.fruits = []
        self.bombs = []
        self.sliced_fruits = []
        self.particles = []
        self.score = 0
        self.game_over = False
        self.show_title_screen = False
        self.swipe_path = []
        self.spawn_timer = 0
        self.spawn_interval = 60
        self.bomb_spawn_timer = 0
    
    def check_title_slice(self):
        """Check if title screen text is sliced"""
        if len(self.swipe_path) < 2:
            return False
        
        # Subtitle text position (İkbal and Esmanur)
        subtitle_y = SCREEN_HEIGHT // 2 + 50
        subtitle_x_center = SCREEN_WIDTH // 2
        subtitle_width = 300  # Approximate width of text
        
        # Check if swipe crosses through subtitle area (İkbal and Esmanur)
        for i in range(len(self.swipe_path) - 1):
            x1, y1 = self.swipe_path[i]
            x2, y2 = self.swipe_path[i + 1]
            
            # Check if line crosses through subtitle text area (horizontal slice)
            min_y = min(y1, y2)
            max_y = max(y1, y2)
            
            if subtitle_y - 25 <= min_y <= subtitle_y + 25 or \
               subtitle_y - 25 <= max_y <= subtitle_y + 25 or \
               (min_y < subtitle_y - 25 and max_y > subtitle_y + 25):
                # Check if it's in the horizontal range of the text
                min_x = min(x1, x2)
                max_x = max(x1, x2)
                if (subtitle_x_center - subtitle_width // 2 <= min_x <= subtitle_x_center + subtitle_width // 2) or \
                   (subtitle_x_center - subtitle_width // 2 <= max_x <= subtitle_x_center + subtitle_width // 2) or \
                   (min_x < subtitle_x_center - subtitle_width // 2 and max_x > subtitle_x_center + subtitle_width // 2):
                    return True
        
        return False
    
    def draw_swipe_path(self, screen, path, color=WHITE):
        """Draw a realistic knife/sword swipe path with glow effect"""
        if len(path) < 2:
            return
        
        # Draw multiple layers for a glowing, realistic effect
        # Outer shadow layer (dark)
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            # Draw shadow offset
            shadow_offset = 2
            shadow_color = (20, 20, 20)
            pygame.draw.line(screen, shadow_color, 
                           (x1 + shadow_offset, y1 + shadow_offset),
                           (x2 + shadow_offset, y2 + shadow_offset), 8)
        
        # Middle glow layer (semi-transparent bright)
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            # Bright center
            bright_color = (255, 255, 200)  # Slightly yellow-white
            pygame.draw.line(screen, bright_color, (x1, y1), (x2, y2), 6)
        
        # Inner core (bright white)
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            # Core bright line
            pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)
        
        # Add small circles at points for smoother look
        for point in path:
            x, y = point
            # Outer glow
            pygame.draw.circle(screen, (255, 255, 200), (int(x), int(y)), 4)
            # Inner core
            pygame.draw.circle(screen, color, (int(x), int(y)), 2)
    
    def update(self):
        if self.game_over or self.show_title_screen:
            return  # Don't update if game is over or on title screen
        
        # Spawn fruits
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_fruit()
            self.spawn_timer = 0
            self.spawn_interval = max(30, self.spawn_interval - 1)  # Increase spawn rate over time
        
        # Spawn bombs (less frequently)
        self.bomb_spawn_timer += 1
        if self.bomb_spawn_timer >= self.bomb_spawn_interval:
            self.spawn_bomb()
            self.bomb_spawn_timer = 0
            # Make bombs spawn more frequently as score increases
            self.bomb_spawn_interval = max(180, self.bomb_spawn_interval - 5)
        
        # Update fruits
        for fruit in self.fruits:
            fruit.update()
        
        # Update bombs
        for bomb in self.bombs:
            bomb.update()
        
        # Update sliced fruits
        for sliced_fruit in self.sliced_fruits:
            sliced_fruit.update()
        
        # Remove dead sliced fruits
        self.sliced_fruits = [sf for sf in self.sliced_fruits if sf.is_alive()]
        
        # Update particles
        for particle in self.particles:
            particle.update()
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def draw(self):
        # Draw title screen if showing
        if self.show_title_screen:
            self.draw_title_screen()
            pygame.display.flip()
            return
        
        # Draw top bar (light blue)
        pygame.draw.rect(self.screen, LIGHT_BLUE, (0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT))
        
        # Draw bottom bar (white)
        pygame.draw.rect(self.screen, WHITE, (0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT))
        
        # Draw game area (wooden background)
        game_area_surface = pygame.Surface((SCREEN_WIDTH, GAME_AREA_HEIGHT))
        game_area_surface.blit(self.wood_texture, (0, -GAME_AREA_Y))
        self.screen.blit(game_area_surface, (0, GAME_AREA_Y))
        
        # Draw border between areas
        pygame.draw.line(self.screen, BLACK, (0, TOP_BAR_HEIGHT), (SCREEN_WIDTH, TOP_BAR_HEIGHT), 2)
        pygame.draw.line(self.screen, BLACK, (0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 2)
        
        # Draw fruits (only in game area)
        for fruit in self.fruits:
            fruit.draw(self.screen)
        
        # Draw bombs
        for bomb in self.bombs:
            bomb.draw(self.screen)
        
        # Draw particles (behind sliced fruits)
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw sliced fruits (halves flying apart) - on top of particles
        for sliced_fruit in self.sliced_fruits:
            sliced_fruit.draw(self.screen)
        
        # Draw swipe path (only in game area)
        if len(self.swipe_path) > 1:
            # Filter swipe path to only show in game area
            filtered_path = []
            for point in self.swipe_path:
                x, y = point
                if GAME_AREA_Y <= y <= GAME_AREA_Y + GAME_AREA_HEIGHT:
                    filtered_path.append(point)
            if len(filtered_path) > 1:
                self.draw_swipe_path(self.screen, filtered_path)
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw combo if active
        if self.combo > 1:
            combo_text = self.font_large.render(f"COMBO {self.combo}!", True, YELLOW)
            combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
            # Add semi-transparent background for better readability
            bg_rect = combo_rect.inflate(20, 20)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 150), (0, 0, bg_rect.width, bg_rect.height), border_radius=10)
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(combo_text, combo_rect)
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_title_screen(self):
        """Draw the title/loading screen"""
        # Draw wooden background
        self.screen.blit(self.wood_texture, (0, 0))
        
        # Draw title "Fruit Ninja"
        title_text = self.font_title.render("Fruit Ninja", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Draw shadow for title
        shadow_offset = 3
        shadow_text = self.font_title.render("Fruit Ninja", True, BLACK)
        self.screen.blit(shadow_text, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle "İkbal and Esmanur"
        subtitle_text = self.font_subtitle.render("İkbal and Esmanur", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Draw shadow for subtitle
        shadow_subtitle = self.font_subtitle.render("İkbal and Esmanur", True, BLACK)
        self.screen.blit(shadow_subtitle, (subtitle_rect.x + shadow_offset, subtitle_rect.y + shadow_offset))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw instruction
        instruction_text = self.font_small.render("Keserek başla!", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw swipe path if swiping
        if len(self.swipe_path) > 1:
            self.draw_swipe_path(self.screen, self.swipe_path)
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        # Best score
        best_text = self.font_medium.render(f"Best: {self.best_score}", True, YELLOW)
        best_rect = best_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(best_text, best_rect)
        
        # Restart instruction
        restart_text = self.font_small.render("Press SPACE to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_ui(self):
        """Draw UI elements on top and bottom bars"""
        # Draw score on top left (with icon)
        score_icon_size = 40
        # Draw simple fruit icon (circle as placeholder)
        pygame.draw.circle(self.screen, RED, (25, TOP_BAR_HEIGHT // 2), score_icon_size // 2)
        
        score_text = self.font_large.render(str(self.score), True, BLACK)
        self.screen.blit(score_text, (65, TOP_BAR_HEIGHT // 2 - score_text.get_height() // 2))
        
        # Draw best score below
        best_text = self.font_small.render(f"BEST: {self.best_score}", True, BLACK)
        self.screen.blit(best_text, (25, TOP_BAR_HEIGHT // 2 + 20))
        
        # Draw lives on top right
        x_start = SCREEN_WIDTH - 30
        y_center = TOP_BAR_HEIGHT // 2
        for i in range(MAX_LIVES):
            x_pos = x_start - (i * 35)
            if i < (MAX_LIVES - self.lives):
                # Draw red X for lost lives
                color = RED
            else:
                # Draw blue X for remaining lives
                color = BLUE
            
            # Draw X symbol
            font = pygame.font.Font(None, 36)
            x_text = font.render("X", True, color)
            self.screen.blit(x_text, (x_pos, y_center - x_text.get_height() // 2))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


class MenuScreen:
    """Main menu screen matching Fruit Ninja style with START and SETTINGS buttons."""
    def __init__(self, game: FruitNinja):
        # reuse game resources (screen, wood texture, images, font)
        self.game = game
        self.screen = game.screen
        self.wood_texture = game.wood_texture
        self.fruit_images = game.fruit_images
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Swipe path tracking
        self.swipe_path: List[Tuple[int, int]] = []
        self.swiping = False
        self.watermelon_sliced = False  # Track if watermelon was sliced

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.ninja_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 24)
        self.instruction_font = pygame.font.Font(None, 20)
        
        # Button positions and sizes
        self.start_button_pos = (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50)
        self.start_button_radius = 100
        self.settings_button_pos = (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 20)
        self.settings_button_radius = 70
        
        # Colors
        self.start_color = (30, 144, 255)  # Blue
        self.settings_color = (148, 0, 211)  # Purple
        self.wood_sign_color = (139, 90, 43)  # Light brown for sign
        self.sign_text_color = (69, 39, 19)  # Dark brown for text

    def draw_colored_title(self):
        """Draw FRUIT NINJA title with colorful letters"""
        # FRUIT letters with colors
        fruit_letters = [
            ("F", (148, 0, 211)),  # Purple
            ("R", (255, 0, 0)),    # Red
            ("U", (255, 165, 0)),  # Orange
            ("I", (255, 255, 0)),  # Yellow
            ("T", (0, 255, 0)),    # Green
        ]
        
        # NINJA letters (silver/metallic)
        ninja_letters = ["N", "I", "N", "J", "A"]
        ninja_color = (192, 192, 192)  # Silver
        
        # Draw FRUIT
        x_start = 100
        y_pos = 80
        letter_spacing = 50
        
        for i, (letter, color) in enumerate(fruit_letters):
            # Create text with shadow for 3D effect
            text_surf = self.title_font.render(letter, True, color)
            shadow_surf = self.title_font.render(letter, True, (0, 0, 0))
            
            x_pos = x_start + i * letter_spacing
            # Draw shadow
            self.screen.blit(shadow_surf, (x_pos + 2, y_pos + 2))
            # Draw main text
            self.screen.blit(text_surf, (x_pos, y_pos))
            
            # Add leaves to T
            if letter == "T":
                # Draw small green leaves on top
                leaf_y = y_pos - 10
                pygame.draw.circle(self.screen, (0, 200, 0), (x_pos - 8, leaf_y), 5)
                pygame.draw.circle(self.screen, (0, 200, 0), (x_pos + 8, leaf_y), 5)
        
        # Draw NINJA
        x_start_ninja = x_start + len(fruit_letters) * letter_spacing + 30
        for i, letter in enumerate(ninja_letters):
            text_surf = self.ninja_font.render(letter, True, ninja_color)
            shadow_surf = self.ninja_font.render(letter, True, (0, 0, 0))
            
            x_pos = x_start_ninja + i * letter_spacing
            # Draw shadow
            self.screen.blit(shadow_surf, (x_pos + 2, y_pos + 2))
            # Draw main text
            self.screen.blit(text_surf, (x_pos, y_pos))
        
        # Draw TM symbol
        tm_surf = pygame.font.Font(None, 20).render("™", True, ninja_color)
        self.screen.blit(tm_surf, (x_start_ninja + len(ninja_letters) * letter_spacing + 5, y_pos - 5))

    def point_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return math.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
        
        dx = px - xx
        dy = py - yy
        return math.sqrt(dx * dx + dy * dy)
    
    def check_watermelon_slice(self):
        """Check if swipe path slices the watermelon button"""
        if len(self.swipe_path) < 2:
            return False
        
        # Watermelon button position and radius
        sx, sy = self.start_button_pos
        watermelon_radius = self.start_button_radius * 0.6  # Inner radius where fruit is
        
        # Check if swipe path crosses through watermelon
        for i in range(len(self.swipe_path) - 1):
            x1, y1 = self.swipe_path[i]
            x2, y2 = self.swipe_path[i + 1]
            
            distance = self.point_line_distance(sx, sy, x1, y1, x2, y2)
            
            if distance < watermelon_radius:
                return True
        
        return False
    
    def draw_instruction_sign(self):
        """Draw the wooden instruction sign"""
        sign_x = 50
        sign_y = 150
        sign_width = 150
        sign_height = 60
        
        # Draw sign background
        pygame.draw.rect(self.screen, self.wood_sign_color, 
                        (sign_x, sign_y, sign_width, sign_height))
        
        # Draw border/nails (X marks in corners)
        nail_color = YELLOW
        nail_size = 5
        corners = [
            (sign_x + 5, sign_y + 5),
            (sign_x + sign_width - 5, sign_y + 5),
            (sign_x + 5, sign_y + sign_height - 5),
            (sign_x + sign_width - 5, sign_y + sign_height - 5)
        ]
        for cx, cy in corners:
            # Draw X
            pygame.draw.line(self.screen, nail_color, (cx - nail_size, cy - nail_size), 
                           (cx + nail_size, cy + nail_size), 2)
            pygame.draw.line(self.screen, nail_color, (cx - nail_size, cy + nail_size), 
                           (cx + nail_size, cy - nail_size), 2)
        
        # Draw text
        line1 = self.instruction_font.render("TAP FRUIT", True, self.sign_text_color)
        line2 = self.instruction_font.render("TO BEGIN", True, self.sign_text_color)
        
        line1_rect = line1.get_rect(center=(sign_x + sign_width // 2, sign_y + sign_height // 2 - 10))
        line2_rect = line2.get_rect(center=(sign_x + sign_width // 2, sign_y + sign_height // 2 + 10))
        
        self.screen.blit(line1, line1_rect)
        self.screen.blit(line2, line2_rect)

    def draw_circular_button(self, center, radius, color, text, fruit_type=None, glow=True):
        """Draw a circular button with text around the ring and fruit in center"""
        cx, cy = center
        
        # Draw glowing outer ring
        if glow:
            for i in range(3):
                glow_radius = radius + i * 3
                glow_alpha = 100 - i * 30
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_radius, glow_radius), glow_radius, 5)
                self.screen.blit(glow_surf, (cx - glow_radius, cy - glow_radius))
        
        # Draw main ring (thick)
        pygame.draw.circle(self.screen, color, center, radius, 8)
        
        # Draw text around the ring (top and bottom, as in the image)
        # Text appears twice: once right-side up at top, once upside down at bottom
        text_no_spaces = text.replace(" ", "")
        if len(text_no_spaces) > 0:
            text_radius = radius + 20
            
            # Draw top arc (right-side up)
            text_angle_step = 180 / len(text_no_spaces)
            for i, char in enumerate(text_no_spaces):
                # Start from left, go to right (top half)
                angle = math.radians(i * text_angle_step - 90)
                
                # Calculate position on circle
                text_x = cx + math.cos(angle) * text_radius
                text_y = cy + math.sin(angle) * text_radius
                
                # Render character
                char_surf = self.button_font.render(char, True, color)
                
                # Rotate character to follow circle tangent
                rotation_angle = math.degrees(angle) + 90
                rotated_char = pygame.transform.rotate(char_surf, rotation_angle)
                char_rect = rotated_char.get_rect(center=(int(text_x), int(text_y)))
                self.screen.blit(rotated_char, char_rect)
            
            # Draw bottom arc (upside down - same text)
            for i, char in enumerate(text_no_spaces):
                # Start from right, go to left (bottom half)
                angle = math.radians(180 - i * text_angle_step - 90)
                
                # Calculate position on circle
                text_x = cx + math.cos(angle) * text_radius
                text_y = cy + math.sin(angle) * text_radius
                
                # Render character (upside down)
                char_surf = self.button_font.render(char, True, color)
                
                # Rotate character to follow circle tangent (upside down)
                rotation_angle = math.degrees(angle) + 90 + 180
                rotated_char = pygame.transform.rotate(char_surf, rotation_angle)
                char_rect = rotated_char.get_rect(center=(int(text_x), int(text_y)))
                self.screen.blit(rotated_char, char_rect)
        
        # Draw fruit in center if available
        if fruit_type and fruit_type in self.fruit_images:
            fruit_img = self.fruit_images[fruit_type].get("whole")
            if fruit_img:
                inner_radius = int(radius * 0.6)
                scale = inner_radius * 1.8 / max(fruit_img.get_width(), fruit_img.get_height())
                w = int(fruit_img.get_width() * scale)
                h = int(fruit_img.get_height() * scale)
                img_s = pygame.transform.smoothscale(fruit_img, (w, h))
                img_rect = img_s.get_rect(center=center)
                self.screen.blit(img_s, img_rect)

    def run(self):
        """Run the menu screen"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.swiping = True
                        self.swipe_path = [event.pos]
                        mx, my = event.pos
                        
                        # Check START button
                        sx, sy = self.start_button_pos
                        if (mx - sx) ** 2 + (my - sy) ** 2 <= self.start_button_radius ** 2:
                            # Play slice animation
                            self.play_slice_animation(self.start_button_pos)
                            return "START"
                        
                        # Check SETTINGS button
                        setx, sety = self.settings_button_pos
                        if (mx - setx) ** 2 + (my - sety) ** 2 <= self.settings_button_radius ** 2:
                            return "SETTINGS"
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.swiping = False
                        self.swipe_path = []
                elif event.type == pygame.MOUSEMOTION:
                    if self.swiping:
                        self.swipe_path.append(event.pos)
                        # Check if swipe path slices the watermelon
                        if not self.watermelon_sliced:
                            if self.check_watermelon_slice():
                                self.watermelon_sliced = True
                                # Play slice animation (this will show the animation)
                                self.play_slice_animation(self.start_button_pos)
                                return "START"

            # Draw background
            self.screen.blit(self.wood_texture, (0, 0))
            
            # Draw title
            self.draw_colored_title()
            
            # Draw instruction sign
            self.draw_instruction_sign()
            
            # Draw START button
            self.draw_circular_button(
                self.start_button_pos,
                self.start_button_radius,
                self.start_color,
                "TAP HERE TO START",
                "watermelon"
            )
            
            # Draw SETTINGS button
            self.draw_circular_button(
                self.settings_button_pos,
                self.settings_button_radius,
                self.settings_color,
                "SETTINGS",
                "kiwi"
            )
            
            # Draw swipe path (knife trail)
            if len(self.swipe_path) > 1:
                self.game.draw_swipe_path(self.screen, self.swipe_path)

            pygame.display.flip()
            self.clock.tick(60)

    def play_slice_animation(self, center_pos):
        """Show sliced-fruit animation at `center_pos` matching game style."""
        cx, cy = center_pos

        # Prepare sliced fruit image (prefer watermelon)
        sliced_img = None
        watermelon_color = (0, 180, 0)  # Green color for watermelon
        if "watermelon" in self.fruit_images:
            sliced_img = self.fruit_images["watermelon"].get("sliced")

        # Create sliced fruit with slower speed for better visibility
        sliced = SlicedFruit(cx, cy, "watermelon", sliced_img)
        # Reduce velocities for slower, more visible movement
        sliced.half1_vx *= 0.6
        sliced.half1_vy *= 0.6
        sliced.half2_vx *= 0.6
        sliced.half2_vy *= 0.6
        particles: List[Particle] = []

        # Create particles (reduced amount for menu)
        # 2 particles with watermelon color (reduced from 5)
        for _ in range(2):
            particles.append(Particle(cx, cy, watermelon_color))
        
        # Create yellow fragments (reduced)
        # 1 fragment with 1 yellow particle (reduced from 2)
        for _ in range(1):
            fragment_x = cx + random.randint(-20, 20)
            fragment_y = cy + random.randint(-20, 20)
            particles.append(Particle(fragment_x, fragment_y, YELLOW))

        # Play animation for duration (longer to see sliced fruit better)
        frames = 90  # Longer duration to see sliced fruit clearly
        for frame in range(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Draw background and menu elements
            self.screen.blit(self.wood_texture, (0, 0))
            self.draw_colored_title()
            self.draw_instruction_sign()
            
            # Draw buttons
            self.draw_circular_button(
                self.start_button_pos,
                self.start_button_radius,
                self.start_color,
                "TAP HERE TO START",
                "watermelon"
            )
            self.draw_circular_button(
                self.settings_button_pos,
                self.settings_button_radius,
                self.settings_color,
                "SETTINGS",
                "kiwi"
            )

            # Update and draw
            # Update sliced fruit
            sliced.update()
            
            # Update particles
            for p in particles:
                p.update()
            
            # Remove dead particles
            particles = [p for p in particles if p.is_alive()]
            
            # Draw particles first (behind sliced fruit) - reduced visibility
            for p in particles:
                p.draw(self.screen)
            
            # Draw sliced fruit on top (more prominent)
            if sliced.is_alive():
                sliced.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)
            
            # Stop early if everything is gone
            if not sliced.is_alive() and len(particles) == 0:
                break



if __name__ == "__main__":
    game = FruitNinja()
    menu = MenuScreen(game)
    selected = menu.run()
    if selected is None:
        pygame.quit()
        sys.exit()
    # You could change game behaviour based on `selected`
    print(f"Selected mode: {selected}")
    # Skip title screen if START was selected
    if selected == "START":
        game.show_title_screen = False
    game.run()
