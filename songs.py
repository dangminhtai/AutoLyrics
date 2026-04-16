import os
from core import load_lyrics, LyricPlayer

# Configurations
MUSIC_PATH = "assets/songs.mp3"
LYRICS_PATH = "assets/lyrics.json"

def main():
    # Load lyrics
    if not os.path.exists(LYRICS_PATH):
        print(f"Không tìm thấy file lyrics: {LYRICS_PATH}")
        return

    subtitles = load_lyrics(LYRICS_PATH)
    if not subtitles:
        print("Dữ liệu subtitle trống hoặc sai định dạng.")
        return

    # Initialize and play
    player = LyricPlayer(MUSIC_PATH, subtitles)
    player.play()

if __name__ == "__main__":
    main()