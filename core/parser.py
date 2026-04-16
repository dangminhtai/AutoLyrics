import os
from .utils import to_seconds

def parse_srt(file_path):
    """
    Parse an SRT file into a list of subtitle dictionaries.
    Each dict contains 'start', 'end', and 'text'.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return []

    blocks = content.strip().split('\n\n')
    subtitles = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            text = ' '.join(lines[2:])

            if ' --> ' in time_line:
                try:
                    start_str, end_str = time_line.split(' --> ')
                    subtitles.append({
                        'start': to_seconds(start_str),
                        'end': to_seconds(end_str),
                        'text': text
                    })
                except Exception:
                    continue

    return subtitles
