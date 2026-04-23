import os
from core import load_lyrics, LyricPlayer

# Configurations
MUSIC_PATH = "assets/songs.mp3"
LYRICS_PATH = "assets/lyrics.json"

def main():
    # Load lyrics
    lyrics_file = LYRICS_PATH
    if not os.path.exists(lyrics_file):
        # Try .srt if .json is missing
        srt_path = lyrics_file.replace(".json", ".srt")
        if os.path.exists(srt_path):
            lyrics_file = srt_path
        else:
            print(f"Không tìm thấy file lyrics (json/srt) tại: {LYRICS_PATH}")
            return

    subtitles = load_lyrics(lyrics_file)
    if not subtitles:
        print("Dữ liệu subtitle trống hoặc sai định dạng.")
        return

    # Initialize and play
    player = LyricPlayer(MUSIC_PATH, subtitles)
    player.play()

if __name__ == "__main__":
    main()