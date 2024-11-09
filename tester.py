import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess
import sys
import os

# Database setup (SQLite)
def create_users_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Function to insert new user into the database
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)
        ''', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# Function to validate login credentials
def validate_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT password FROM users WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == password:
        return True
    return False

# Function for Tkinter login page
def show_login_page():
    def handle_login():
        username = entry_username.get()
        password = entry_password.get()

        if validate_login(username, password):
            messagebox.showinfo("Login Successful", "You have logged in successfully.")
            root.quit()  # Close Tkinter window

            # Launch Streamlit app (running it in a subprocess)
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "/Users/padhraigizediuno/HackathonGoldMan_Sachs/tester2.py"])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_register():
        username = entry_username.get()
        password = entry_password.get()

        # Basic check for empty fields
        if not username or not password:
            messagebox.showerror("Error", "Both fields are required.")
            return

        # Register the user in the database
        if register_user(username, password):
            messagebox.showinfo("Registration Successful", f"Account created for {username}. You can now log in.")
        else:
            messagebox.showerror("Registration Failed", "Username already exists. Please choose another username.")

    # Tkinter UI setup
    root = tk.Tk()
    root.title("Login")

    # Labels and Entry Widgets
    label_username = tk.Label(root, text="Username")
    label_username.grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(root)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    label_password = tk.Label(root, text="Password")
    label_password.grid(row=1, column=0, padx=10, pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    # Buttons
    login_button = tk.Button(root, text="Login", command=handle_login)
    login_button.grid(row=2, column=0, pady=10)

    register_button = tk.Button(root, text="Register", command=handle_register)
    register_button.grid(row=2, column=1, pady=10)

    root.mainloop()

# Create the users table if it doesn't exist
create_users_table()

# Function to run the Streamlit app
def run_streamlit():
    os.system('streamlit run financial_performance.py')

if __name__ == '__main__':
    show_login_page()
