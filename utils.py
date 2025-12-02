import pygame
import os
import random
from typing import List, Dict, Tuple

# Constants
IMAGES_FOLDER = "images"
SOUND_FOLDER = "sound"
FRUIT_SIZE = 80
FRUIT_MIN_SIZE = 70
SLICED_FRUIT_SIZE = 90
BROWN = (101, 67, 33)
DARK_BROWN = (69, 39, 19)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Map variant/alias names from images/fruit to canonical fruit types
FRUIT_ALIASES = {
    "sandia": "watermelon",
    # "basaha" kendi tipi olarak kalsın; pineapple ile karışmasın
    # others map to themselves by default (apple, banana, peach, basaha, etc.)
}

def create_wood_texture():
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

def load_sounds():
    """Load all sound effects from sound folder (slice, bomb, etc.)"""
    sounds = {}
    # Initialize mixer if possible
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception as e:
        print(f"⚠ Ses sistemi başlatılamadı: {e}")
        return sounds

    if not os.path.exists(SOUND_FOLDER):
        print(f"'{SOUND_FOLDER}' klasörü bulunamadı. Sesler kapalı olacak.")
        return sounds

    for filename in os.listdir(SOUND_FOLDER):
        name_lower = filename.lower()
        if not name_lower.endswith((".wav", ".ogg", ".mp3")):
            continue
        sound_name = os.path.splitext(name_lower)[0]  # e.g. slice.wav -> slice
        path = os.path.join(SOUND_FOLDER, filename)
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(0.6)
            sounds[sound_name] = snd
            print(f"🔊 Ses yüklendi: {sound_name} ({filename})")
        except Exception as e:
            print(f"✗ Ses yüklenemedi {path}: {e}")

    if not sounds:
        print("⚠ Ses dosyası bulunamadı. Sesler kapalı.")

    return sounds

