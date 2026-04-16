import os
from core import parse_srt, LyricPlayer

# Configurations
MUSIC_PATH = "assets/songs.mp3"
LYRICS_PATH = "assets/lyrics.srt"

def main():
    # Load lyrics
    if not os.path.exists(LYRICS_PATH):
        print(f"Không tìm thấy file subtitle: {LYRICS_PATH}")
        return

    subtitles = parse_srt(LYRICS_PATH)
    if not subtitles:
        print("Dữ liệu subtitle trống hoặc sai định dạng.")
        return

    # Initialize and play
    player = LyricPlayer(MUSIC_PATH, subtitles)
    player.play()

if __name__ == "__main__":
    main()