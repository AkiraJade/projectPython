# Entry point for Computer & Laptop Repair Service System

import tkinter as tk
from tkinter import ttk
import storage
import gui.login as login_gui
import gui.dashboard as dashboard_gui


def main():
    # Initialize data folder and seed records
    storage.init_storage()

    root = tk.Tk()
    root.title("Computer & Laptop Repair Service System")

    # Set ttk theme to default standard theme
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    def open_dashboard(user):
        dashboard_gui.show_dashboard_window(root, user, on_logout=open_login)

    def open_login():
        login_gui.show_login_window(root, on_login_success=open_dashboard)

    # Start with login screen
    open_login()

    root.mainloop()


if __name__ == "__main__":
    main()
