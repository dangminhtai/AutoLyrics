import os
import json
from .utils import to_seconds
from .config import CONFIG

def parse_srt(file_path):
    """
    Parse an SRT file into a list of subtitle dictionaries.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{CONFIG.COLOR_ERROR}Lỗi khi đọc file srt: {e}")
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
                        'words': [] 
                    })
                except Exception:
                    continue
    return subtitles

def parse_json(file_path):
    """
    Parse word-level JSON lyrics and group them using advanced configuration rules.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
    except Exception as e:
        print(f"{CONFIG.COLOR_ERROR}Lỗi khi đọc file JSON: {e}")
        return []

    if not words:
        return []

    lines = []
    current_line_words = []
    
    for i, word_info in enumerate(words):
        word_text = word_info.get('word', '').strip()
        if not word_text:
            continue

        if not current_line_words:
            current_line_words.append(word_info)
            continue
        
        last_word_info = current_line_words[-1]
        last_word_text = last_word_info.get('word', '').strip()
        gap = word_info['start'] - last_word_info['end']
        current_text = ' '.join([w['word'] for w in current_line_words])
        
        # New line triggers
        should_break = False
        
        # 1. Gap threshold (if enabled)
        if CONFIG.USE_GAP_RULE and gap > CONFIG.BRK_MAX_GAP:
            should_break = True
            
        # 2. Length threshold (if enabled)
        elif CONFIG.USE_LEN_RULE and len(current_text) + len(word_text) + 1 > CONFIG.BRK_MAX_LINE_LEN:
            should_break = True
            
        # 3. Capitalization rule (if enabled)
        elif CONFIG.BRK_ON_CAPS and word_text[0].isupper():
            if word_text not in CONFIG.EXCLUDED_FROM_BREAK:
                if gap >= CONFIG.BRK_CAPS_GAP_MIN and len(current_text) >= CONFIG.BRK_MIN_LINE_LEN:
                    should_break = True
        
        # 4. Punctuation rule (if enabled)
        elif CONFIG.BRK_ON_PUNCTUATION:
            if last_word_text and last_word_text[-1] in CONFIG.PUNCTUATION_MARKS:
                should_break = True

        if should_break:
            lines.append({
                'start': current_line_words[0]['start'],
                'end': last_word_info['end'],
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

def load_lyrics(file_path=None):
    """
    Generic lyric loader based on file extension. Uses CONFIG path by default.
    """
    path = file_path if file_path else CONFIG.LYRICS_PATH
    _, ext = os.path.splitext(path)
    if ext.lower() == '.json':
        return parse_json(path)
    return parse_srt(path)
