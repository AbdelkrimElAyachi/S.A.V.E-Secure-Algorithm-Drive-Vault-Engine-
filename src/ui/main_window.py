import customtkinter as ctk
from tkinter import messagebox

# --- STYLE CONSTANTS ---
WINDOW_TITLE = "S.A.V.E. - Password Vault"
WINDOW_SIZE = "850x500"

# Component Dimensions
SIDEBAR_WIDTH = 200
ROW_FRAME_HEIGHT = 50
COPY_BTN_WIDTH = 60
COPY_BTN_HEIGHT = 25

# Padding Settings
PADDING_SIDEBAR_ELEMENTS = 20
PADDING_SIDEBAR_VERTICAL = 10
PADDING_CONTENT_FRAME = 20
PADDING_HEADER_LBL = (0, 10)
PADDING_ROW_FRAME_VERTICAL = 5
PADDING_INNER_ROW_WIDGETS = 15

# Typography
FONT_LOGO = ("Urbanist", 20, "bold")
FONT_HEADER = ("Urbanist", 18, "bold")
FONT_RECORD = ("Urbanist", 14)

# Color Palette
COLOR_DESTRUCTIVE = "#e74c3c"
COLOR_DESTRUCTIVE_HOVER = "#c0392b"


class MainWindow(ctk.CTk):
    def __init__(self, controller, session_key):
        super().__init__()
        self.controller = controller
        self.session_key = session_key  # 10-bit S-DES master session key
        
        # Configure Window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(True, True)
        
        self._initialize_layout_grid()
        self._initialize_ui()
        self._load_initial_entries()

    def _initialize_layout_grid(self):
        """Configures grid weights for layout distribution (Sidebar vs Content Area)."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _initialize_ui(self):
        """Assembles the primary regions of the vault dashboard."""
        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        """Creates the navigation and administrative control panel on the left."""
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # Maintain sidebar width
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="S.A.V.E. Vault", font=FONT_LOGO
        )
        self.logo_label.pack(
            pady=PADDING_SIDEBAR_ELEMENTS, 
            padx=PADDING_SIDEBAR_ELEMENTS
        )
        
        self.add_btn = ctk.CTkButton(
            self.sidebar, text="+ Add Password", command=self._on_add_password_click
        )
        self.add_btn.pack(
            pady=PADDING_SIDEBAR_VERTICAL, 
            padx=PADDING_SIDEBAR_ELEMENTS,
            fill="x"
        )
        
        self.lock_btn = ctk.CTkButton(
            self.sidebar, 
            text="Lock Vault", 
            fg_color=COLOR_DESTRUCTIVE, 
            hover_color=COLOR_DESTRUCTIVE_HOVER, 
            command=self._on_lock_click
        )
        self.lock_btn.pack(
            side="bottom", 
            pady=PADDING_SIDEBAR_ELEMENTS, 
            padx=PADDING_SIDEBAR_ELEMENTS,
            fill="x"
        )

    def _build_content_area(self):
        """Creates the main scrolling list region where decrypted records appear."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", 
            padx=PADDING_CONTENT_FRAME, pady=PADDING_CONTENT_FRAME
        )
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.header_label = ctk.CTkLabel(
            self.content_frame, text="Stored Credentials", font=FONT_HEADER
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=PADDING_HEADER_LBL)
        
        self.scrollable_vault = ctk.CTkScrollableFrame(self.content_frame)
        self.scrollable_vault.grid(row=1, column=0, sticky="nsew")
        self.scrollable_vault.grid_columnconfigure(0, weight=1)

    def refresh_records(self, decrypted_records_list):
        """Clears and visually maps a clean decrypted data array into UI listing entries."""
        # Clean out old visual widgets from the scroll view area
        for widget in self.scrollable_vault.winfo_children():
            widget.destroy()
        
        # Display empty state if no records
        if not decrypted_records_list:
            empty_label = ctk.CTkLabel(
                self.scrollable_vault, 
                text="No passwords stored yet.\nClick '+ Add Password' to get started.", 
                font=FONT_RECORD,
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
            
        # Dynamically build visual record frames line item by line item
        for record in decrypted_records_list:
            row_frame = ctk.CTkFrame(self.scrollable_vault, height=ROW_FRAME_HEIGHT)
            row_frame.pack(fill="x", pady=PADDING_ROW_FRAME_VERTICAL)
            row_frame.pack_propagate(False)
            
            label_text = f"Site: {record['site']}  |  User: {record['username']}"
            item_label = ctk.CTkLabel(row_frame, text=label_text, font=FONT_RECORD)
            item_label.pack(
                side="left", 
                padx=PADDING_INNER_ROW_WIDGETS, 
                pady=PADDING_INNER_ROW_WIDGETS
            )
            
            copy_btn = ctk.CTkButton(
                row_frame, text="Copy", 
                width=COPY_BTN_WIDTH, height=COPY_BTN_HEIGHT,
                command=lambda pwd=record['password']: self._copy_to_clipboard(pwd)
            )
            copy_btn.pack(
                side="right", 
                padx=PADDING_INNER_ROW_WIDGETS, 
                pady=PADDING_INNER_ROW_WIDGETS
            )

    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Password copied to clipboard safely!")

    def _on_add_password_click(self):
        """Opens the add password modal dialog."""
        self.controller.open_add_password_modal()

    def _on_lock_click(self):
        """Handler for lock vault button - clears session and returns to login."""
        self.controller.handle_vault_lock()

    def _load_initial_entries(self):
        """Load and display password entries on window startup."""
        try:
            decrypted_entries = self.controller.get_decrypted_entries()
            self.refresh_records(decrypted_entries)
            print(f"[UI] Loaded {len(decrypted_entries)} password entries")
        except Exception as e:
            print(f"[Error] Failed to load initial entries: {e}")