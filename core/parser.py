import os
import json
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
                        'text': text,
                        'words': [] # No word level info in SRT
                    })
                except Exception:
                    continue

    return subtitles

def parse_json(file_path):
    """
    Parse word-level JSON lyrics and group them into lines intelligently.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return []

    if not words:
        return []

    lines = []
    current_line_words = []
    
    # Heuristics for grouping words into lines
    max_gap = 0.5 # Reduced from 0.8 for better sensitivity
    max_len = 50  # Reduced from 60 for better readability in terminal

    for i, word_info in enumerate(words):
        word_text = word_info.get('word', '').strip()
        if not word_text:
            continue

        if not current_line_words:
            current_line_words.append(word_info)
            continue
        
        last_word = current_line_words[-1]
        gap = word_info['start'] - last_word['end']
        
        current_text = ' '.join([w['word'] for w in current_line_words])
        
        # New line triggers:
        # 1. Significant timing gap
        # 2. Line is too long
        # 3. Word starts with uppercase and there's at least a small gap (indicating start of a new phrase)
        is_capitalized = word_text[0].isupper()
        ends_with_punctuation = last_word.get('word', '').strip()[-1] in ('.', '!', '?')
        
        should_break = (
            gap > max_gap or 
            len(current_text) + len(word_text) + 1 > max_len or
            (is_capitalized and gap > 0.1 and len(current_text) > 10) or
            ends_with_punctuation
        )

        if should_break:
            # Save current line
            lines.append({
                'start': current_line_words[0]['start'],
                'end': last_word['end'],
                'text': current_text,
                'words': current_line_words
            })
            current_line_words = [word_info]
        else:
            current_line_words.append(word_info)
            
    # Add last line
    if current_line_words:
        lines.append({
            'start': current_line_words[0]['start'],
            'end': current_line_words[-1]['end'],
            'text': ' '.join([w['word'] for w in current_line_words]),
            'words': current_line_words
        })
        
    return lines

def load_lyrics(file_path):
    """
    Generic lyric loader based on file extension.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        return parse_json(file_path)
    return parse_srt(file_path)