def load_fruit_images():
    """Load fruit images from images folder"""
    fruit_images = {}
    
    # Check if images folder exists
    if not os.path.exists(IMAGES_FOLDER):
        print(f"'{IMAGES_FOLDER}' klasörü bulunamadı. Renkli daireler kullanılacak.")
        return fruit_images
    
    # Automatically detect all fruit images in the folder
    # First: scan PNG files directly under images (canonical sprites)
    top_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith('.png')]
    
    # Extract fruit types from filenames
    # We store relative paths from IMAGES_FOLDER so that we can also support subfolders
    fruit_type_map = {}  # Maps fruit type to file paths and variants
    
    for filename in top_files:
        rel_path = filename  # relative to IMAGES_FOLDER
        name_lower = filename.lower().replace('.png', '')
        
        # Check if it's a sliced image
        if '_sliced' in name_lower:
            # Extract fruit type (before _sliced)
            fruit_type = name_lower.split('_sliced')[0]
            # Remove any numbers at the end (like pineapple_sliced1 -> pineapple)
            fruit_type = ''.join([c for c in fruit_type if not c.isdigit()])
            
            if fruit_type not in fruit_type_map:
                fruit_type_map[fruit_type] = {"whole": None, "whole_variants": [], "sliced": []}
            
            # Handle multiple sliced images (like pineapple_sliced1, pineapple_sliced2)
            fruit_type_map[fruit_type]["sliced"].append(rel_path)
        else:
            # This is a whole fruit image
            fruit_type = name_lower
            
            if fruit_type not in fruit_type_map:
                fruit_type_map[fruit_type] = {"whole": None, "whole_variants": [], "sliced": []}
            
            # Default whole image and also a variant
            fruit_type_map[fruit_type]["whole"] = rel_path
            fruit_type_map[fruit_type]["whole_variants"].append(rel_path)
    
    # Second: scan images/fruit subfolder for high-quality variants and halves
    fruit_subdir = os.path.join(IMAGES_FOLDER, "fruit")
    if os.path.exists(fruit_subdir):
        for filename in os.listdir(fruit_subdir):
            if not filename.lower().endswith(".png"):
                continue
            rel_path = os.path.join("fruit", filename)  # relative to IMAGES_FOLDER
            name_lower = filename.lower().replace(".png", "")
            
            # apple-1 -> apple, sandia-2 -> sandia, etc.
            parts = name_lower.split("-")
            base_name = parts[0]
            suffix = parts[1] if len(parts) > 1 else None
            # Map aliases (sandia -> watermelon, basaha -> pineapple, ...)
            fruit_type = FRUIT_ALIASES.get(base_name, base_name)
            
            if fruit_type not in fruit_type_map:
                fruit_type_map[fruit_type] = {
                    "whole": None,
                    "whole_variants": [],
                    "sliced": [],
                    "half1": None,
                    "half2": None,
                }

            # Files ending with -1 / -2 are the sliced halves.
            # Others are high-quality whole variants.
            if suffix == "1":
                fruit_type_map[fruit_type]["half1"] = rel_path
            elif suffix == "2":
                fruit_type_map[fruit_type]["half2"] = rel_path
            else:
                fruit_type_map[fruit_type]["whole_variants"].append(rel_path)
                # If no main whole yet, use the first variant
                if fruit_type_map[fruit_type]["whole"] is None:
                    fruit_type_map[fruit_type]["whole"] = rel_path
    
    # Load all detected fruit images
    for fruit_type, files in fruit_type_map.items():
        whole_imgs: List[pygame.Surface] = []
        sliced_img = None
        half_imgs: List[pygame.Surface] = []
        
        # Load all whole fruit variants (top-level + images/fruit)
        whole_paths = files.get("whole_variants") or []
        if not whole_paths and files.get("whole"):
            whole_paths = [files["whole"]]
        
        for rel_path in whole_paths:
            whole_path = os.path.join(IMAGES_FOLDER, rel_path)
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
                    print(f"  ⚠ {fruit_type} ({rel_path}) çok küçüktü, minimum boyuta ölçeklendi")
                
                whole_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))
                whole_imgs.append(whole_img)
                print(f"✓ Yüklendi: {fruit_type} whole ({rel_path}) {original_width}x{original_height} -> {new_width}x{new_height}")
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
        
        # Load sliced halves from images/fruit (e.g. apple-1.png, apple-2.png)
        for key in ("half1", "half2"):
            rel = files.get(key)
            if not rel:
                continue
            half_path = os.path.join(IMAGES_FOLDER, rel)
            try:
                loaded_img = pygame.image.load(half_path).convert_alpha()
                original_width, original_height = loaded_img.get_size()
                # Scale halves similarly to sliced images
                max_dimension = max(original_width, original_height)
                scale = SLICED_FRUIT_SIZE / max_dimension
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                half_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))
                half_imgs.append(half_img)
                print(f"✓ Yüklendi: {fruit_type} half ({rel}) {original_width}x{original_height} -> {new_width}x{new_height}")
            except Exception as e:
                print(f"✗ Hata yükleme {half_path}: {e}")

        # Only add if we have whole images and at least one way to render sliced state
        # (either a full sliced sprite or two half images)
        if whole_imgs and (sliced_img or half_imgs):
            fruit_images[fruit_type] = {
                "whole": whole_imgs[0],          # primary image
                "whole_variants": whole_imgs,    # all variants
                "sliced": sliced_img,
                "halves": half_imgs if half_imgs else None,
            }
            print(f"  ✓ {fruit_type} oyuna eklendi (gerçek meyve görselleri yüklendi)")
        elif whole_imgs:
            print(f"  ⚠ {fruit_type} atlandı (kesilmiş veya yarım görseli yok)")
    
    print(f"\n🎮 Toplam {len(fruit_images)} meyve tipi yüklendi: {', '.join(fruit_images.keys())}")
    
    if not fruit_images:
        print(f"⚠ '{IMAGES_FOLDER}' klasöründe meyve resmi bulunamadı. Renkli daireler kullanılacak.")
    
    return fruit_images
