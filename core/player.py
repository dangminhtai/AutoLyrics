import time
import sys
import pygame
import os
from colorama import Fore, Style
from .utils import clear_screen, hide_cursor, show_cursor, move_to_top

class LyricPlayer:
    def __init__(self, music_path, subtitles):
        self.music_path = music_path
        self.subtitles = subtitles
        self.current_sub_idx = 0
        self.window_size = 5
        self.cursor_char = "▌"

    def play(self):
        """Start the music and the lyric rendering loop."""
        if not os.path.exists(self.music_path):
            print(f"Không tìm thấy file nhạc: {self.music_path}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play()

        start_time = time.time()
        clear_screen()
        hide_cursor()

        try:
            while pygame.mixer.music.get_busy():
                current_time = time.time() - start_time
                self._render_frame(current_time)
                time.sleep(0.016)  # ~60 FPS
        except KeyboardInterrupt:
            pygame.mixer.music.stop()
        finally:
            show_cursor()
            clear_screen()
            print(Fore.RED + "Đã dừng.")

    def _render_frame(self, current_time):
        """Find the active subtitle and render the terminal frame."""
        # Find active index
        active_idx = -1
        # Optimize: search from current index
        for i in range(self.current_sub_idx, len(self.subtitles)):
            sub = self.subtitles[i]
            if sub['start'] <= current_time <= sub['end']:
                active_idx = i
                self.current_sub_idx = i
                break
            elif sub['start'] > current_time:
                break
        
        # Fallback if no match found (e.g. rewind or gap)
        if active_idx == -1:
            for i, sub in enumerate(self.subtitles):
                if sub['start'] <= current_time <= sub['end']:
                    active_idx = i
                    self.current_sub_idx = i
                    break

        # Rendering
        move_to_top()
        display_idx = active_idx if active_idx != -1 else self.current_sub_idx
        start_view = max(0, display_idx - 2)
        
        output = []
        for i in range(start_view, start_view + self.window_size):
            if i < len(self.subtitles):
                sub = self.subtitles[i]
                if i == active_idx:
                    # Typing effect with fake cursor
                    duration = max(sub['end'] - sub['start'], 0.001)
                    elapsed = current_time - sub['start']
                    progress = max(0.0, min(1.0, elapsed / duration))
                    
                    num_chars = int(len(sub['text']) * progress)
                    typed = sub['text'][:num_chars]
                    rem = sub['text'][num_chars:]
                    
                    line = f"{Fore.YELLOW}{typed}{self.cursor_char}{Style.DIM}{rem}{Style.RESET_ALL}\033[K"
                    output.append(line)
                elif i < display_idx:
                    # Past lines
                    output.append(f"{Fore.WHITE}{sub['text']}{Style.RESET_ALL}\033[K")
                else:
                    # Future lines
                    output.append(f"{Style.DIM}{sub['text']}{Style.RESET_ALL}\033[K")
            else:
                output.append('\033[K')

        sys.stdout.write('\n'.join(output) + '\n')
        sys.stdout.flush()
