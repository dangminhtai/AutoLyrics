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
        self.last_frame = "" # For dirty checking

    def play(self):
        """Start the music and the lyric rendering loop."""
        if not os.path.exists(self.music_path):
            print(f"Không tìm thấy file nhạc: {self.music_path}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play()

        clear_screen()
        hide_cursor()

        try:
            while pygame.mixer.music.get_busy():
                # get_pos is more reliable for staying in sync with audio
                current_time = pygame.mixer.music.get_pos() / 1000.0
                
                if current_time >= 0:
                    self._render_frame(current_time)
                
                time.sleep(0.01) # Faster update loop
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
        for i in range(self.current_sub_idx, len(self.subtitles)):
            sub = self.subtitles[i]
            if sub['start'] <= current_time <= sub['end']:
                active_idx = i
                self.current_sub_idx = i
                break
            elif sub['start'] > current_time:
                break
        
        if active_idx == -1:
            for i, sub in enumerate(self.subtitles):
                if sub['start'] <= current_time <= sub['end']:
                    active_idx = i
                    self.current_sub_idx = i
                    break

        # Redraw logic with window calculation
        display_idx = active_idx if active_idx != -1 else self.current_sub_idx
        start_view = max(0, display_idx - 2)
        
        output_lines = []
        for i in range(start_view, start_view + self.window_size):
            if i < len(self.subtitles):
                sub = self.subtitles[i]
                if i == active_idx:
                    # Highlight words based on timing
                    if sub.get('words'):
                        num_chars = 0
                        words_list = sub['words']
                        for j, w in enumerate(words_list):
                            if current_time >= w['end']:
                                num_chars += len(w['word']) + (1 if j < len(words_list) - 1 else 0)
                            elif current_time >= w['start']:
                                word_dur = max(w['end'] - w['start'], 0.001)
                                word_elapsed = current_time - w['start']
                                word_prog = min(1.0, word_elapsed / word_dur)
                                num_chars += int(len(w['word']) * word_prog)
                                break
                            else:
                                break
                    else:
                        duration = max(sub['end'] - sub['start'], 0.001)
                        elapsed = current_time - sub['start']
                        progress = max(0.0, min(1.0, elapsed / duration))
                        num_chars = int(len(sub['text']) * progress)
                    
                    typed = sub['text'][:num_chars]
                    rem = sub['text'][num_chars:]
                    line = f"{Fore.YELLOW}{typed}{Style.DIM}{rem}{Style.RESET_ALL}\033[K"
                elif i < display_idx:
                    line = f"{Fore.WHITE}{sub['text']}{Style.RESET_ALL}\033[K"
                else:
                    line = f"{Style.DIM}{sub['text']}{Style.RESET_ALL}\033[K"
                output_lines.append(line)
            else:
                output_lines.append('\033[K')

        current_frame_content = '\n'.join(output_lines)
        
        # Dirty checking: Only write to terminal if content actually changed
        if current_frame_content != self.last_frame:
            move_to_top()
            sys.stdout.write(current_frame_content + '\n')
            sys.stdout.flush()
            self.last_frame = current_frame_content
