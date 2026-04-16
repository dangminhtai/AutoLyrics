import time
import sys
import pygame
import os
import msvcrt
from colorama import Fore, Style
from .utils import clear_screen, hide_cursor, show_cursor, move_to_top, get_terminal_width, get_visible_width
from .config import CONFIG

class LyricPlayer:
    def __init__(self, music_path=None, subtitles=None):
        self.music_path = music_path if music_path else CONFIG.MUSIC_PATH
        self.subtitles = subtitles if subtitles else []
        self.current_sub_idx = 0
        self.window_size = CONFIG.WINDOW_SIZE
        self.last_frame = "" 
        self.start_time_offset = 0.0 
        self.total_duration = 0.0
        self.is_paused = False
        
        # Get total duration for the progress bar
        if os.path.exists(self.music_path):
            pygame.mixer.init()
            try:
                sound = pygame.mixer.Sound(self.music_path)
                self.total_duration = sound.get_length()
            except Exception:
                if self.subtitles:
                    self.total_duration = self.subtitles[-1]['end']

    def play(self):
        """Start the music and the lyric rendering loop."""
        if not os.path.exists(self.music_path):
            print(f"{CONFIG.COLOR_ERROR}Không tìm thấy file nhạc: {self.music_path}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play()

        clear_screen()
        hide_cursor()

        try:
            # Main playback loop
            while pygame.mixer.music.get_busy() or self.is_paused or pygame.mixer.music.get_pos() != -1:
                self._handle_input()
                
                # Calculate current time based on play head + manual offset
                # get_pos resets to 0 when unpaused or after seeking (play(start=...))
                current_time = self.start_time_offset + (pygame.mixer.music.get_pos() / 1000.0)
                
                if current_time >= 0:
                    self._render_frame(current_time)
                
                time.sleep(CONFIG.FRAME_DELAY)
        except KeyboardInterrupt:
            pygame.mixer.music.stop()
        finally:
            show_cursor()
            clear_screen()
            print(f"{CONFIG.COLOR_ERROR}Đã dừng.")

    def _handle_input(self):
        """Non-blocking check for keyboard input (Windows only)."""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Handle standard keys
            if key == b' ': # Space to toggle pause
                if self.is_paused:
                    pygame.mixer.music.unpause()
                    self.is_paused = False
                else:
                    pygame.mixer.music.pause()
                    self.is_paused = True
            elif key in (b'r', b'R'): # R to restart
                self._seek(-self.total_duration) # Seek to start
                if self.is_paused:
                    pygame.mixer.music.unpause()
                    self.is_paused = False

            # Handling special keys (Arrow keys)
            elif key in (b'\x00', b'\xe0'):
                sub_key = msvcrt.getch()
                if sub_key == b'K': # Left Arrow
                    self._seek(-CONFIG.SEEK_SECONDS)
                elif sub_key == b'M': # Right Arrow
                    self._seek(CONFIG.SEEK_SECONDS)

    def _seek(self, seconds):
        """Jump forward or backward in the song."""
        current_pos = self.start_time_offset + (pygame.mixer.music.get_pos() / 1000.0)
        new_pos = max(0, min(current_pos + seconds, self.total_duration - 1))
        
        self.start_time_offset = new_pos
        pygame.mixer.music.play(start=new_pos)
        
        # Reset state for correct redraw
        self.last_frame = ""
        self.current_sub_idx = 0

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

        term_width = get_terminal_width()
        display_idx = active_idx if active_idx != -1 else self.current_sub_idx
        start_view = max(0, display_idx - 2)
        
        output_lines = [""] # Header spacing
        
        for i in range(start_view, start_view + self.window_size):
            if i < len(self.subtitles):
                sub = self.subtitles[i]
                
                # Prefix based on active status
                prefix = f"{CONFIG.COLOR_INDICATOR}{CONFIG.ACTIVE_INDICATOR}{Style.RESET_ALL}" if i == active_idx else "  "
                
                if i == active_idx:
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
                    line_content = f"{CONFIG.COLOR_ACTIVE}{typed}{Style.DIM}{rem}{Style.RESET_ALL}"
                elif i < display_idx:
                    line_content = f"{CONFIG.COLOR_PAST}{sub['text']}{Style.RESET_ALL}"
                else:
                    line_content = f"{CONFIG.COLOR_FUTURE}{sub['text']}{Style.RESET_ALL}"
                
                full_line = f"{prefix}{line_content}"
                visible_width = get_visible_width(full_line)
                padding = max(0, (term_width - visible_width) // 2)
                output_lines.append(" " * padding + full_line + "\033[K")
            else:
                output_lines.append('\033[K')

        # Add Progress Bar
        output_lines.append("")
        progress_bar = self._create_progress_bar(current_time, term_width)
        padding_bar = max(0, (term_width - get_visible_width(progress_bar)) // 2)
        output_lines.append(" " * padding_bar + progress_bar + "\033[K")

        current_frame_content = '\n'.join(output_lines)
        if current_frame_content != self.last_frame:
            move_to_top()
            sys.stdout.write(current_frame_content + '\n')
            sys.stdout.flush()
            self.last_frame = current_frame_content

    def _create_progress_bar(self, current_time, width):
        """Create a visual progress bar string."""
        bar_width = min(CONFIG.PROGRESS_BAR_WIDTH, width - 20)
        if bar_width < 10: return ""
        
        percent = min(1.0, current_time / self.total_duration) if self.total_duration > 0 else 0
        filled = int(bar_width * percent)
        bar = f"{CONFIG.COLOR_PROGRESS_BAR}{'█' * filled}{Style.DIM}{'░' * (bar_width - filled)}{Style.RESET_ALL}"
        
        def fmt_time(s):
            m, s = divmod(int(s), 60)
            return f"{m:02d}:{s:02d}"
        
        time_str = f"{fmt_time(current_time)} / {fmt_time(self.total_duration)}"
        return f"{bar} {time_str}"
