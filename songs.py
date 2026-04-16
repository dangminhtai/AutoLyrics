import time
import sys
import pygame
import os
from colorama import init, Fore, Style

# Init
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
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def play(subs):
    pygame.mixer.init()

    if not os.path.exists("assets/songs.mp3"):
        print("Không tìm thấy file nhạc")
        return

    pygame.mixer.music.load("assets/songs.mp3")
    pygame.mixer.music.play()

    start_time = time.time()

    clear()
    sys.stdout.write('\033[?25l')  # hide cursor thật
    sys.stdout.flush()

    try:
        current_sub_idx = 0

        while pygame.mixer.music.get_busy():
            current_time = time.time() - start_time

            active_idx = -1
            for i in range(current_sub_idx, len(subs)):
                sub = subs[i]
                if sub['start'] <= current_time <= sub['end']:
                    active_idx = i
                    current_sub_idx = i
                    break
                elif sub['start'] > current_time:
                    break

            if active_idx == -1:
                for i, sub in enumerate(subs):
                    if sub['start'] <= current_time <= sub['end']:
                        active_idx = i
                        current_sub_idx = i
                        break

            # render
            sys.stdout.write('\033[H')

            window_size = 5
            display_idx = active_idx if active_idx != -1 else current_sub_idx
            start_view = max(0, display_idx - 2)

            output = []

            for i in range(start_view, start_view + window_size):
                if i < len(subs):
                    sub = subs[i]

                    if i == active_idx:
                        duration = max(sub['end'] - sub['start'], 0.001)
                        elapsed = current_time - sub['start']
                        progress = max(0.0, min(1.0, elapsed / duration))

                        num_chars = int(len(sub['text']) * progress)

                        typed = sub['text'][:num_chars]
                        rem = sub['text'][num_chars:]

                        # cursor giả
                        cursor_char = "▌"

                        line = (
                            f"{Fore.YELLOW}{typed}"
                            f"{cursor_char}"
                            f"{Style.DIM}{rem}"
                            f"{Style.RESET_ALL}\033[K"
                        )
                        output.append(line)

                    elif i < display_idx:
                        output.append(f"{Fore.WHITE}{sub['text']}{Style.RESET_ALL}\033[K")
                    else:
                        output.append(f"{Style.DIM}{sub['text']}{Style.RESET_ALL}\033[K")
                else:
                    output.append('\033[K')

            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()

            time.sleep(0.016)

    except KeyboardInterrupt:
        pygame.mixer.music.stop()

    finally:
        sys.stdout.write('\033[?25h')  # restore cursor
        clear()
        print(Fore.RED + "Đã dừng.")


if __name__ == "__main__":
    if os.path.exists("assets/lyrics.srt"):
        subs = parse_srt("assets/lyrics.srt")
        play(subs)
    else:
        print("Không tìm thấy subtitle")