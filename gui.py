# gui.py
# This module creates the enhanced user interface for Code-Mitra v3.0.

import tkinter as tk
from tkinter import scrolledtext, ttk

class AppGUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.title("Code-Mitra v3.0 - The Ultimate Python AI Coding Assistant")
        self.geometry("1100x800")
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self._configure_styles()

        self._create_widgets()
        self._after_id = None

    def _configure_styles(self):
        """Configures the styles for the themed widgets."""
        self.configure(bg="#2d2d2d")
        self.style.configure("TNotebook", background="#2d2d2d", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#3c3c3c", foreground="white", padding=[15, 8], borderwidth=0, font=('Calibri', 10, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", "#555555")])
        self.style.configure("TButton", background="#007acc", foreground="white", borderwidth=0, padding=8, font=('Calibri', 10, 'bold'))
        self.style.map("TButton", background=[('active', '#005f9e'), ('disabled', '#5a5a5a')])
        self.style.configure("TLabel", background="#2d2d2d", foreground="gray")
        self.style.configure("Status.TLabel", foreground="white", background="#252526")

    def _create_widgets(self):
        """Creates all the widgets for the application."""
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.folder_button = ttk.Button(top_frame, text="Select Folder (for auto-save)", command=self.controller.select_folder)
        self.folder_button.pack(side=tk.LEFT)

        self.load_file_button = ttk.Button(top_frame, text="Load & Analyze File", command=self.controller.load_and_analyze_file)
        self.load_file_button.pack(side=tk.LEFT, padx=10)

        self.selected_folder_label = ttk.Label(top_frame, text="No folder selected")
        self.selected_folder_label.pack(side=tk.LEFT, padx=10)

        qa_main_frame = ttk.Frame(self)
        qa_main_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        qa_main_frame.columnconfigure(0, weight=1)

        qa_label = ttk.Label(qa_main_frame, text="Ask AI to generate code or ask about the code in the Live Editor:", font=('Calibri', 11, 'bold'), foreground="white")
        qa_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.qa_input = tk.Entry(qa_main_frame, bg="#3c3c3c", fg="white", insertbackground="white", relief=tk.FLAT, font=('Calibri', 12))
        self.qa_input.grid(row=1, column=0, sticky="ew", ipady=10)

        self.ask_button = ttk.Button(qa_main_frame, text="Ask AI", command=self.controller.handle_ask_question)
        self.ask_button.grid(row=1, column=1, sticky="e", padx=(10, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        live_editor_pane = ttk.PanedWindow(self.notebook, orient=tk.VERTICAL)
        editor_frame = ttk.Frame(live_editor_pane)
        self.live_editor_tab = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT, borderwidth=0, font=("Consolas", 11))
        self.live_editor_tab.pack(expand=True, fill="both")
        self.live_editor_tab.bind("<KeyRelease>", self.on_key_release)
        live_editor_pane.add(editor_frame, weight=3)

        output_main_frame = ttk.Frame(live_editor_pane)
        output_controls_frame = ttk.Frame(output_main_frame)
        output_controls_frame.pack(fill=tk.X, pady=(5,0))
        
        self.run_button = ttk.Button(output_controls_frame, text="Run Code & Analyze", command=self.controller.run_live_code)
        self.run_button.pack(side=tk.LEFT)
        
        self.save_button = ttk.Button(output_controls_frame, text="Save", command=self.controller.overwrite_file, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.save_as_button = ttk.Button(output_controls_frame, text="Save As...", command=self.controller.save_live_code)
        self.save_as_button.pack(side=tk.LEFT)
        
        self.output_area = scrolledtext.ScrolledText(output_main_frame, wrap=tk.WORD, bg="#1e1e1e", fg="#cccccc", height=10, relief=tk.FLAT, borderwidth=0, font=("Consolas", 10))
        self.output_area.pack(expand=True, fill="both", pady=(5,0))
        live_editor_pane.add(output_main_frame, weight=1)

        self.explanation_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT, borderwidth=0)
        self.errors_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT, borderwidth=0)
        self.tasks_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT, borderwidth=0)
        self.answer_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT, borderwidth=0)

        self.notebook.add(live_editor_pane, text="Live Code Editor")
        self.notebook.add(self.explanation_tab, text="AI Code Explanation")
        self.notebook.add(self.errors_tab, text="Errors & AI Solution")
        self.notebook.add(self.answer_tab, text="Ask AI Results")
        self.notebook.add(self.tasks_tab, text="Markdown Task Breakdown")

        self.status_bar = ttk.Label(self, text="Ready. Type in the Live Editor or load a file to start.", style="Status.TLabel", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, ipady=2, padx=2)

    def on_key_release(self, event=None):
        if self._after_id: self.after_cancel(self._after_id)
        self._after_id = self.after(1500, self.trigger_live_analysis)

    def trigger_live_analysis(self):
        content = self.live_editor_tab.get(1.0, tk.END)
        self.controller.handle_live_code_analysis(content)

    def load_content_to_editor(self, content):
        self.live_editor_tab.delete(1.0, tk.END)
        self.live_editor_tab.insert(1.0, content)
        self.notebook.select(0)

    def update_display(self, target_widget, content):
        def _update():
            widget_map = {
                "explanation": self.explanation_tab,
                "errors": self.errors_tab,
                "tasks": self.tasks_tab,
                "output": self.output_area,
                "answer": self.answer_tab
            }
            widget = widget_map.get(target_widget)

            if widget:
                widget.delete(1.0, tk.END)
                widget.insert(tk.END, content)
                if target_widget != "output": self.notebook.select(widget)
                if target_widget == "answer": self.qa_input.delete(0, tk.END)
        self.after(0, _update)

    def update_status(self, message):
        self.after(0, lambda: self.status_bar.config(text=message))

    def update_folder_label(self, path):
        self.after(0, lambda: self.selected_folder_label.config(text=f"Monitoring: {path}"))
