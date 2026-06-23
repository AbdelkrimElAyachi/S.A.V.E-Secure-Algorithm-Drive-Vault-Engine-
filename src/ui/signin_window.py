import customtkinter as ctk

# --- STYLE CONSTANTS ---
WINDOW_TITLE = "S.A.V.E. - Create New Vault"
WINDOW_SIZE = "400x500"

# Padding constants: (Top, Bottom)
PADDING_HEADER = (40, 10)
PADDING_SUBTEXT = (0, 25)
PADDING_INPUT = (10, 10)
PADDING_BUTTON = (30, 10)

# Component Dimensions
ELEMENT_WIDTH = 280
FONT_HEADER = ("Urbanist", 22, "bold")
FONT_SUBTEXT = ("Urbanist", 12)
FONT_ERROR = ("Urbanist", 12, "bold")

# Color Palette
COLOR_SUCCESS = "#2ecc71"
COLOR_SUCCESS_HOVER = "#27ae60"

# Validation constants
MIN_PASSWORD_LENGTH = 8  # Minimum password length required
MAX_PASSWORD_LENGTH = 128  # Maximum password length


class SigninWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Configure Window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        
        self._initialize_ui()
        
    def _initialize_ui(self):
        """Assembles the visual components in a clean, readable sequence."""
        self._build_header_section()
        self._build_input_fields()
        self._build_error_display()
        self._build_action_buttons()

    def _build_header_section(self):
        self.header = ctk.CTkLabel(
            self, text="Initialize Secure Vault", font=FONT_HEADER
        )
        self.header.pack(pady=PADDING_HEADER)

        self.desc = ctk.CTkLabel(
            self, 
            text="Set your Master Password. This cannot be recovered.",
            font=FONT_SUBTEXT, 
            text_color="gray"
        )
        self.desc.pack(pady=PADDING_SUBTEXT)
        
    def _build_input_fields(self):
        self.pass_entry = ctk.CTkEntry(
            self, placeholder_text="New Master Password", show="*", width=ELEMENT_WIDTH
        )
        self.pass_entry.pack(pady=PADDING_INPUT)
        
        self.confirm_entry = ctk.CTkEntry(
            self, placeholder_text="Confirm Master Password", show="*", width=ELEMENT_WIDTH
        )
        self.confirm_entry.pack(pady=PADDING_INPUT)
        
    def _build_error_display(self):
        """Error message label for displaying validation errors."""
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONT_ERROR, text_color="#FF6B6B"
        )
        self.error_label.pack(pady=5)
        
    def _build_action_buttons(self):
        self.create_btn = ctk.CTkButton(
            self, 
            text="Create Vault", 
            width=ELEMENT_WIDTH, 
            fg_color=COLOR_SUCCESS, 
            hover_color=COLOR_SUCCESS_HOVER,
            command=self._on_create_click
        )
        self.create_btn.pack(pady=PADDING_BUTTON)

    def _on_create_click(self):
        """Validates passwords and creates vault if all checks pass."""
        p1 = self.pass_entry.get()
        p2 = self.confirm_entry.get()
        
        # Validate password input
        validation_error = self._validate_password(p1, p2)
        if validation_error:
            self._show_error(validation_error)
            return
        
        # Clear any previous error messages
        self._clear_error()
        
        # Create vault with validated password
        try:
            self.controller.initialize_vault(p1)
        except Exception as e:
            self._show_error(f"Vault creation failed: {str(e)}")
            return
    
    def _validate_password(self, password, confirm_password):
        """Validate passwords meet requirements. Returns error message or None if valid."""
        if not password or not confirm_password:
            return "All fields are required."
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        
        if len(password) > MAX_PASSWORD_LENGTH:
            return f"Password must be no more than {MAX_PASSWORD_LENGTH} characters."
        
        if password != confirm_password:
            return "Passwords do not match."
        
        return None  # Valid
    
    def _show_error(self, error_message):
        """Display error message to user."""
        self.error_label.configure(text=error_message, text_color="#FF6B6B")
    
    def _clear_error(self):
        """Clear any displayed error messages."""
        self.error_label.configure(text="")