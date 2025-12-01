#!/usr/bin/env python3
"""
Script to update fruit_ninja.py with language support and other improvements
"""

import re

def update_fruit_ninja():
    with open('fruit_ninja.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add language attribute after load_settings in __init__
    pattern1 = r'(        self\.game_mode = "Classic"  # Classic, Zen, Arcade\n        self\.load_settings\(\))'
    replacement1 = r'\1\n        self.language = "eng"  # "eng" for English, "tr" for Turkish'
    content = re.sub(pattern1, replacement1, content)
    
    # 2. Update load_settings to load language and apply difficulty
    pattern2 = r'(                self\.difficulty = data\.get\("difficulty", self\.difficulty\))'
    replacement2 = r'\1\n                self.language = data.get("language", self.language)\n                # Apply loaded difficulty to game\n                self.set_difficulty(self.difficulty)'
    content = re.sub(pattern2, replacement2, content)
    
    # 3. Update save_settings to include language
    pattern3 = r'(            "difficulty": self\.difficulty,\n        \})'
    replacement3 = r'\1'.replace('"difficulty": self.difficulty,\n        }', '"difficulty": self.difficulty,\n            "language": self.language,\n        }')
    content = re.sub(pattern3, replacement3, content)
    
    # 4. Update show_settings_screen to add language support
    pattern4 = r'(        difficulties = \["Easy", "Normal", "Hard", "Extreme"\]\n        difficulty_index = difficulties\.index\(self\.game\.difficulty\) if self\.game\.difficulty in difficulties else 1\n        active_field = "none"  # "name" for editing)'
    replacement4 = r'\1\n        languages = ["English", "Turkish"]\n        language_index = 0 if self.game.language == "eng" else 1'
    content = re.sub(pattern4, replacement4, content)
    
    # 5. Update panel height to accommodate Language field
    pattern5 = r'(        panel_height = )[0-9]+'
    replacement5 = r'\g<1>480'
    content = re.sub(pattern5, replacement5, content)
    
    # 6. Add language click handler in mouse event
    pattern6 = r'(                    # Difficulty change\n                    elif panel_rect\.left \+ 140 <= mx <= panel_rect\.right - 80 and panel_rect\.top \+ 290 <= my <= panel_rect\.top \+ 320:\n                        difficulty_index = \(difficulty_index \+ 1\) % len\(difficulties\))'
    replacement6 = r'\1\n                    # Language change\n                    elif panel_rect.left + 140 <= mx <= panel_rect.right - 80 and panel_rect.top + 360 <= my <= panel_rect.top + 390:\n                        language_index = (language_index + 1) % len(languages)'
    content = re.sub(pattern6, replacement6, content)
    
    # 7. Add Language row in draw section (after Difficulty)
    pattern7 = r'(            # Difficulty level row\n            difficulty_label = self\.font_small\.render\("Seviye:", True, \(70, 40, 20\)\)\n            difficulty_value = self\.font_small\.render\(difficulties\[difficulty_index\], True, YELLOW\)\n            self\.screen\.blit\(difficulty_label, \(panel_rect\.left \+ 40, panel_rect\.top \+ 290\)\)\n            self\.screen\.blit\(difficulty_value, \(panel_rect\.left \+ 140, panel_rect\.top \+ 290\)\))'
    replacement7 = r'''\1

            # Language row
            language_label = self.font_small.render("Language:", True, (70, 40, 20))
            language_value = self.font_small.render(languages[language_index], True, YELLOW)
            self.screen.blit(language_label, (panel_rect.left + 40, panel_rect.top + 360))
            self.screen.blit(language_value, (panel_rect.left + 140, panel_rect.top + 360))'''
    content = re.sub(pattern7, replacement7, content)
    
    # 8. Update settings save to include language
    pattern8 = r'(        # Save back to game object and persist\n        self\.game\.player_name = name_text or "Player"\n        self\.game\.music_enabled = music_on\n        self\.game\.sfx_enabled = music_on\n        self\.game\.difficulty = difficulties\[difficulty_index\])'
    replacement8 = r'\1\n        self.game.language = "eng" if language_index == 0 else "tr"'
    content = re.sub(pattern8, replacement8, content)
    
    # 9. Update set_difficulty to be called after settings save
    pattern9 = r'(        self\.game\.language = "eng" if language_index == 0 else "tr"\n        if hasattr\(self\.game, "save_settings"\):\n            self\.game\.save_settings\(\))'
    replacement9 = r'\1\n        # Apply the selected difficulty\n        self.game.set_difficulty(self.game.difficulty)'
    content = re.sub(pattern9, replacement9, content)
    
    # 10. Translate "Seviye" to "Level" and other Turkish text to English
    content = content.replace('"Seviye:"', '"Level:"')
    content = content.replace('draw_slider_row(\n                panel_rect.top + 130,\n                "Sound",', 'draw_slider_row(\n                panel_rect.top + 130,\n                "Sound",')
    
    with open('fruit_ninja.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ fruit_ninja.py updated successfully!")

if __name__ == "__main__":
    update_fruit_ninja()
