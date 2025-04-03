import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os
import datetime
import re
import threading
import time

class ClipboardHistoryTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard History Tool")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        
        # Set up data structures
        self.history = []
        self.max_history_size = 100
        self.current_clipboard = ""
        self.monitoring = True
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clipboard_history.json")
        
        # Create UI elements
        self.create_ui()
        
        # Load history from file
        self.load_history()
        
        # Start clipboard monitoring
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        
        # Set up auto-save
        self.root.after(30000, self.auto_save)  # Save every 30 seconds
    
    def create_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear search button
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
        
        # History list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History listbox
        self.history_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("TkDefaultFont", 10))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Bind selection event
        self.history_listbox.bind("<<ListboxSelect>>", self.on_item_select)
        self.history_listbox.bind("<Double-1>", self.on_item_double_click)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Copy button
        ttk.Button(control_frame, text="Copy Selected", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        ttk.Button(control_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear all button
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        
        # Monitoring toggle
        self.monitor_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Monitor Clipboard", variable=self.monitor_var, 
                        command=self.toggle_monitoring).pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def monitor_clipboard(self):
        """Monitor the clipboard for changes in a separate thread"""
        try:
            # Initialize with current clipboard content
            self.current_clipboard = pyperclip.paste()
            
            while True:
                if self.monitoring:
                    try:
                        # Get current clipboard content
                        clipboard_content = pyperclip.paste()
                        
                        # Check if content has changed
                        if clipboard_content != self.current_clipboard and clipboard_content.strip():
                            self.current_clipboard = clipboard_content
                            
                            # Add to history in the main thread
                            self.root.after(0, lambda: self.add_to_history(clipboard_content))
                    except Exception as e:
                        print(f"Error monitoring clipboard: {e}")
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)
        except Exception as e:
            print(f"Monitor thread error: {e}")
    
    def add_to_history(self, content):
        """Add new content to history"""
        # Skip if content is already at the top of history
        if self.history and self.history[0]["content"] == content:
            return
        
        # Create new history item
        timestamp = datetime.datetime.now().isoformat()
        item = {
            "id": str(int(time.time() * 1000)),  # Unique ID based on timestamp
            "content": content,
            "timestamp": timestamp,
            "content_type": "text"
        }
        
        # Add to history
        self.history.insert(0, item)
        
        # Limit history size
        if len(self.history) > self.max_history_size:
            self.history = self.history[:self.max_history_size]
        
        # Update UI
        self.update_listbox()
        self.status_var.set(f"Added new item ({len(self.history)} items in history)")
    
    def update_listbox(self):
        """Update the listbox with current history items"""
        self.history_listbox.delete(0, tk.END)
        
        search_term = self.search_var.get().lower()
        
        for item in self.history:
            content = item["content"]
            # Truncate long content for display
            display_text = content[:60] + "..." if len(content) > 60 else content
            # Replace newlines with spaces for display
            display_text = display_text.replace("\n", " ")
            
            # If searching, only show matching items
            if not search_term or search_term in content.lower():
                self.history_listbox.insert(tk.END, display_text)
    
    def filter_history(self, *args):
        """Filter history based on search term"""
        self.update_listbox()
    
    def clear_search(self):
        """Clear the search field"""
        self.search_var.set("")
    
    def on_item_select(self, event):
        """Handle item selection"""
        if not self.history_listbox.curselection():
            return
        
        index = self.history_listbox.curselection()[0]
        search_term = self.search_var.get().lower()
        
        # Find the actual history index considering the search filter
        actual_index = 0
        for i, item in enumerate(self.history):
            if not search_term or search_term in item["content"].lower():
                if actual_index == index:
                    self.status_var.set(f"Selected item from {item['timestamp'].split('T')[0]}")
                    break
                actual_index += 1
    
    def on_item_double_click(self, event):
        """Handle double click on an item"""
        self.copy_selected()
    
    def copy_selected(self):
        """Copy selected item to clipboard"""
        if not self.history_listbox.curselection():
            messagebox.showinfo("Info", "No item selected")
            return
        
        index = self.history_listbox.curselection()[0]
        search_term = self.search_var.get().lower()
        
        # Find the actual history index considering the search filter
        actual_index = 0
        selected_item = None
        
        for i, item in enumerate(self.history):
            if not search_term or search_term in item["content"].lower():
                if actual_index == index:
                    selected_item = item
                    break
                actual_index += 1
        
        if selected_item:
            # Temporarily disable monitoring to avoid re-adding the same content
            old_monitoring = self.monitoring
            self.monitoring = False
            
            # Copy to clipboard
            pyperclip.copy(selected_item["content"])
            
            # Update status
            self.status_var.set("Copied to clipboard")
            
            # Re-enable monitoring after a short delay
            self.root.after(1000, lambda: setattr(self, 'monitoring', old_monitoring))
    
    def delete_selected(self):
        """Delete selected item from history"""
        if not self.history_listbox.curselection():
            messagebox.showinfo("Info", "No item selected")
            return
        
        index = self.history_listbox.curselection()[0]
        search_term = self.search_var.get().lower()
        
        # Find the actual history index considering the search filter
        actual_index = 0
        history_index = -1
        
        for i, item in enumerate(self.history):
            if not search_term or search_term in item["content"].lower():
                if actual_index == index:
                    history_index = i
                    break
                actual_index += 1
        
        if history_index >= 0:
            del self.history[history_index]
            self.update_listbox()
            self.status_var.set(f"Item deleted ({len(self.history)} items remaining)")
    
    def clear_all(self):
        """Clear all history items"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            self.history = []
            self.update_listbox()
            self.status_var.set("History cleared")
    
    def toggle_monitoring(self):
        """Toggle clipboard monitoring"""
        self.monitoring = self.monitor_var.get()
        status = "enabled" if self.monitoring else "disabled"
        self.status_var.set(f"Monitoring {status}")
    
    def load_history(self):
        """Load history from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get("items", [])
                    self.max_history_size = data.get("max_items", 100)
                
                self.update_listbox()
                self.status_var.set(f"Loaded {len(self.history)} items from history")
        except Exception as e:
            self.status_var.set(f"Error loading history: {e}")
    
    def save_history(self):
        """Save history to file"""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "max_items": self.max_history_size,
                "items": self.history
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.status_var.set(f"Saved {len(self.history)} items to history")
            return True
        except Exception as e:
            self.status_var.set(f"Error saving history: {e}")
            return False
    
    def auto_save(self):
        """Automatically save history periodically"""
        self.save_history()
        # Schedule next auto-save
        self.root.after(30000, self.auto_save)  # Every 30 seconds

def main():
    root = tk.Tk()
    app = ClipboardHistoryTool(root)
    
    # Handle window close
    def on_closing():
        app.save_history()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
