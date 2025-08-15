# main_app.py
# The main controller for the Code-Mitra v3.0 application.

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
import tempfile
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gui import AppGUI
from analyzer import run_pylint, read_file_content
from gemini_client import query_gemini

class MainApplication:
    def __init__(self):
        self.gui = AppGUI(self)
        self.observer = None
        self.monitoring_path = None
        self.current_file_path = None
        self.is_analyzing = False
        self.analysis_lock = threading.Lock()
        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run(self):
        self.gui.mainloop()

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path: return
        
        self.monitoring_path = path
        self.gui.update_folder_label(self.monitoring_path)
        
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.monitoring_path, recursive=True)
        self.observer.start()
        self.gui.update_status(f"Started monitoring folder: {self.monitoring_path}")

    def load_and_analyze_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=(("Python files", "*.py"), ("Markdown files", "*.md"))
        )
        if not file_path: return
        
        self.current_file_path = file_path
        self.gui.save_button.config(state='normal')
        threading.Thread(target=self.handle_file_analysis, args=(file_path,), daemon=True).start()

    def handle_live_code_analysis(self, content: str):
        with self.analysis_lock:
            if self.is_analyzing:
                return
            self.is_analyzing = True
        
        threading.Thread(target=self._process_analysis, args=(content, "python"), daemon=True).start()

    def handle_file_analysis(self, file_path):
        with self.analysis_lock:
            if self.is_analyzing:
                return
            self.is_analyzing = True

        self.gui.load_content_to_editor(read_file_content(file_path))
        
        file_type = "python" if file_path.endswith(".py") else "markdown"
        # Since load_content_to_editor is async, get content from the widget after a small delay or directly
        # For simplicity, we'll get it directly here.
        content = self.gui.live_editor_tab.get(1.0, tk.END)
        threading.Thread(target=self._process_analysis, args=(content, file_type), daemon=True).start()

    def _process_analysis(self, content, file_type):
        """A centralized method to run analysis and reset the flag."""
        try:
            self.current_file_content = content
            if not content.strip():
                self.gui.update_display("explanation", "File is empty.")
                return

            if file_type == "python":
                self._analyze_python_file(content)
            elif file_type == "markdown":
                self._analyze_markdown_file(content)
            
            self.gui.update_status(f"Analysis complete. Ready.")
        finally:
            with self.analysis_lock:
                self.is_analyzing = False

    def _analyze_python_file(self, content):
        self.gui.update_status("Asking AI for code explanation...")
        explanation_prompt = (
            f"Please analyze the following Python code and provide three things:\n"
            f"1. A clear explanation of the code's logic and purpose.\n"
            f"2. Suggestions for alternative methods or approaches to achieve the same result.\n"
            f"3. Potential optimizations or improvements.\n\n"
            f"--- PYTHON CODE ---\n{content}"
        )
        explanation = query_gemini(explanation_prompt)
        self.gui.update_display("explanation", explanation)
        self.gui.update_status("Explanation received. Analyzing for errors...")

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py', encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        pylint_errors = run_pylint(temp_file_path)
        os.remove(temp_file_path)

        if "Your code has been rated at 10.00/10" in pylint_errors or not pylint_errors.strip():
            solution = "No errors found. Your code is clean!"
            self.gui.update_display("errors", solution)
        else:
            self.gui.update_status("Errors found. Asking AI for a solution...")
            solution_prompt = (
                f"The Python code below has these pylint errors:\n\n"
                f"--- DETECTED ERRORS ---\n{pylint_errors}\n\n"
                f"--- PYTHON CODE ---\n{content}\n\n"
                f"Please explain these errors in simple terms and provide the corrected, complete code snippet."
            )
            solution = f"--- DETECTED ERRORS ---\n{pylint_errors}\n\n--- AI SUGGESTED SOLUTION ---\n" + query_gemini(solution_prompt)
            self.gui.update_display("errors", solution)

    def _analyze_markdown_file(self, content):
        self.gui.update_status("Asking AI to break down the task...")
        task_prompt = f"Break down the task in this Markdown:\n\n---\n\n{content}"
        task_breakdown = query_gemini(task_prompt)
        self.gui.update_display("tasks", task_breakdown)

    def handle_ask_question(self):
        question = self.gui.qa_input.get()
        live_code = self.gui.live_editor_tab.get(1.0, tk.END)

        if not question: return self.gui.update_status("Please type a question first.")
        
        self.gui.update_status("Asking AI... Please wait.")
        threading.Thread(target=self._process_question, args=(question, live_code), daemon=True).start()

    def _process_question(self, question, live_code):
        if not live_code.strip():
            prompt = f"Generate a Python code snippet for the following request: '{question}'. Provide only the code, without any explanation before or after."
            answer = query_gemini(prompt)
            self.gui.load_content_to_editor(answer)
            self.gui.update_display("answer", f"--- Your Request ---\n{question}\n\n--- AI Generated Code ---\n{answer}")
        else:
            prompt = f"Context:\n---\n{live_code}\n---\n\nQuestion: '{question}'\n\nAnswer:"
            answer = query_gemini(prompt)
            self.gui.update_display("answer", f"--- Your Question ---\n{question}\n\n--- AI's Answer ---\n{answer}")
        
        self.gui.update_status("Ready.")

    def run_live_code(self):
        code = self.gui.live_editor_tab.get(1.0, tk.END)
        if not code.strip():
            self.gui.update_display("output", "Nothing to run.")
            return

        threading.Thread(target=self._execute_code, args=(code,), daemon=True).start()
        threading.Thread(target=self.handle_live_code_analysis, args=(code,), daemon=True).start()

    def _execute_code(self, code):
        self.gui.update_status("Executing code...")
        try:
            process = subprocess.run(
                ['python', '-c', code], capture_output=True, text=True, encoding='utf-8', timeout=10
            )
            output = f"--- OUTPUT ---\n{process.stdout}\n"
            if process.stderr: output += f"--- ERRORS ---\n{process.stderr}"
            self.gui.update_display("output", output)
        except subprocess.TimeoutExpired:
            self.gui.update_display("output", "Execution timed out after 10 seconds.")
        except Exception as e:
            self.gui.update_display("output", f"An error occurred: {e}")

    def save_live_code(self):
        code = self.gui.live_editor_tab.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not file_path: return
        self._save_to_file(file_path, code)

    def overwrite_file(self):
        if not self.current_file_path:
            messagebox.showerror("Error", "No file is currently loaded to save over.")
            return
        code = self.gui.live_editor_tab.get(1.0, tk.END)
        self._save_to_file(self.current_file_path, code)

    def _save_to_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.gui.update_status(f"File saved successfully to {file_path}")
        except Exception as e:
            self.gui.update_status(f"Error saving file: {e}")
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

    def on_closing(self):
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.gui.destroy()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, controller):
        self.controller = controller
        self.last_triggered = 0

    def on_modified(self, event):
        if not event.is_directory and (time.time() - self.last_triggered > 1.5):
            if event.src_path.endswith((".py", ".md")):
                self.last_triggered = time.time()
                threading.Thread(target=self.controller.handle_file_analysis, args=(event.src_path,), daemon=True).start()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
