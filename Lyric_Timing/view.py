import tkinter as tk
from tkinter import ttk

class EditorView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        self.loop_enabled = tk.BooleanVar(value=False)
        self.var_start = tk.StringVar()
        self.var_end = tk.StringVar()
        
        self.setup_ui()

    def setup_ui(self):
        # Top toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(toolbar, text="Load JSON", command=self.controller.load_data).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Save JSON", bg="lightgreen", command=self.controller.save_data).pack(side=tk.LEFT, padx=2)
        tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)
        tk.Button(toolbar, text="Play Start (0.0s)", command=self.controller.play_from_start).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Stop Audio", command=self.controller.stop_audio).pack(side=tk.LEFT, padx=2)
        tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)
        
        self.lbl_flag = tk.Label(toolbar, text="A: -- | B: --", fg="blue")
        self.lbl_flag.pack(side=tk.LEFT, padx=5)
        
        # We trace the checkbox so controller knows when it changes
        chk = tk.Checkbutton(toolbar, text="Loop A-B", variable=self.loop_enabled)
        chk.pack(side=tk.LEFT)
        self.loop_enabled.trace_add("write", lambda *args: self.controller.on_loop_toggle(self.loop_enabled.get()))
        
        tk.Button(toolbar, text="Clear Flags", command=self.controller.clear_flags).pack(side=tk.LEFT, padx=2)

        # Live Preview Panel
        preview_frame = tk.LabelFrame(self.root, text="Live Preview (SPACE: Play/Pause | F: Jump | [ ]: Flags A/B)", bg="#2b2b2b", fg="white")
        preview_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        
        self.lbl_time = tk.Label(preview_frame, text="0.000s", font=("Consolas", 14), bg="#2b2b2b", fg="yellow")
        self.lbl_time.pack(pady=2)

        self.txt_preview = tk.Text(preview_frame, height=1, width=60, font=("Helvetica", 18, "bold"), bg="#2b2b2b", fg="cyan", borderwidth=0, highlightthickness=0)
        self.txt_preview.pack(pady=10)
        self.txt_preview.tag_configure("center", justify='center')
        self.txt_preview.tag_configure("normal", foreground="gray")
        self.txt_preview.tag_configure("bracket", foreground="white")
        self.txt_preview.tag_configure("active", foreground="yellow")

        # Edit Panel
        edit_frame = tk.LabelFrame(self.root, text="Edit Selected Word")
        edit_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

        self.lbl_word = tk.Label(edit_frame, text="Word: ---", font=("Helvetica", 14, "bold"))
        self.lbl_word.grid(row=0, column=0, columnspan=5, pady=5, sticky=tk.W)

        tk.Label(edit_frame, text="Start:").grid(row=1, column=0, padx=5)
        tk.Button(edit_frame, text="-0.1", command=lambda: self.controller.adjust_time('start', -0.1)).grid(row=1, column=1)
        
        tk.Entry(edit_frame, textvariable=self.var_start, width=10).grid(row=1, column=2, padx=5)
        tk.Button(edit_frame, text="+0.1", command=lambda: self.controller.adjust_time('start', 0.1)).grid(row=1, column=3)
        
        play_frame = tk.Frame(edit_frame)
        play_frame.grid(row=1, column=4, padx=10, sticky=tk.W)
        tk.Button(play_frame, text="Play from Start", command=self.controller.play_segment).pack(side=tk.LEFT, padx=2)
        tk.Button(play_frame, text="Play Word Only", command=lambda: self.controller.play_segment(isolated=True)).pack(side=tk.LEFT)

        tk.Label(edit_frame, text="End:").grid(row=2, column=0, padx=5, pady=5)
        tk.Button(edit_frame, text="-0.1", command=lambda: self.controller.adjust_time('end', -0.1)).grid(row=2, column=1)
        tk.Entry(edit_frame, textvariable=self.var_end, width=10).grid(row=2, column=2, padx=5)
        tk.Button(edit_frame, text="+0.1", command=lambda: self.controller.adjust_time('end', 0.1)).grid(row=2, column=3)

        tk.Button(edit_frame, text="Apply Typed Values to Table", command=self.controller.apply_entry).grid(row=2, column=4, padx=10, sticky=tk.W)

        # Treeview (Table)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("#", "Word", "Start", "End")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("#", text="Index")
        self.tree.heading("Word", text="Word")
        self.tree.heading("Start", text="Start Time (s)")
        self.tree.heading("End", text="End Time (s)")

        self.tree.column("#", width=50, anchor=tk.CENTER)
        self.tree.column("Word", width=300)
        self.tree.column("Start", width=100, anchor=tk.CENTER)
        self.tree.column("End", width=100, anchor=tk.CENTER)

        self.tree.tag_configure('highlight', background='#4a90e2', foreground='white')

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.controller.on_tree_select)

    def populate_tree(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, item in enumerate(data):
            self.tree.insert("", tk.END, iid=str(i), values=(
                i, item.get('word', ''), round(item.get('start', 0), 3), round(item.get('end', 0), 3)
            ))

    def update_tree_row(self, idx, item):
        self.tree.item(str(idx), values=(
            idx, item.get('word',''), round(item.get('start', 0), 3), round(item.get('end', 0), 3)
        ))

    def get_selected_indices(self):
        selected = self.tree.selection()
        if not selected: return []
        return sorted([int(x) for x in selected])

    def set_selection(self, idx):
        # We temporarily disable the tree select event so it doesn't trigger unexpectedly
        self.tree.selection_set(str(idx))
        self.tree.focus(str(idx))
        self.tree.see(str(idx))

    def update_edit_panel(self, word, start, end):
        self.lbl_word.config(text=f"Word: {word}")
        self.var_start.set(str(round(start, 3)))
        self.var_end.set(str(round(end, 3)))

    def get_edit_panel_values(self):
        return self.var_start.get(), self.var_end.get()

    def update_time_display(self, time_str):
        self.lbl_time.config(text=time_str)

    def update_flags_display(self, a_val, b_val):
        a_txt = f"{a_val}s" if a_val is not None else "--"
        b_txt = f"{b_val}s" if b_val is not None else "--"
        self.lbl_flag.config(text=f"A: {a_txt} | B: {b_txt}")

    def update_preview_panel(self, active_idx, data):
        self.txt_preview.config(state=tk.NORMAL)
        self.txt_preview.delete("1.0", tk.END)
        
        if active_idx != -1 and data:
            start_i = max(0, active_idx - 5)
            end_i = min(len(data), active_idx + 6)
            
            for i in range(start_i, end_i):
                w = data[i].get('word', '')
                if i == active_idx:
                    self.txt_preview.insert(tk.END, "[", "bracket")
                    self.txt_preview.insert(tk.END, w, "active")
                    self.txt_preview.insert(tk.END, "] ", "bracket")
                else:
                    self.txt_preview.insert(tk.END, w + " ", "normal")
        else:
            self.txt_preview.insert(tk.END, "...", "normal")

        self.txt_preview.tag_add("center", "1.0", "end")
        self.txt_preview.config(state=tk.DISABLED)

    def apply_highlight_tags(self, data, flag_a, flag_b):
        if flag_a is None or flag_b is None:
            for i in range(len(data)):
                try: self.tree.item(str(i), tags=())
                except: pass
            return
            
        for i, item in enumerate(data):
            try:
                if item.get('end', 0) > flag_a - 0.01 and item.get('start', 0) < flag_b + 0.01:
                    self.tree.item(str(i), tags=('highlight',))
                else:
                    self.tree.item(str(i), tags=())
            except: pass
