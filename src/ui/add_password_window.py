import customtkinter as ctk

# --- STYLE CONSTANTS ---
WINDOW_TITLE = "S.A.V.E. - Add Password"
WINDOW_SIZE = "500x500"

# Padding constants
PADDING_TITLE = (20, 15)
PADDING_INPUT = 10
PADDING_BUTTON = (20, 20)

# Component Dimensions
ELEMENT_WIDTH = 300
FONT_TITLE = ("Urbanist", 18, "bold")
FONT_ERROR = ("Urbanist", 11, "bold")
FONT_LABEL = ("Urbanist", 11)

# Color Palette
COLOR_SUCCESS = "#2ecc71"
COLOR_SUCCESS_HOVER = "#27ae60"

# Validation constants
MIN_INPUT_LENGTH = 1
MAX_INPUT_LENGTH = 256


class AddPasswordWindow(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.result = None
        
        # Configure Window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        self._initialize_ui()
        
    def _initialize_ui(self):
        """Assembles the dialog components."""
        self._build_header()
        self._build_input_fields()
        self._build_error_display()
        self._build_action_buttons()
        
    def _build_header(self):
        self.title_label = ctk.CTkLabel(
            self, text="Add New Password", font=FONT_TITLE
        )
        self.title_label.pack(pady=PADDING_TITLE)
        
    def _build_input_fields(self):
        # Site/Service name
        site_label = ctk.CTkLabel(self, text="Site/Service Name:", font=FONT_LABEL)
        site_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.site_entry = ctk.CTkEntry(
            self, placeholder_text="e.g., Gmail, GitHub, Bank", width=ELEMENT_WIDTH
        )
        self.site_entry.pack(pady=PADDING_INPUT, padx=20)
        
        # Username/Email
        user_label = ctk.CTkLabel(self, text="Username/Email:", font=FONT_LABEL)
        user_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.username_entry = ctk.CTkEntry(
            self, placeholder_text="e.g., user@example.com", width=ELEMENT_WIDTH
        )
        self.username_entry.pack(pady=PADDING_INPUT, padx=20)
        
        # Password
        password_label = ctk.CTkLabel(self, text="Password:", font=FONT_LABEL)
        password_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            self, placeholder_text="Enter password", show="*", width=ELEMENT_WIDTH
        )
        self.password_entry.pack(pady=PADDING_INPUT, padx=20)
        
    def _build_error_display(self):
        """Error message label for displaying validation errors."""
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONT_ERROR, text_color="#FF6B6B"
        )
        self.error_label.pack(pady=10, padx=20)
        
    def _build_action_buttons(self):
        """Create Save and Cancel buttons with proper spacing."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=PADDING_BUTTON, padx=20, fill="x", expand=True)
        
        self.save_btn = ctk.CTkButton(
            button_frame, 
            text="Save Password", 
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            font=("Urbanist", 13, "bold"),
            command=self._on_save_click
        )
        self.save_btn.pack(side="left", padx=10, fill="x", expand=True)
        
        self.cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            width=150,
            height=40,
            font=("Urbanist", 13, "bold"),
            command=self._on_cancel_click
        )
        self.cancel_btn.pack(side="left", padx=10, fill="x", expand=True)

    def _on_save_click(self):
        """Validates input and saves password entry."""
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate input
        validation_error = self._validate_input(site, username, password)
        if validation_error:
            self._show_error(validation_error)
            return
        
        # Clear error
        self._clear_error()
        
        # Create entry dict
        entry = {
            "site": site,
            "username": username,
            "password": password
        }
        
        # Add to vault via controller
        try:
            success = self.controller.add_password_entry(entry)
            if success:
                self.result = entry
                self.destroy()
            else:
                self._show_error("Failed to save password. Try again.")
        except Exception as e:
            self._show_error(f"Error: {str(e)}")

    def _on_cancel_click(self):
        """Close the dialog without saving."""
        self.destroy()

    def _validate_input(self, site, username, password):
        """Validate input fields. Returns error message or None if valid."""
        if not site or not username or not password:
            return "All fields are required."
        
        if len(site) < MIN_INPUT_LENGTH:
            return "Site name cannot be empty."
        
        if len(site) > MAX_INPUT_LENGTH:
            return f"Site name must be under {MAX_INPUT_LENGTH} characters."
        
        if len(username) > MAX_INPUT_LENGTH:
            return f"Username must be under {MAX_INPUT_LENGTH} characters."
        
        if len(password) > MAX_INPUT_LENGTH:
            return f"Password must be under {MAX_INPUT_LENGTH} characters."
        
        return None  # Valid

    def _show_error(self, error_message):
        """Display error message to user."""
        self.error_label.configure(text=error_message, text_color="#FF6B6B")

    def _clear_error(self):
        """Clear any displayed error messages."""
        self.error_label.configure(text="")
