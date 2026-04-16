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

    # Clear terminal screen and hide cursor
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.stdout.write('\033[?25l') 
    sys.stdout.flush()
    
    try:
        current_sub_idx = 0
        while pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000.0
            
            active_idx = -1
            for i in range(current_sub_idx, len(subs)):
                sub = subs[i]
                if sub['start'] <= current_time <= sub['end']:
                    active_idx = i
                    current_sub_idx = i
                    break
                elif sub['start'] > current_time:
                    break
            
            if active_idx == -1 and current_time < subs[current_sub_idx]['start']:
                for i, sub in enumerate(subs):
                    if sub['start'] <= current_time <= sub['end']:
                        active_idx = i
                        current_sub_idx = i
                        break
                    elif sub['start'] > current_time:
                        break

            # Move cursor to top-left to redraw
            sys.stdout.write('\033[H')
            
            window_size = 5
            display_idx = active_idx if active_idx != -1 else current_sub_idx
            start_view = max(0, display_idx - 2)
            
            output = []
            cursor_pos = None
            
            for i in range(start_view, start_view + window_size):
                row_in_window = i - start_view
                if i < len(subs):
                    sub = subs[i]
                    if i == active_idx:
                        duration = sub['end'] - sub['start']
                        elapsed = current_time - sub['start']
                        progress = min(1.0, elapsed / (duration if duration > 0 else 0.1))
                        num_chars = int(len(sub['text']) * progress)
                        
                        typed = sub['text'][:num_chars]
                        rem = sub['text'][num_chars:]
                        
                        line = f"{Fore.YELLOW}{typed}{Style.DIM}{rem}{Style.RESET_ALL}\033[K"
                        output.append(line)
                        # Save cursor position: row is 1-indexed, col is 1-indexed
                        cursor_pos = (row_in_window + 1, num_chars + 1)
                    elif i < display_idx:
                        line = f"{Fore.WHITE}{sub['text']}{Style.RESET_ALL}\033[K"
                        output.append(line)
                    else:
                        line = f"{Style.DIM}{sub['text']}{Style.RESET_ALL}\033[K"
                        output.append(line)
                else:
                    output.append('\033[K')

            sys.stdout.write('\n'.join(output) + '\n')
            
            # Move cursor to the typing position and show it
            if cursor_pos:
                sys.stdout.write(f'\033[{cursor_pos[0]};{cursor_pos[1]}H\033[?25h')
            else:
                sys.stdout.write('\033[?25l') # Hide if no active sub
                
            sys.stdout.flush()
            time.sleep(0.016)

    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        # Show cursor and clean up
        sys.stdout.write('\033[?25h')
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + "Đã dừng.")

if __name__ == "__main__":
    if os.path.exists("assets/lyrics.srt"):
        subs = parse_srt("assets/lyrics.srt")
        play(subs)
    else:
        print("Không tìm thấy file subtitle assets/lyrics.srt")