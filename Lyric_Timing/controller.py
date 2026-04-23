import tkinter as tk
from tkinter import messagebox
from view import EditorView

class AppController:
    def __init__(self, root, model, player):
        self.root = root
        self.model = model
        self.player = player
        
        # Instantiate view and pass self as controller
        self.view = EditorView(root, self)

        
        self.current_index = None
        self.silent_select = False
        
        self.flag_a = None
        self.flag_b = None
        self.is_looping = False

        self._bind_global_keys()
        self.load_data()
        self._start_update_loop()

    def _bind_global_keys(self):
        self.root.bind("<space>", self.on_key_space)
        self.root.bind("f", self.on_key_find)
        self.root.bind("F", self.on_key_find)
        self.root.bind("[", self.on_key_flag_a)
        self.root.bind("]", self.on_key_flag_b)

    def _is_in_entry(self):
        return isinstance(self.root.focus_get(), tk.Entry)

    # --- UI Actions ---
    def load_data(self):
        try:
            data = self.model.load()
            self.view.populate_tree(data)
            self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON:\n{e}")

    def save_data(self):
        try:
            self.model.save()
            messagebox.showinfo("Success", "Saved successfully to lyrics.json!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def on_tree_select(self, event):
        indices = self.view.get_selected_indices()
        if not indices: return
        
        # Multiple selection triggers auto flags
        if len(indices) > 1:
            try:
                first_idx = indices[0]
                last_idx = indices[-1]
                
                start_val = self.model.get_item(first_idx).get('start', 0.0)
                end_val = self.model.get_item(last_idx).get('end', 0.0)
                
                self.flag_a = round(start_val, 3)
                self.flag_b = round(end_val, 3)
                
                self.view.loop_enabled.set(True)
                self.is_looping = True
                
                self.view.update_flags_display(self.flag_a, self.flag_b)
                self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)
                
                self.current_index = first_idx
            except: pass
        else:
            self.current_index = indices[0]

        item = self.model.get_item(self.current_index)
        if item:
            self.view.update_edit_panel(item.get('word', ''), item.get('start', 0), item.get('end', 0))

        if not self.silent_select:
            self.play_segment()
        self.silent_select = False

    def on_loop_toggle(self, is_enabled):
        self.is_looping = is_enabled

    # --- Audio Actions ---
    def play_from_start(self):
        self.player.play(start=0.0)

    def play_segment(self, isolated=False):
        if self.current_index is None:
            self.player.play(0.0)
            return
            
        item = self.model.get_item(self.current_index)
        start_t = item.get('start', 0)
        end_t = item.get('end', 0) if isolated else None
        
        self.player.play(start=start_t, isolated_end=end_t)

    def stop_audio(self):
        self.player.stop()
        self.view.update_time_display("0.000 s")
        self.view.update_preview_panel(-1, [])

    # --- Key Bindings ---
    def on_key_space(self, event):
        if self._is_in_entry(): return
        res = self.player.toggle_pause()
        if res is None: # was stopped
            self.play_segment()
        return "break"

    def on_key_find(self, event):
        if self._is_in_entry(): return
        if self.model.get_len() == 0: return

        current_time = self.player.get_current_time()
        idx = self.model.find_closest_index(current_time)
        
        self.silent_select = True
        self.view.set_selection(idx)
        return "break"

    def on_key_flag_a(self, event):
        if self._is_in_entry(): return
        self.flag_a = round(self.player.get_current_time(), 3)
        self.view.update_flags_display(self.flag_a, self.flag_b)
        self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)
        return "break"
        
    def on_key_flag_b(self, event):
        if self._is_in_entry(): return
        self.flag_b = round(self.player.get_current_time(), 3)
        self.view.update_flags_display(self.flag_a, self.flag_b)
        self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)
        return "break"

    def clear_flags(self):
        self.flag_a = None
        self.flag_b = None
        self.view.update_flags_display(self.flag_a, self.flag_b)
        self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)

    # --- Editing ---
    def adjust_time(self, key, amount):
        if self.current_index is None: return
        
        item = self.model.get_item(self.current_index)
        new_val = max(0.0, item.get(key, 0.0) + amount)
        self.model.update_time(self.current_index, key, new_val)
        
        self.view.update_tree_row(self.current_index, self.model.get_item(self.current_index))
        # Update fields
        item = self.model.get_item(self.current_index)
        self.view.update_edit_panel(item.get('word',''), item.get('start',0), item.get('end',0))

        if key == 'start':
            self.silent_select = True
            self.play_segment()
            
        self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)

    def apply_entry(self):
        if self.current_index is None: return
        s_val, e_val = self.view.get_edit_panel_values()
        try:
            self.model.update_time(self.current_index, 'start', float(s_val))
            self.model.update_time(self.current_index, 'end', float(e_val))
            
            item = self.model.get_item(self.current_index)
            self.view.update_tree_row(self.current_index, item)
            self.view.apply_highlight_tags(self.model.data, self.flag_a, self.flag_b)
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value")

    # --- Main Loop ---
    def _start_update_loop(self):
        self._update_tick()

    def _update_tick(self):
        if self.player.is_initialized:
            # Check if isolated playback hit threshold
            self.player.check_isolated_stop()
            
            # Check A-B Loop
            current_time = self.player.get_current_time()
            if self.is_looping and self.flag_a is not None and self.flag_b is not None:
                if current_time >= self.flag_b:
                    self.player.play(start=self.flag_a)
                    current_time = self.flag_a

            # Update displays
            self.view.update_time_display(f"{current_time:.3f} s")
            
            active_idx = self.model.find_active_index(current_time)
            self.view.update_preview_panel(active_idx, self.model.data)
            
        self.root.after(50, self._update_tick)
