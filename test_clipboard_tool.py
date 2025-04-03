import unittest
import os
import json
import time
import pyperclip
from clipboard_history_tool import ClipboardHistoryTool
import tkinter as tk

class MockRoot:
    """Mock Tkinter root for testing"""
    def __init__(self):
        self.title_text = ""
        self.geometry_text = ""
        self.protocol_func = None
        self.after_calls = []
        self.minsize_width = 0
        self.minsize_height = 0
    
    def title(self, text):
        self.title_text = text
    
    def geometry(self, text):
        self.geometry_text = text
    
    def protocol(self, protocol, func):
        self.protocol_func = func
    
    def after(self, ms, func):
        self.after_calls.append((ms, func))
        return 1  # Return an ID
    
    def minsize(self, width, height):
        self.minsize_width = width
        self.minsize_height = height

class TestClipboardHistoryTool(unittest.TestCase):
    def setUp(self):
        # Create a temporary test file
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_file = os.path.join(self.test_dir, "test_history.json")
        
        # Create mock root
        self.root = MockRoot()
        
        # Initialize the tool with mock root
        self.tool = ClipboardHistoryTool(self.root)
        self.tool.data_file = self.test_file  # Override data file
        
        # Clear any existing test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def tearDown(self):
        # Clean up test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_initialization(self):
        """Test that the tool initializes correctly"""
        self.assertEqual(self.root.title_text, "Clipboard History Tool")
        self.assertEqual(self.root.geometry_text, "600x500")
        self.assertEqual(self.root.minsize_width, 400)
        self.assertEqual(self.root.minsize_height, 300)
        self.assertEqual(len(self.tool.history), 0)
        self.assertEqual(self.tool.max_history_size, 100)
        self.assertTrue(self.tool.monitoring)
    
    def test_add_to_history(self):
        """Test adding items to history"""
        # Add a test item
        test_content = "Test clipboard content"
        self.tool.add_to_history(test_content)
        
        # Check that it was added
        self.assertEqual(len(self.tool.history), 1)
        self.assertEqual(self.tool.history[0]["content"], test_content)
        
        # Add another item
        test_content2 = "Another test content"
        self.tool.add_to_history(test_content2)
        
        # Check that it was added at the beginning
        self.assertEqual(len(self.tool.history), 2)
        self.assertEqual(self.tool.history[0]["content"], test_content2)
        
        # Add duplicate content (should not add)
        self.tool.add_to_history(test_content2)
        self.assertEqual(len(self.tool.history), 2)
    
    def test_history_limit(self):
        """Test that history size is limited"""
        # Set a small limit for testing
        self.tool.max_history_size = 3
        
        # Add more items than the limit
        for i in range(5):
            self.tool.add_to_history(f"Test content {i}")
        
        # Check that only the limit is kept
        self.assertEqual(len(self.tool.history), 3)
        self.assertEqual(self.tool.history[0]["content"], "Test content 4")
        self.assertEqual(self.tool.history[1]["content"], "Test content 3")
        self.assertEqual(self.tool.history[2]["content"], "Test content 2")
    
    def test_save_and_load_history(self):
        """Test saving and loading history"""
        # Add some test items
        test_items = ["Item 1", "Item 2", "Item 3"]
        for item in test_items:
            self.tool.add_to_history(item)
        
        # Save history
        self.tool.save_history()
        
        # Check that file exists
        self.assertTrue(os.path.exists(self.test_file))
        
        # Create a new tool instance
        new_tool = ClipboardHistoryTool(MockRoot())
        new_tool.data_file = self.test_file
        
        # Load history
        new_tool.load_history()
        
        # Check that history was loaded correctly
        self.assertEqual(len(new_tool.history), 3)
        self.assertEqual(new_tool.history[0]["content"], "Item 3")
        self.assertEqual(new_tool.history[1]["content"], "Item 2")
        self.assertEqual(new_tool.history[2]["content"], "Item 1")
    
    def test_search_functionality(self):
        """Test search functionality"""
        # Add test items
        test_items = ["Apple", "Banana", "Apple pie", "Orange"]
        for item in test_items:
            self.tool.add_to_history(item)
        
        # Set up search
        self.tool.search_var = tk.StringVar()
        
        # Test with no search term
        self.tool.search_var.set("")
        matching_items = [item for item in self.tool.history 
                         if not self.tool.search_var.get().lower() 
                         or self.tool.search_var.get().lower() in item["content"].lower()]
        self.assertEqual(len(matching_items), 4)
        
        # Test with search term
        self.tool.search_var.set("apple")
        matching_items = [item for item in self.tool.history 
                         if not self.tool.search_var.get().lower() 
                         or self.tool.search_var.get().lower() in item["content"].lower()]
        self.assertEqual(len(matching_items), 2)
        self.assertEqual(matching_items[0]["content"], "Apple pie")
        self.assertEqual(matching_items[1]["content"], "Apple")
    
    def test_delete_functionality(self):
        """Test deleting items from history"""
        # Add test items
        test_items = ["Item 1", "Item 2", "Item 3"]
        for item in test_items:
            self.tool.add_to_history(item)
        
        # Delete the middle item (index 1)
        del self.tool.history[1]
        
        # Check that it was deleted
        self.assertEqual(len(self.tool.history), 2)
        self.assertEqual(self.tool.history[0]["content"], "Item 3")
        self.assertEqual(self.tool.history[1]["content"], "Item 1")
    
    def test_clear_all(self):
        """Test clearing all history"""
        # Add test items
        test_items = ["Item 1", "Item 2", "Item 3"]
        for item in test_items:
            self.tool.add_to_history(item)
        
        # Clear all (simulate user confirming)
        original_askyesno = tk.messagebox.askyesno
        tk.messagebox.askyesno = lambda *args, **kwargs: True
        
        try:
            self.tool.clear_all()
            
            # Check that history is empty
            self.assertEqual(len(self.tool.history), 0)
        finally:
            # Restore original function
            tk.messagebox.askyesno = original_askyesno

if __name__ == "__main__":
    unittest.main()
