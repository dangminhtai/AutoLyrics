import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def to_seconds(t):
    """Convert SRT timestamp format (HH:MM:SS,mmm) to total seconds."""
    parts = t.replace(',', '.').strip().split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(parts[0])

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def hide_cursor():
    """Hide the terminal cursor."""
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    """Show the terminal cursor."""
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

import shutil
import re
from wcwidth import wcswidth

def move_to_top():
    """Move cursor to top-left of the terminal."""
    sys.stdout.write('\033[H')

def strip_ansi(text):
    """Remove ANSI escape sequences from a string."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_visible_width(text):
    """Get the actual display width of a string, accounting for Unicode and ignoring ANSI codes."""
    clean_text = strip_ansi(text)
    width = wcswidth(clean_text)
    return width if width >= 0 else len(clean_text)

def get_terminal_width():
    """Return the current terminal width."""
    return shutil.get_terminal_size().columns
