"""
NostalgiKit - Vintage Handheld Gaming Hub
Main launcher for the NostalgiKit
Run this file to start the retro gaming experience

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def set_window_icon(window):
    """Set the application icon for a window"""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            # Try with PIL first for better compatibility
            try:
                from PIL import Image, ImageTk
                pil_image = Image.open(icon_path)
                # Resize if necessary for icon
                if pil_image.size != (32, 32):
                    pil_image = pil_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(pil_image)
                window.iconphoto(False, icon)

                # Also set taskbar icon on Windows by generating a temporary ICO
                try:
                    import tempfile
                    ico_path = os.path.join(tempfile.gettempdir(), 'nostalgikit_icon.ico')
                    pil_image.save(ico_path, format='ICO')
                    window.iconbitmap(default=ico_path)
                except Exception:
                    pass
            except Exception:
                # Fallback to PhotoImage
                icon = tk.PhotoImage(file=icon_path)
                window.iconphoto(False, icon)
    except Exception:
        pass  # If icon loading fails, continue without it

def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import tkinter
    except ImportError:
        missing_packages.append("tkinter")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_packages.append("Pillow")

    try:
        import pygame
    except ImportError:
        missing_packages.append("pygame")
    
    if missing_packages:
        root = tk.Tk()
        root.withdraw()
        set_window_icon(root)
        messagebox.showerror(
            "Missing Dependencies", 
            f"The following packages are required but not installed:\n" +
            "\n".join(missing_packages) +
            "\n\nPlease install them using:\npip install Pillow pygame"
        )
        return False
    
    return True

def main():
    """Main entry point"""
    try:
        # Check dependencies first
        if not check_dependencies():
            return
        
        # Import and start the NostalgiKit
        from game_hub import NostalgiKitHub
        
        app = NostalgiKitHub()
        app.run()
        
    except Exception as e:
        # Fallback error handling
        root = tk.Tk()
        root.withdraw()
        set_window_icon(root)
        messagebox.showerror(
            "Error", 
            f"An error occurred while starting the game hub:\n{str(e)}\n\n" +
            "Please make sure all game files are in the same directory."
        )

if __name__ == "__main__":
    main()
