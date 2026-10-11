# Theme module: Design tokens, ttk style configuration, and UI helper functions

import tkinter as tk
from tkinter import ttk

# Palette
BG_APP = "#F4F6F9"
BG_SURFACE = "#FFFFFF"
BG_SIDEBAR = "#1E293B"
TEXT_SIDEBAR = "#E2E8F0"
COLOR_PRIMARY = "#2563EB"
COLOR_PRIMARY_HOVER = "#1D4ED8"
COLOR_SUCCESS = "#16A34A"
COLOR_WARNING = "#D97706"
COLOR_DANGER = "#DC2626"
TEXT_MAIN = "#111827"
TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_ZEBRA = "#F9FAFB"
COLOR_SELECTED = "#DBEAFE"

# Status colors for table tags
STATUS_COLORS = {
    "Pending Drop-off": "#4B5563",
    "Received": "#2563EB",
    "Diagnosing": "#D97706",
    "Waiting for Parts": "#EA580C",
    "Under Repair": "#D97706",
    "Completed": "#16A34A",
    "Released": "#6B7280",
    "Cancelled": "#DC2626"
}

# Typography
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 12, "bold")
FONT_SUBHEADING = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_TABLE = ("Segoe UI", 10)
FONT_MUTED = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)

# Spacing scale
PAD_XS = 4
PAD_SM = 8
PAD_MD = 12
PAD_LG = 16
PAD_XL = 24


def enable_dpi_awareness():
    """Enable Per-Monitor DPI awareness on Windows for crisp rendering."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def center_window(win, width, height, min_w=None, min_h=None):
    """Centers a window or Toplevel on the screen and sets minimum size."""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
    if min_w and min_h:
        win.minsize(min_w, min_h)


def apply_theme(root):
    """Applies the modern light dashboard theme to all ttk widgets."""
    root.configure(bg=BG_APP)

    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # Base frames
    style.configure("TFrame", background=BG_APP)
    style.configure("Surface.TFrame", background=BG_SURFACE)
    style.configure("Sidebar.TFrame", background=BG_SIDEBAR)
    style.configure("Card.TFrame", background=BG_SURFACE, relief="solid", borderwidth=1)

    # Base labels
    style.configure("TLabel", background=BG_APP, foreground=TEXT_MAIN, font=FONT_BODY)
    style.configure("Surface.TLabel", background=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_BODY)
    style.configure("Muted.TLabel", background=BG_APP, foreground=TEXT_MUTED, font=FONT_MUTED)
    style.configure("SurfaceMuted.TLabel", background=BG_SURFACE, foreground=TEXT_MUTED, font=FONT_MUTED)
    style.configure("Title.TLabel", background=BG_APP, foreground=TEXT_MAIN, font=FONT_TITLE)
    style.configure("Section.TLabel", background=BG_APP, foreground=TEXT_MAIN, font=FONT_SECTION)
    style.configure("SurfaceSection.TLabel", background=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_SECTION)
    style.configure("SidebarHeader.TLabel", background=BG_SIDEBAR, foreground="#94A3B8", font=("Segoe UI", 9, "bold"))
    style.configure("Brand.TLabel", background=BG_SIDEBAR, foreground="#FFFFFF", font=("Segoe UI", 13, "bold"))

    # LabelFrames (Cards)
    style.configure("TLabelframe", background=BG_SURFACE, relief="solid", borderwidth=1)
    style.configure("TLabelframe.Label", background=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_SUBHEADING)

    # Inputs
    style.configure("TEntry", fieldbackground=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_BODY, padding=(6, 4))
    style.configure("TCombobox", fieldbackground=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_BODY, padding=(4, 4))
    style.configure("TSpinbox", fieldbackground=BG_SURFACE, foreground=TEXT_MAIN, font=FONT_BODY, padding=(4, 4))

    # Buttons
    style.configure(
        "Primary.TButton",
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(14, 6)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
        foreground=[("active", "#FFFFFF")]
    )

    style.configure(
        "Secondary.TButton",
        background=BG_SURFACE,
        foreground=TEXT_MAIN,
        font=FONT_BODY,
        relief="solid",
        borderwidth=1,
        focuscolor="none",
        padding=(12, 6)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLOR_ZEBRA), ("pressed", COLOR_BORDER)],
        foreground=[("active", TEXT_MAIN)]
    )

    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6)
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#B91C1C"), ("pressed", "#991B1B")],
        foreground=[("active", "#FFFFFF")]
    )

    # Sidebar Navigation Buttons
    style.configure(
        "Sidebar.TButton",
        background=BG_SIDEBAR,
        foreground=TEXT_SIDEBAR,
        font=FONT_BODY,
        anchor="w",
        relief="flat",
        borderwidth=0,
        focuscolor="none",
        padding=(14, 8)
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", "#334155"), ("pressed", "#0F172A")],
        foreground=[("active", "#FFFFFF")]
    )

    style.configure(
        "SidebarActive.TButton",
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        anchor="w",
        relief="flat",
        borderwidth=0,
        focuscolor="none",
        padding=(14, 8)
    )
    style.map(
        "SidebarActive.TButton",
        background=[("active", COLOR_PRIMARY_HOVER)],
        foreground=[("active", "#FFFFFF")]
    )

    # Treeview
    style.configure(
        "Treeview",
        background=BG_SURFACE,
        fieldbackground=BG_SURFACE,
        foreground=TEXT_MAIN,
        font=FONT_TABLE,
        rowheight=28,
        borderwidth=1,
        relief="solid"
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_SELECTED)],
        foreground=[("selected", TEXT_MAIN)]
    )

    style.configure(
        "Treeview.Heading",
        background=COLOR_BORDER,
        foreground=TEXT_MAIN,
        font=FONT_BODY_BOLD,
        relief="flat",
        padding=(6, 6)
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#D1D5DB")]
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLOR_BORDER,
        troughcolor=BG_APP,
        borderwidth=0,
        arrowsize=12
    )

    # Separator
    style.configure("TSeparator", background=COLOR_BORDER)


def setup_treeview_tags(tree):
    """Configures alternating row colors and status tag colors on a Treeview."""
    tree.tag_configure("odd", background=BG_SURFACE)
    tree.tag_configure("even", background=COLOR_ZEBRA)

    for status, color in STATUS_COLORS.items():
        tree.tag_configure(f"status_{status}", foreground=color)
