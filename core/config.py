from colorama import Fore, Style

class Settings:
    # --- Paths ---
    MUSIC_PATH = "assets/songs.mp3"
    LYRICS_PATH = "assets/lyrics.json"

    # --- UI Settings ---
    WINDOW_SIZE = 5
    ACTIVE_INDICATOR = "→ "
    PROGRESS_BAR_WIDTH = 40
    
    # Colors
    COLOR_ACTIVE = Fore.YELLOW
    COLOR_PAST = Fore.WHITE
    COLOR_FUTURE = Style.DIM
    COLOR_INDICATOR = Fore.CYAN
    COLOR_PROGRESS_BAR = Fore.GREEN
    COLOR_ERROR = Fore.RED

    # --- Timing Settings ---
    SEEK_SECONDS = 5
    FRAME_DELAY = 0.01  # Animation smoothness

    # --- Line Grouping Rules (Advanced) ---
    # Global switches
    USE_GAP_RULE = False    # Break based on time gap (BRK_MAX_GAP)
    USE_LEN_RULE = False    # Break based on char length (BRK_MAX_LINE_LEN)
    BRK_ON_CAPS = True
    BRK_ON_PUNCTUATION = True
    
    # Thresholds
    BRK_MAX_GAP = 0.5       
    BRK_MAX_LINE_LEN = 50   
    BRK_MIN_LINE_LEN = 0   # Avoid breaking tiny lines (unless huge gap)
    BRK_CAPS_GAP_MIN = 0  # Min gap required for a Capital word to trigger break
    
    # Proper Nouns / Excluded words 
    # (Words in this list will NEVER trigger a line break even if capitalized)
    EXCLUDED_FROM_BREAK = [
        "Jack","Sơn Tùng"
    ]
    
    # Punctuation marks that trigger a break
    PUNCTUATION_MARKS = ('.', '!', '?', ';')

# Global instance
CONFIG = Settings()
