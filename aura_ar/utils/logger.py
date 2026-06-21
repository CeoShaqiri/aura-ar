import sys
from datetime import datetime


class Logger:
    """Simple logging utility for the addon"""
    
    def __init__(self, name="WebXR"):
        self.name = name
        self.debug_mode = False
    
    def info(self, message):
        """Log info message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{self.name}] {timestamp} - ℹ️  {message}")
    
    def warning(self, message):
        """Log warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{self.name}] {timestamp} - ⚠️  {message}")
    
    def error(self, message):
        """Log error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{self.name}] {timestamp} - ❌ {message}")
    
    def debug(self, message):
        """Log debug message (only if debug mode enabled)"""
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{self.name}] {timestamp} - 🔍 {message}")


def get_logger(name="WebXR"):
    """Get or create a logger instance"""
    return Logger(name)
