import customtkinter as ctk

# --- STYLE CONSTANTS ---
WINDOW_TITLE = "S.A.V.E. - Authenticate"
WINDOW_SIZE = "400x350"

# Padding constants: (Top, Bottom) or single integer
PADDING_TITLE = (30, 20)
PADDING_INPUT = 10
PADDING_BUTTON = (20, 10)

# Component Dimensions
ELEMENT_WIDTH = 250
FONT_TITLE = ("Urbanist", 20, "bold")
FONT_ERROR = ("Urbanist", 12, "bold")

# Validation constants
MIN_PASSWORD_LENGTH = 1  # Minimum password length required
MAX_PASSWORD_LENGTH = 128  # Maximum password length


class LoginWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Configure Window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        
        self._initialize_ui()
        
    def _initialize_ui(self):
        """Assembles the login interface components."""
        self._build_header_section()
        self._build_input_fields()
        self._build_error_display()
        self._build_action_buttons()
        
    def _build_header_section(self):
        self.title_label = ctk.CTkLabel(
            self, text="Master Vault Login", font=FONT_TITLE
        )
        self.title_label.pack(pady=PADDING_TITLE)
        
    def _build_input_fields(self):
        self.password_entry = ctk.CTkEntry(
            self, placeholder_text="Enter Master Password", show="*", width=ELEMENT_WIDTH
        )
        self.password_entry.pack(pady=PADDING_INPUT)
        
    def _build_error_display(self):
        """Error message label for displaying validation/login errors."""
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONT_ERROR, text_color="#FF6B6B"
        )
        self.error_label.pack(pady=5)
        
    def _build_action_buttons(self):
        self.login_button = ctk.CTkButton(
            self, 
            text="Unlock Vault", 
            width=ELEMENT_WIDTH,
            command=self._on_login_click
        )
        self.login_button.pack(pady=PADDING_BUTTON)

    def _on_login_click(self):
        """Validates input and passes to Controller to handle authentication."""
        password = self.password_entry.get()
        
        # Validate password input
        validation_error = self._validate_password(password)
        if validation_error:
            self._show_error(validation_error)
            return
        
        # Clear any previous error messages
        self._clear_error()
        
        # Attempt login via controller
        success = self.controller.handle_login(password)
        
        # If login failed, show error and clear password field
        if not success:
            self._show_error("Invalid master password. Access denied.")
            self.password_entry.delete(0, "end")
    
    def _validate_password(self, password):
        """Validate password meets requirements. Returns error message or None if valid."""
        if not password:
            return "Password cannot be empty."
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return f"Password must be at least {MIN_PASSWORD_LENGTH} character(s)."
        
        if len(password) > MAX_PASSWORD_LENGTH:
            return f"Password must be no more than {MAX_PASSWORD_LENGTH} characters."
        
        return None  # Valid
    
    def _show_error(self, error_message):
        """Display error message to user."""
        self.error_label.configure(text=error_message, text_color="#FF6B6B")
    
    def _clear_error(self):
        """Clear any displayed error messages."""
        self.error_label.configure(text="")