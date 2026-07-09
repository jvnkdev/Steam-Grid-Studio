#!/usr/bin/env python3
"""
Steam Grid Studio - GUI
A simple point-and-click window for generating Steam artwork,
no typing commands required.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from steamgrid import STYLES, SIZES


class SteamGridGUI:
    def __init__(self, root):
        self.root = root
        root.title("Steam Grid Studio")
        root.geometry("420x320")
        root.resizable(False, False)

        padding = {"padx": 16, "pady": 8}

        # Game name
        tk.Label(root, text="Game name", font=("Segoe UI", 10, "bold")).pack(anchor="w", **padding)
        self.game_entry = tk.Entry(root, font=("Segoe UI", 11))
        self.game_entry.pack(fill="x", padx=16)
        self.game_entry.insert(0, "Half-Life 2")

        # Style dropdown
        tk.Label(root, text="Style", font=("Segoe UI", 10, "bold")).pack(anchor="w", **padding)
        self.style_var = tk.StringVar(value=list(STYLES.keys())[0])
        style_dropdown = ttk.Combobox(
            root, textvariable=self.style_var, values=list(STYLES.keys()), state="readonly", font=("Segoe UI", 11)
        )
        style_dropdown.pack(fill="x", padx=16)

        # Output folder
        tk.Label(root, text="Output folder", font=("Segoe UI", 10, "bold")).pack(anchor="w", **padding)
        folder_frame = tk.Frame(root)
        folder_frame.pack(fill="x", padx=16)
        self.output_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        tk.Entry(folder_frame, textvariable=self.output_var, font=("Segoe UI", 10)).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(folder_frame, text="Browse...", command=self.browse_folder).pack(side="left", padx=(6, 0))

        # Generate button
        self.generate_btn = tk.Button(
            root,
            text="Generate Artwork",
            font=("Segoe UI", 11, "bold"),
            bg="#5ac8fa",
            command=self.generate,
        )
        self.generate_btn.pack(pady=20, ipadx=10, ipady=6)

        # Status label
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status_var, fg="gray").pack(pady=(0, 8))

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def generate(self):
        game_name = self.game_entry.get().strip()
        if not game_name:
            messagebox.showwarning("Missing info", "Please enter a game name.")
            return

        style = self.style_var.get()
        output_dir = self.output_var.get().strip() or "output"

        self.generate_btn.config(state="disabled")
        self.status_var.set("Generating...")
        self.root.update_idletasks()

        thread = threading.Thread(target=self._run_generate, args=(game_name, style, output_dir))
        thread.start()

    def _run_generate(self, game_name, style, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            render_fn = STYLES[style]
            safe_name = "".join(c for c in game_name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")

            saved_paths = []
            for asset_name, size in SIZES.items():
                img = render_fn(size, game_name)
                out_path = os.path.join(output_dir, f"{safe_name}_{asset_name}_{style}.png")
                img.save(out_path)
                saved_paths.append(out_path)

            self.root.after(0, self._on_success, saved_paths, output_dir)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_success(self, saved_paths, output_dir):
        self.status_var.set(f"Done! Saved {len(saved_paths)} images to {output_dir}")
        self.generate_btn.config(state="normal")
        messagebox.showinfo("Success", f"Generated {len(saved_paths)} images in:\n{output_dir}")

    def _on_error(self, error_message):
        self.status_var.set("Error occurred.")
        self.generate_btn.config(state="normal")
        messagebox.showerror("Error", error_message)


def main():
    root = tk.Tk()
    SteamGridGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
