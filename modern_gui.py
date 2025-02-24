"""
Answer Sheet Grading System
Developer: Atik Faysal
Email: faysal24@rowan.edu
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import logging
from pathlib import Path
import cv2
import easyocr
import numpy as np
import torch

class ModernGraderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Answer Sheet Grading System")
        # Increase window size
        self.root.geometry("1200x1000")
        # Make window resizable
        
        # Add proper window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize EasyOCR reader
        use_gpu = torch.cuda.is_available()
        self.reader = easyocr.Reader(['en'], gpu=use_gpu)
        
        # Add method to load answer key from file if exists
        self.answer_key_file = os.path.join(os.path.dirname(__file__), 'answer_key.txt')
        self.load_answer_key()
        
        # Configure styles
        self.setup_styles()
        
        # Create main containers
        self.create_layout()
        
        # Current directory and image path
        self.current_dir = None
        self.current_image = None
    
    def on_closing(self):
        """Handle window closing properly"""
        try:
            # Clean up any resources
            if hasattr(self, 'reader'):
                del self.reader
            if hasattr(self, 'current_image'):
                del self.current_image
            
            # Destroy all widgets and quit
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.root.destroy()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Reduce header font size
        style.configure('Header.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('Developer.TLabel', font=('Helvetica', 10))
        style.configure('Main.TButton', font=('Helvetica', 14), padding=8)
        style.configure('Directory.TLabel', font=('Helvetica', 12))
        style.configure('Results.TLabel', font=('Helvetica', 14))
        
        # Configure Treeview font
        style.configure('Treeview', font=('Helvetica', 12))
        style.configure('Treeview.Heading', font=('Helvetica', 12, 'bold'))
        
    def create_layout(self):
        # Main container with reduced padding
        main_container = ttk.Frame(self.root, padding="5")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=3)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)  # Adjust weight to give more space to content
        
        # Header frame to contain both title and developer info
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(5, 10))
        
        # Header
        header = ttk.Label(
            header_frame, 
            text="Answer Sheet Grading System",
            style='Header.TLabel'
        )
        header.pack()
        
        # Developer info with smaller font and reduced padding
        dev_info = ttk.Label(
            header_frame,
            text="Developer: Atik Faysal (faysal24@rowan.edu)",
            style='Developer.TLabel',
            foreground='#666666'
        )
        dev_info.pack(pady=(2, 0))
        
        # Adjust the main content to start at row 1 instead of 2
        self.create_file_browser(main_container)
        self.create_preview_panel(main_container)
    
    def create_file_browser(self, parent):
        browser_frame = ttk.LabelFrame(parent, text="File Browser", padding="5")
        browser_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Button frame
        btn_frame = ttk.Frame(browser_frame)
        btn_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="Select Folder",
            command=self.browse_folder,
            style='Main.TButton'
        ).pack(side='left', padx=5)
        
        # Current directory label with larger font
        self.dir_label = ttk.Label(
            browser_frame,
            text="No folder selected",
            style='Directory.TLabel',
            wraplength=250,
            font=('Helvetica', 12)  # Added explicit font size
        )
        self.dir_label.pack(fill='x', pady=(0, 5))
        
        # Create Treeview with larger font
        self.tree = ttk.Treeview(browser_frame, selectmode="browse", height=30, style='Treeview')
        self.tree.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(browser_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select_file)
    
    def create_preview_panel(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview & Controls", padding="10")
        preview_frame.grid(row=1, column=1, sticky="nsew")
        
        # Preview area with smaller size
        self.preview_label = ttk.Label(preview_frame, text="No image selected", font=('Helvetica', 14))
        self.preview_label.pack(pady=10)
        
        # Control buttons
        btn_frame = ttk.Frame(preview_frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            btn_frame,
            text="Grade Selected",
            command=self.grade_selected,
            style='Main.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Edit Answer Key",
            command=self.edit_answer_key,
            style='Main.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Clear Results",
            command=self.clear_results,
            style='Main.TButton'
        ).pack(side='left', padx=5)
        
        # Results area with scrollbar
        results_frame = ttk.LabelFrame(preview_frame, text="Results", padding="5")
        results_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create a frame to hold both text widget and scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Configure text widget with scrollbar
        self.result_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            font=('Helvetica', 14),
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.result_text.yview)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_dir = folder_path
            self.dir_label.config(text=f"Current: {Path(folder_path).name}")
            self.update_file_tree(folder_path)
    
    def update_file_tree(self, path):
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Add new items
        for item in sorted(os.listdir(path)):
            if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                full_path = os.path.join(path, item)
                self.tree.insert('', 'end', text=item, values=(full_path,))
    
    def on_select_file(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            file_path = self.tree.item(selected_items[0])['values'][0]
            self.show_preview(file_path)
    
    def show_preview(self, filepath):
        try:
            self.current_image = filepath
            img = Image.open(filepath)
            # Reduce preview size
            img.thumbnail((600, 600))  # Reduced from 800x800
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo  # Keep reference!
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def preprocess_image(self, image_path):
        """Enhanced image preprocessing optimized for answer sheets."""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        denoised = cv2.fastNlMeansDenoising(thresh)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        return enhanced

    def extract_answers(self, image):
        """Extract answers using EasyOCR with enhanced pattern recognition."""
        try:
            results = self.reader.readtext(
                image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.',
                paragraph=False,
                height_ths=0.4,
                width_ths=0.4,
                contrast_ths=0.2
            )
            
            student_answers = {}
            for result in results:
                if len(result) >= 2:
                    bbox, text = result[0], result[1]
                    text = text.strip().upper()
                    
                    import re
                    match = re.search(r'(\d+)\s*[.,]?\s*([A-Z])', text)
                    if match:
                        num = int(match.group(1))
                        ans = match.group(2)
                        if num in self.answer_key:
                            student_answers[num] = ans
            
            return student_answers
        except Exception as e:
            messagebox.showerror("Error", f"Error in OCR processing: {str(e)}")
            return {}

    def grade_selected(self):
        """Grade the selected image and show results."""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return

        try:
            # Show loading message
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Processing image... Please wait.")
            self.root.update()
            
            # Process image
            processed_img = self.preprocess_image(self.current_image)
            student_answers = self.extract_answers(processed_img)
            
            # Create verification window
            verify_window = tk.Toplevel(self.root)
            verify_window.title("Verify Detected Answers")
            
            # Add instructions
            ttk.Label(
                verify_window,
                text="Please verify and correct the detected answers:",
                padding=10
            ).pack()
            
            # Create entry fields
            answer_vars = {}
            for q_num in range(1, len(self.answer_key) + 1):
                frame = ttk.Frame(verify_window)
                frame.pack(pady=2)
                
                ttk.Label(frame, text=f"Question {q_num}:").pack(side=tk.LEFT)
                answer_var = tk.StringVar(value=student_answers.get(q_num, ''))
                entry = ttk.Entry(frame, textvariable=answer_var, width=5)
                entry.pack(side=tk.LEFT, padx=5)
                answer_vars[q_num] = answer_var

            def confirm_answers():
                verified_answers = {q: var.get().upper() for q, var in answer_vars.items()}
                self.display_results(verified_answers)
                verify_window.destroy()

            ttk.Button(
                verify_window,
                text="Confirm Answers",
                command=confirm_answers,
                padding=5
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Error occurred during processing.")

    def display_results(self, student_answers):
        """Display grading results in the result text widget."""
        correct_count = 0
        results = []
        
        for q_num in range(1, len(self.answer_key) + 1):
            student_ans = student_answers.get(q_num, 'No Answer')
            correct_ans = self.answer_key[q_num]
            is_correct = student_ans == correct_ans
            if is_correct:
                correct_count += 1
            
            results.append(
                f"Q{q_num:2d}: Your answer: {student_ans:^5} | Correct: {correct_ans:^5} | {'✓' if is_correct else '✗'}"
            )
        
        percentage = (correct_count / len(self.answer_key)) * 100
        
        result_text = (
            f"Final Score: {correct_count}/{len(self.answer_key)} ({percentage:.1f}%)\n\n"
            "Detailed Results:\n" +
            "-" * 50 + "\n" +
            "\n".join(results) + "\n" +
            "-" * 50
        )
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

    def load_answer_key(self):
        """Load answer key from file if exists, otherwise use default"""
        try:
            if os.path.exists(self.answer_key_file):
                with open(self.answer_key_file, 'r') as f:
                    self.answer_key = {int(k): v for k, v in 
                                     [line.strip().split(':') for line in f 
                                      if line.strip() and ':' in line]}
            else:
                self.answer_key = {
                    1: 'B', 2: 'E', 3: 'C', 4: 'B', 5: 'G',
                    6: 'A', 7: 'A', 8: 'A', 9: 'E', 10: 'D'
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load answer key: {str(e)}")
            self.answer_key = {i: 'A' for i in range(1, 11)}  # Default fallback

    def save_answer_key(self):
        """Save answer key to file"""
        try:
            with open(self.answer_key_file, 'w') as f:
                for k, v in sorted(self.answer_key.items()):
                    f.write(f"{k}:{v}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save answer key: {str(e)}")

    def edit_answer_key(self):
        """Open window to edit answer key"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Answer Key")
        edit_window.geometry("400x600")

        # Create scrollable frame
        canvas = tk.Canvas(edit_window)
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Instructions
        ttk.Label(
            scrollable_frame,
            text="Edit Answer Key\nEnter correct answers (A-Z) for each question:",
            font=('Helvetica', 12),
            padding=10
        ).pack()

        # Create entry fields
        answer_vars = {}
        for q_num in sorted(self.answer_key.keys()):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(pady=5, fill='x', padx=20)
            
            ttk.Label(
                frame,
                text=f"Question {q_num}:",
                font=('Helvetica', 11)
            ).pack(side=tk.LEFT)
            
            answer_var = tk.StringVar(value=self.answer_key.get(q_num, ''))
            entry = ttk.Entry(frame, textvariable=answer_var, width=5)
            entry.pack(side=tk.LEFT, padx=10)
            answer_vars[q_num] = answer_var

        # Add/Remove question buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(pady=10)

        def add_question():
            next_num = max(self.answer_key.keys()) + 1 if self.answer_key else 1
            self.answer_key[next_num] = 'A'
            edit_window.destroy()
            self.edit_answer_key()

        def remove_question():
            if len(self.answer_key) > 1:
                max_num = max(self.answer_key.keys())
                del self.answer_key[max_num]
                edit_window.destroy()
                self.edit_answer_key()

        ttk.Button(
            btn_frame,
            text="Add Question",
            command=add_question
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Remove Question",
            command=remove_question
        ).pack(side=tk.LEFT, padx=5)

        def save_changes():
            # Validate and save changes
            new_answers = {}
            for q_num, var in answer_vars.items():
                answer = var.get().strip().upper()
                if not answer or not answer[0].isalpha():
                    messagebox.showwarning(
                        "Invalid Input",
                        f"Question {q_num} must have a valid letter answer (A-Z)"
                    )
                    return
                new_answers[q_num] = answer[0]
            
            self.answer_key = new_answers
            self.save_answer_key()
            edit_window.destroy()

        ttk.Button(
            scrollable_frame,
            text="Save Changes",
            command=save_changes,
            style='Main.TButton'
        ).pack(pady=20)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGraderGUI(root)
    root.mainloop()
