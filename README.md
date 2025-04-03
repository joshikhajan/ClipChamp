# Clipboard History Tool

A simple clipboard history manager that tracks and stores clipboard contents, allowing you to search through your clipboard history and reuse previously copied items.

## Features

- Monitors clipboard changes in real-time
- Maintains a searchable history of clipboard items
- Allows you to select and re-copy previous items
- Automatically saves history between sessions
- Clean, user-friendly interface

## Installation

### Prerequisites

- Python 3.6 or higher
- Tkinter (usually comes with Python, but may need to be installed separately)
- pyperclip

### Option 1: Install from source

1. Clone or download this repository
2. Navigate to the directory containing the code
3. Install the required dependencies:
   ```
   pip install pyperclip
   ```
4. Install the application:
   ```
   pip install -e .
   ```

### Option 2: Install using pip

```
pip install clipboard-history-tool
```

## Usage

### Starting the application

After installation, you can start the application by running:

```
clipboard-history-tool
```

Or you can run it directly from the source directory:

```
python manual_test.py
```

### Using the application

1. **Monitoring clipboard**: The application automatically monitors your clipboard and adds new content to the history.

2. **Viewing history**: All clipboard items are displayed in the main window, with the most recent at the top.

3. **Searching**: Use the search box at the top to filter items in your clipboard history.

4. **Reusing items**: 
   - Click on an item to select it
   - Click "Copy Selected" or double-click the item to copy it back to your clipboard
   - Paste it wherever you need using your system's paste command (Ctrl+V or Command+V)

5. **Managing history**:
   - "Delete Selected" removes the selected item from history
   - "Clear All" removes all items from history
   - Toggle "Monitor Clipboard" to temporarily disable monitoring

## Configuration

The application stores its configuration and history in a JSON file located at:
- `~/.local/share/clipboard_history_tool/clipboard_history.json` (Linux/macOS)
- `%APPDATA%\clipboard_history_tool\clipboard_history.json` (Windows)

## Troubleshooting

### Common issues:

1. **Application doesn't start**: Ensure Python and Tkinter are properly installed.

2. **Clipboard monitoring not working**: Some applications use special clipboard formats that may not be detected. Try copying text from a different application.

3. **Missing dependencies**: Make sure you have installed all required dependencies:
   ```
   pip install pyperclip
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
