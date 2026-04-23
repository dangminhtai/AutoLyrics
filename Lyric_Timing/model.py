import json
import os

class LyricModel:
    def __init__(self, json_path):
        self.json_path = json_path
        self.data = []

    def load(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Missing {self.json_path}")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data

    def save(self):
        if not self.data: return
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_len(self):
        return len(self.data)
        
    def get_item(self, idx):
        if 0 <= idx < len(self.data):
            return self.data[idx]
        return None

    def update_time(self, idx, key, new_val):
        if 0 <= idx < len(self.data):
            self.data[idx][key] = round(new_val, 3)

    def find_closest_index(self, target_time):
        closest_idx = 0
        min_diff = float('inf')
        for i, item in enumerate(self.data):
            diff = abs(item.get('start', 0) - target_time)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i
        return closest_idx
        
    def find_active_index(self, current_time):
        for i, item in enumerate(self.data):
            if item.get('start', 0) <= current_time <= item.get('end', 0):
                return i
        return -1
