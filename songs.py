import time
import sys
import pygame
import os
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal support
init(autoreset=True)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    subtitles = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            text = ' '.join(lines[2:])

            if ' --> ' in time_line:
                start_str, end_str = time_line.split(' --> ')
                subtitles.append({
                    'start': to_seconds(start_str),
                    'end': to_seconds(end_str),
                    'text': text
                })

    return subtitles


def to_seconds(t):
    # Handle both ":" and "," or "."
    parts = t.replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def play(subs):
    pygame.mixer.init()
    if not os.path.exists("assets/songs.mp3"):
        print("Không tìm thấy file nhạc assets/songs.mp3")
        return
        
    pygame.mixer.music.load("assets/songs.mp3")
    pygame.mixer.music.play()

    # Clear terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        current_sub_idx = -1
        while pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000.0
            
            # Find the active subtitle index
            active_idx = -1
            for i, sub in enumerate(subs):
                if sub['start'] <= current_time <= sub['end']:
                    active_idx = i
                    break
                elif sub['start'] > current_time:
                    break
            
            # Only redraw if time has passed or index changed to minimize flicker
            # Move cursor to top-left to redraw
            sys.stdout.write('\033[H')
            
            # Show a window of lyrics (e.g., 2 previous, current, 2 next)
            window_size = 5
            start_view = max(0, active_idx - 2) if active_idx != -1 else max(0, current_sub_idx - 2)
            
            for i in range(start_view, start_view + window_size):
                if i < len(subs):
                    sub = subs[i]
                    if i == active_idx:
                        # Typing effect for active line
                        duration = sub['end'] - sub['start']
                        elapsed = current_time - sub['start']
                        progress = min(1.0, elapsed / duration)
                        num_chars = int(len(sub['text']) * progress)
                        
                        typed = sub['text'][:num_chars]
                        rem = sub['text'][num_chars:]
                        
                        # Current line: Yellow for typed part, Dim for remaining
                        sys.stdout.write(f"{Fore.YELLOW}{typed}{Style.DIM}{rem}{Style.RESET_ALL}\033[K\n")
                    elif i < active_idx or (active_idx == -1 and i <= current_sub_idx):
                        # Past lines: White
                        sys.stdout.write(f"{Fore.WHITE}{sub['text']}{Style.RESET_ALL}\033[K\n")
                    else:
                        # Future lines: Dim
                        sys.stdout.write(f"{Style.DIM}{sub['text']}{Style.RESET_ALL}\033[K\n")
                else:
                    # Empty line to maintain window size
                    sys.stdout.write('\033[K\n')

            if active_idx != -1:
                current_sub_idx = active_idx
                
            sys.stdout.flush()
            time.sleep(0.01)

    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("\n\n" + Fore.RED + "Đã dừng.")

if __name__ == "__main__":
    if os.path.exists("assets/lyrics.srt"):
        subs = parse_srt("assets/lyrics.srt")
        play(subs)
    else:
        print("Không tìm thấy file subtitle assets/lyrics.srt")