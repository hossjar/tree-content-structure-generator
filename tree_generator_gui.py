import os
import sys
import string
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import webbrowser

class TreeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VSCode Project Tree Generator")
        self.root.geometry("900x750")  # Increased size for better layout
        self.create_widgets()

    def create_widgets(self):
        # Create Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Create Frames for each tab
        self.main_frame = ttk.Frame(self.notebook)
        self.contact_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text='Generate Tree')
        self.notebook.add(self.contact_frame, text='Contact Us')

        # --- Main Frame Widgets ---
        self.create_main_tab_widgets()

        # --- Contact Us Tab Widgets ---
        self.create_contact_tab_widgets()

    def create_main_tab_widgets(self):
        # Project Folder Selection
        self.folder_label = ttk.Label(self.main_frame, text="VSCode Project Folder:")
        self.folder_label.pack(pady=(10, 0), anchor='w', padx=10)

        self.folder_frame = ttk.Frame(self.main_frame)
        self.folder_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_path, width=80)
        self.folder_entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.browse_folder_btn = ttk.Button(self.folder_frame, text="Browse", command=self.browse_folder)
        self.browse_folder_btn.pack(side=tk.LEFT)

        # Depth Input
        self.depth_label = ttk.Label(self.main_frame, text="Tree Depth:")
        self.depth_label.pack(pady=(10, 0), anchor='w', padx=10)

        self.depth_entry = ttk.Entry(self.main_frame)
        self.depth_entry.pack(pady=(0, 10), padx=10, fill=tk.X)
        self.depth_entry.insert(0, "3")  # Default depth

        # Output Directory Selection
        self.output_label = ttk.Label(self.main_frame, text="Output Directory:")
        self.output_label.pack(pady=(10, 0), anchor='w', padx=10)

        self.output_frame = ttk.Frame(self.main_frame)
        self.output_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

        self.output_path = tk.StringVar(value=self.get_default_output_directory())
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_path, width=80)
        self.output_entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.browse_output_btn = ttk.Button(self.output_frame, text="Browse", command=self.browse_output_directory)
        self.browse_output_btn.pack(side=tk.LEFT)

        # Generate Button
        self.generate_btn = ttk.Button(self.main_frame, text="Generate Tree", command=self.generate_tree)
        self.generate_btn.pack(pady=(10, 10))

        # Progress Indicator
        self.progress_label = ttk.Label(self.main_frame, text="", foreground="blue")
        self.progress_label.pack()

        # Display Window (ScrolledText)
        self.display_text = scrolledtext.ScrolledText(self.main_frame, height=25, state='disabled', font=("Courier New", 10))
        self.display_text.pack(pady=(10, 0), padx=10, fill=tk.BOTH, expand=True)
        self.display_text.insert(tk.END, "Output will be displayed here after processing.\n")

        # Copy to Clipboard Button
        self.copy_button = ttk.Button(self.main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(pady=(5, 5))

    def create_contact_tab_widgets(self):
        contact_label = ttk.Label(
            self.contact_frame,
            text="Contact Us: Jariani@live.com",
            foreground="blue",
            font=("Helvetica", 12, "underline"),
            cursor="hand2"
        )
        contact_label.pack(pady=20)
        contact_label.bind("<Button-1>", self.open_email)

    def get_default_output_directory(self):
        # Get the user's home directory
        home_dir = os.path.expanduser("~")
        # Path to Documents folder
        documents_dir = os.path.join(home_dir, "Documents")
        # Ensure the Documents directory exists
        if not os.path.isdir(documents_dir):
            documents_dir = home_dir  # Fallback to home directory if Documents doesn't exist
        return documents_dir

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def browse_output_directory(self):
        directory_selected = filedialog.askdirectory()
        if directory_selected:
            self.output_path.set(directory_selected)

    def open_email(self, event):
        # Open the default email client with the contact email
        webbrowser.open("mailto:Jariani@live.com")

    def copy_to_clipboard(self):
        content = self.display_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Copied", "Content copied to clipboard.")
        else:
            messagebox.showwarning("No Content", "There is no content to copy.")

    def generate_output_filename(self, folder_path):
        # Get the base name of the folder
        base_name = os.path.basename(os.path.normpath(folder_path))
        # Replace invalid filename characters
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safe_base_name = ''.join(c for c in base_name if c in valid_chars)
        # Append timestamp to make it unique
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{safe_base_name}_{timestamp}.md"
        return filename

    def load_gitignore(self, folder_path):
        gitignore_path = os.path.join(folder_path, '.gitignore')
        if not os.path.isfile(gitignore_path):
            return None
        try:
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
            spec = PathSpec.from_lines(GitWildMatchPattern, patterns)
            return spec
        except Exception as e:
            self.log_error(f"Error reading .gitignore: {e}")
            return None

    def should_ignore(self, path, spec, base_path, excluded_folders):
        # Check against .gitignore patterns
        if spec:
            try:
                relative_path = os.path.relpath(path, base_path)
                if spec.match_file(relative_path):
                    return True
            except Exception:
                pass
        # Exclude specific folders
        for folder in excluded_folders:
            folder_path = os.path.join(base_path, folder)
            if os.path.commonpath([path, folder_path]) == folder_path:
                return True
        return False

    def generate_tree_structure(self, folder_path, max_depth, selected_extensions, media_extensions, spec, excluded_folders, errors):
        tree_lines = []
        base_path = os.path.abspath(folder_path)

        def traverse(current_path, depth):
            if depth > max_depth:
                return
            try:
                entries = sorted(os.listdir(current_path))
            except Exception as e:
                errors.append(f"Error accessing {current_path}: {e}")
                return

            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if self.should_ignore(full_path, spec, base_path, excluded_folders):
                    continue
                rel_path = os.path.relpath(full_path, base_path)
                indent = "    " * depth
                if os.path.isdir(full_path):
                    tree_lines.append(f"{indent}- **{entry}/**")
                    traverse(full_path, depth + 1)
                else:
                    ext = os.path.splitext(entry)[1].lower()
                    if ext in media_extensions or entry.lower() in media_extensions:
                        # Media file: include only the file name
                        tree_lines.append(f"{indent}- {entry}")
                    else:
                        tree_lines.append(f"{indent}- {entry}")
                        if ext in selected_extensions or entry in selected_extensions:
                            try:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                # Determine the language for code blocks
                                language = ext.replace('.', '') if ext.startswith('.') else ext
                                if language in ['Dockerfile', 'nginx.conf']:
                                    language = 'conf'
                                # Include the relative path as a comment inside the code block
                                relative_file_path = os.path.relpath(full_path, base_path)
                                tree_lines.append(f"{indent}    ```{language}")
                                tree_lines.append(f"{indent}    /* {relative_file_path} */")
                                tree_lines.append(content)
                                tree_lines.append(f"{indent}    ```")
                            except UnicodeDecodeError:
                                errors.append(f"Binary or undecodable file skipped: {full_path}")
                            except Exception as e:
                                errors.append(f"Error reading {full_path}: {e}")

        traverse(base_path, 0)
        return "\n".join(tree_lines)

    def log_error(self, message):
        self.display_text.configure(state='normal')
        self.display_text.insert(tk.END, f"{message}\n")
        self.display_text.configure(state='disabled')

    def generate_tree(self):
        # Clear previous output
        self.display_text.configure(state='normal')
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "Processing...\n")
        self.display_text.configure(state='disabled')

        folder = self.folder_path.get()
        depth = self.depth_entry.get()
        output_dir = self.output_path.get()

        # Input Validation
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Invalid Folder", "Please select a valid VSCode project folder.")
            return
        try:
            depth = int(depth)
            if depth < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Depth", "Please enter a non-negative integer for depth.")
            return
        if not os.path.isdir(output_dir):
            messagebox.showerror("Invalid Output Directory", "Please select a valid output directory.")
            return

        # Validate output directory
        if not self.can_write_to_directory(output_dir):
            messagebox.showerror("Permission Denied", f"Cannot write to the directory:\n{output_dir}\nPlease choose a different location.")
            return

        # Generate unique output filename based on folder path
        output_filename = self.generate_output_filename(folder)
        output = os.path.join(output_dir, output_filename)

        # Fixed list of file types to include
        selected_extensions = [
            '.txt', '.html', '.py', '.yml', '.yaml', 'Dockerfile',
            'nginx.conf', '.js', '.css', '.json', '.ts', '.jsx',
            '.tsx', '.java', '.c', '.cpp', '.md', '.xml', '.ini'
        ]

        # Media file extensions
        media_extensions = [
            '.mp3', '.wav', '.mp4', '.jpg', '.jpeg', '.png', '.svg', '.gif',
            '.bmp', '.tiff', '.ico', '.mkv', '.flv', '.avi', '.mov', '.webm'
        ]

        include_contents = True  # As per user requirement to include contents

        # Excluded folders
        excluded_folders = ['.git', 'venv', '__pycache__', 'build', 'dist', '.env', '.idea', '.vscode', 'My Music', 'My Pictures', 'My Videos']

        # Load .gitignore if exists
        spec = self.load_gitignore(folder)

        errors = []

        # Update progress
        self.progress_label.config(text="Generating tree structure...")

        # Generate the tree
        tree = self.generate_tree_structure(
            folder,
            depth,
            selected_extensions,
            media_extensions,
            spec,
            excluded_folders,
            errors
        )

        # Write to the output file
        try:
            with open(output, 'w', encoding='utf-8') as f:
                f.write("# Project Tree Structure\n\n")
                f.write(tree)
            success = True
            self.progress_label.config(text="Generation completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error writing to output file: {e}")
            self.progress_label.config(text="")
            errors.append(f"Error writing to output file: {e}")
            success = False

        # Display output and errors separately
        if success:
            try:
                with open(output, 'r', encoding='utf-8') as f:
                    output_content = f.read()
                self.display_text.configure(state='normal')
                self.display_text.delete(1.0, tk.END)
                self.display_text.insert(tk.END, output_content)
                self.display_text.configure(state='disabled')
                messagebox.showinfo("Success", f"Tree structure successfully saved to:\n{output}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading output file: {e}")
                self.log_error(f"Error reading output file: {e}")

        # Display errors if any
        if errors:
            self.display_text.configure(state='normal')
            self.display_text.insert(tk.END, "\n### Errors Encountered:\n")
            for error in errors:
                self.display_text.insert(tk.END, f"- {error}\n")
            self.display_text.configure(state='disabled')

        # Reset progress after a short delay
        self.root.after(2000, lambda: self.progress_label.config(text=""))

    def can_write_to_directory(self, directory):
        try:
            test_file = os.path.join(directory, "temp_permission_test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except Exception:
            return False

    def load_gitignore(self, folder_path):
        gitignore_path = os.path.join(folder_path, '.gitignore')
        if not os.path.isfile(gitignore_path):
            return None
        try:
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
            spec = PathSpec.from_lines(GitWildMatchPattern, patterns)
            return spec
        except Exception as e:
            self.log_error(f"Error reading .gitignore: {e}")
            return None

    def should_ignore(self, path, spec, base_path, excluded_folders):
        # Check against .gitignore patterns
        if spec:
            try:
                relative_path = os.path.relpath(path, base_path)
                if spec.match_file(relative_path):
                    return True
            except Exception:
                pass
        # Exclude specific folders
        for folder in excluded_folders:
            folder_path = os.path.join(base_path, folder)
            if os.path.commonpath([path, folder_path]) == folder_path:
                return True
        return False

    def generate_tree_structure(self, folder_path, max_depth, selected_extensions, media_extensions, spec, excluded_folders, errors):
        tree_lines = []
        base_path = os.path.abspath(folder_path)

        def traverse(current_path, depth):
            if depth > max_depth:
                return
            try:
                entries = sorted(os.listdir(current_path))
            except Exception as e:
                errors.append(f"Error accessing {current_path}: {e}")
                return

            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if self.should_ignore(full_path, spec, base_path, excluded_folders):
                    continue
                rel_path = os.path.relpath(full_path, base_path)
                indent = "    " * depth
                if os.path.isdir(full_path):
                    tree_lines.append(f"{indent}- **{entry}/**")
                    traverse(full_path, depth + 1)
                else:
                    ext = os.path.splitext(entry)[1].lower()
                    if ext in media_extensions or entry.lower() in media_extensions:
                        # Media file: include only the file name
                        tree_lines.append(f"{indent}- {entry}")
                    else:
                        tree_lines.append(f"{indent}- {entry}")
                        if ext in selected_extensions or entry in selected_extensions:
                            try:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                # Determine the language for code blocks
                                language = ext.replace('.', '') if ext.startswith('.') else ext
                                if language in ['Dockerfile', 'nginx.conf']:
                                    language = 'conf'
                                # Include the relative path as a comment inside the code block
                                relative_file_path = os.path.relpath(full_path, base_path)
                                tree_lines.append(f"{indent}    ```{language}")
                                tree_lines.append(f"{indent}    /* {relative_file_path} */")
                                tree_lines.append(content)
                                tree_lines.append(f"{indent}    ```")
                            except UnicodeDecodeError:
                                errors.append(f"Binary or undecodable file skipped: {full_path}")
                            except Exception as e:
                                errors.append(f"Error reading {full_path}: {e}")

        traverse(base_path, 0)
        return "\n".join(tree_lines)

def main():
    root = tk.Tk()
    app = TreeGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
