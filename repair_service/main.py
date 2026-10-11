# Entry point for Computer & Laptop Repair Service System

import tkinter as tk
import storage
import gui.login as login_gui
import gui.dashboard as dashboard_gui
import gui.theme as theme


def main():
    # Enable crisp rendering on Windows
    theme.enable_dpi_awareness()

    # Initialize data folder and seed records
    storage.init_storage()

    root = tk.Tk()
    root.title("Computer & Laptop Repair Service System")

    # Apply global modern light dashboard theme
    theme.apply_theme(root)

    def open_dashboard(user):
        dashboard_gui.show_dashboard_window(root, user, on_logout=open_login)

    def open_login():
        login_gui.show_login_window(root, on_login_success=open_dashboard)

    # Start with login screen
    open_login()

    root.mainloop()


if __name__ == "__main__":
    main()
