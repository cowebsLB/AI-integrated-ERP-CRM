"""
AI Chat view for interacting with TinyLlama.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont
from src.ai.data_aware_ai import DataAwareAI
import logging

logger = logging.getLogger(__name__)


class AIResponseThread(QThread):
    """Thread for generating AI responses without blocking UI."""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data_aware_ai, message, conversation_history):
        super().__init__()
        self.data_aware_ai = data_aware_ai
        self.message = message
        self.conversation_history = conversation_history
    
    def run(self):
        """Generate AI response in background thread."""
        try:
            response = self.data_aware_ai.answer_question(self.message, self.conversation_history)
            self.response_ready.emit(response)
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            self.error_occurred.emit(str(e))


class AIChatView(QWidget):
    """View for AI chat interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_aware_ai = DataAwareAI()
        self.conversation_history = []
        self.response_thread = None
        self.init_ui()
        
        # Check if AI is available
        if not self.data_aware_ai.ai_service.is_available():
            self.show_ai_unavailable_message()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("AI Assistant")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: green;")
        header_layout.addWidget(self.status_label)
        
        # Clear button
        clear_button = QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_chat)
        header_layout.addWidget(clear_button)
        
        layout.addLayout(header_layout)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Add welcome message
        self.add_system_message("Welcome to AI Assistant! How can I help you today?")
        
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 11px;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
    
    def add_message(self, role: str, message: str, is_system: bool = False):
        """Add a message to the chat display."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if is_system:
            # System message styling
            html = f'<div style="color: #666; font-style: italic; margin: 10px 0;">{message}</div>'
        elif role == "user":
            # User message styling (right aligned)
            html = f'''
            <div style="margin: 10px 0; text-align: right;">
                <div style="display: inline-block; background-color: #0078d4; color: white; padding: 8px 12px; border-radius: 10px; max-width: 70%;">
                    {message}
                </div>
            </div>
            '''
        else:
            # Assistant message styling (left aligned)
            html = f'''
            <div style="margin: 10px 0;">
                <div style="display: inline-block; background-color: #e8e8e8; color: #333; padding: 8px 12px; border-radius: 10px; max-width: 70%;">
                    {message}
                </div>
            </div>
            '''
        
        cursor.insertHtml(html)
        cursor.insertHtml("<br>")
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def add_system_message(self, message: str):
        """Add a system message."""
        self.add_message("system", message, is_system=True)
    
    def send_message(self):
        """Send a message to the AI."""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Check if AI is available (but data queries work even without AI)
        # if not self.data_aware_ai.ai_service.is_available():
        #     QMessageBox.warning(
        #         self,
        #         "AI Not Available",
        #         "AI service is not available. Please install Ollama and pull the tinyllama model.\n\n"
        #         "See OLLAMA_SETUP.md for instructions."
        #     )
        #     return
        
        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("Thinking...")
        self.status_label.setStyleSheet("color: orange;")
        
        # Add user message to display
        self.add_message("user", message)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Clear input
        self.message_input.clear()
        
        # Generate response in background thread
        self.response_thread = AIResponseThread(
            self.data_aware_ai,
            message,
            self.conversation_history.copy()
        )
        self.response_thread.response_ready.connect(self.on_response_received)
        self.response_thread.error_occurred.connect(self.on_error)
        self.response_thread.start()
    
    def on_response_received(self, response: str):
        """Handle AI response."""
        # Add assistant message to display
        self.add_message("assistant", response)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: green;")
        
        # Focus input
        self.message_input.setFocus()
    
    def on_error(self, error: str):
        """Handle error."""
        error_msg = f"Error: {error}"
        self.add_message("system", error_msg, is_system=True)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("color: red;")
        
        # Focus input
        self.message_input.setFocus()
    
    def clear_chat(self):
        """Clear the chat history."""
        self.chat_display.clear()
        self.conversation_history = []
        self.add_system_message("Chat cleared. How can I help you?")
    
    def show_ai_unavailable_message(self):
        """Show message when AI is not available."""
        self.add_system_message(
            "⚠️ AI service is not available. Please install Ollama and pull the tinyllama model.\n\n"
            "Steps:\n"
            "1. Install Ollama from https://ollama.ai\n"
            "2. Run: ollama pull tinyllama\n"
            "3. Restart the application\n\n"
            "See OLLAMA_SETUP.md for detailed instructions."
        )
        self.status_label.setText("Not Available")
        self.status_label.setStyleSheet("color: red;")

