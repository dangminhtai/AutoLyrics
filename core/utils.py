import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def to_seconds(t):
    """Convert SRT timestamp format to total seconds."""
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

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

def move_to_top():
    """Move cursor to top-left of the terminal."""
    sys.stdout.write('\033[H')
