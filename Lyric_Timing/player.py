import pygame
import os

class AudioPlayer:
    def __init__(self, mp3_path):
        self.mp3_path = mp3_path
        self.audio_offset = 0.0
        self.is_paused = False
        self.play_until = None
        self.is_initialized = False

        if os.path.exists(mp3_path):
            pygame.mixer.init()
            pygame.mixer.music.load(mp3_path)
            self.is_initialized = True

    def play(self, start=0.0, isolated_end=None):
        if not self.is_initialized: return
        self.audio_offset = start
        self.is_paused = False
        self.play_until = isolated_end
        try:
            pygame.mixer.music.play(start=start)
        except Exception as e:
            print("Playback error:", e)

    def stop(self):
        if not self.is_initialized: return
        pygame.mixer.music.stop()
        self.is_paused = False
        self.play_until = None
        
    def pause(self):
        if not self.is_initialized: return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
            
    def unpause(self):
        if not self.is_initialized: return
        pygame.mixer.music.unpause()
        self.is_paused = False

    def toggle_pause(self):
        if not self.is_initialized: return
        if self.is_paused:
            self.unpause()
            return True # now playing
        elif pygame.mixer.music.get_busy():
            self.pause()
            return False # now paused
        return None # stopped

    def get_current_time(self):
        if not self.is_initialized: return 0.0
        pos = pygame.mixer.music.get_pos()
        if pos == -1 and not self.is_paused:
             # It means stopped.
            return self.audio_offset
        return self.audio_offset + (pos / 1000.0)

    def check_isolated_stop(self):
        """Checks if the player should pause because it reached its isolated bounds."""
        if not self.is_initialized: return False
        
        pos = pygame.mixer.music.get_pos()
        if pos == -1 and not self.is_paused:
            return False
            
        current_time = self.audio_offset + (pos / 1000.0)
        
        if self.play_until is not None and current_time >= self.play_until:
            self.pause()
            self.play_until = None
            return True
        return False
