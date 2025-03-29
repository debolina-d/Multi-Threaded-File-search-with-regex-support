import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


def search_files(directory, pattern, file_extension='*', case_sensitive=False, show_lines=False, progress_callback=None):
    """
    Multi-threaded file search with regex support.
    """
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)

    total_files = sum(len(files) for _, _, files in os.walk(directory))
    current_file = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file_extension != '*' and not file.endswith(file_extension):
                continue

            file_path = os.path.join(root, file)
            current_file += 1

            # Update progress bar
            if progress_callback:
                progress_callback(current_file, total_files)

            try:
                # Streamed reading for large files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_number, line in enumerate(f, start=1):
                        if regex.search(line):
                            result = f"\nMatch in: {file_path}\nLine {line_number}"
                            if show_lines:
                                result += f"\n→ {line.strip()}"
                            results.append(result)

            except Exception as e:
                results.append(f"Error reading {file}: {e}")

    return results


def save_results(results, output_file="results.txt"):
    """ Save search results to a text file """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))


# GUI Functions
def browse_directory():
    """ Open file explorer to select directory """
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)


def update_progress(current, total):
    """ Update the progress bar """
    progress["value"] = (current / total) * 100
    root.update_idletasks()


def search_action():
    """ Perform the search in a separate thread """
    directory = entry_directory.get()
    pattern = entry_pattern.get()
    file_ext = entry_ext.get() or "*"
    case_sensitive = case_var.get()
    show_lines = lines_var.get()

    if not os.path.exists(directory):
        messagebox.showerror("Error", "Invalid directory path")
        return

    if not pattern:
        messagebox.showerror("Error", "Enter a valid regex pattern")
        return

    # Disable search button during search
    search_button.config(state=tk.DISABLED)
    result_display.delete(1.0, tk.END)

    def run_search():
        """ Thread function for the search """
        results = search_files(directory, pattern, file_ext, case_sensitive, show_lines, update_progress)

        if results:
            result_display.insert(tk.END, "\n".join(results))
            save_results(results)
            messagebox.showinfo("Success", "Search complete. Results saved to results.txt")
        else:
            messagebox.showinfo("No Results", "No matches found.")

        # Reset UI
        search_button.config(state=tk.NORMAL)
        progress["value"] = 0

    # Start the search in a separate thread
    threading.Thread(target=run_search).start()


# GUI Setup
root = tk.Tk()
root.title("Fast Text-Based File Search")
root.geometry("800x650")
root.configure(bg="#f0f0f0")

# Labels and Inputs
tk.Label(root, text="Directory:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entry_directory = tk.Entry(root, width=60)
entry_directory.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_directory).grid(row=0, column=2, padx=10)

tk.Label(root, text="Regex Pattern:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_pattern = tk.Entry(root, width=60)
entry_pattern.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="File Extension:", bg="#f0f0f0").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_ext = tk.Entry(root, width=20)
entry_ext.grid(row=2, column=1, sticky="w", padx=10, pady=5)

# Checkboxes
case_var = tk.BooleanVar()
tk.Checkbutton(root, text="Case Sensitive", variable=case_var, bg="#f0f0f0").grid(row=3, column=0, sticky="w", padx=10)

lines_var = tk.BooleanVar()
tk.Checkbutton(root, text="Show Matching Lines", variable=lines_var, bg="#f0f0f0").grid(row=3, column=1, sticky="w", padx=10)

# Progress Bar
progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Search Button
search_button = tk.Button(root, text="Search", command=search_action, bg="#4caf50", fg="white", width=15)
search_button.grid(row=5, column=0, columnspan=3, pady=10)

# Result Display
result_display = scrolledtext.ScrolledText(root, width=95, height=20)
result_display.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# Start the GUI loop
root.mainloop()
