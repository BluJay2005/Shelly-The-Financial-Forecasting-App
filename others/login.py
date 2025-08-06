import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess
import sys
import os
from PIL import Image, ImageTk  # To handle images in more formats

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
    
    # Set the background color of the root window to lightGray
    root.configure(bg="lightGray")
    
    # Set the window size and center it
    root.geometry("400x300")
    root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
    root.resizable(False, False)

    # Title label for the login page (Centered)
    label = tk.Label(root, text="Shell", font=('Comic Sans MS', 28,'bold'), bg="lightGray")
    label.grid(row=0, column=0, columnspan=2, pady=20)

    # Load and add image to the right of the label
    img = Image.open("a-turtle-shell-icon-for-an-app-make-it-green.png")  # Provide the correct image path
    img = img.resize((50, 50))  # Resize the image if necessary
    img_tk = ImageTk.PhotoImage(img)

    image_label = tk.Label(root, image=img_tk, bg="lightGray")
    image_label.grid(row=0, column=2, padx=10)  # Place the image to the right of the label

    # Labels and Entry Widgets with white background
    label_username = tk.Label(root, text="Username", bg="lightgray", font=('Courier', 18, "bold"), fg="black")
    label_username.grid(row=1, column=0, padx=10, pady=10, sticky="e")  # Align label to the right
    entry_username = tk.Entry(root, font=('Arial', 12), bg='white', fg='black')
    entry_username.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Expand horizontally

    label_password = tk.Label(root, text="Password", bg="lightgray", font=('Courier', 18, "bold"), fg="black")
    label_password.grid(row=2, column=0, padx=10, pady=10, sticky="e")  # Align label to the right
    entry_password = tk.Entry(root, show="*", font=('Arial', 12))
    entry_password.grid(row=2, column=1, padx=10, pady=10, sticky="ew")  # Expand horizontally

    # Buttons (Center aligned)
    login_button = tk.Button(root, text="Login", command=handle_login, bg="lightgray", font=('Courier', 14))
    login_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")  # Center button (spans two columns)

    register_button = tk.Button(root, text="Register", command=handle_register, bg="lightgray", font=('Courier', 14))
    register_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")  # Center button (spans two columns)

    # Configure row and column weights to allow centering
    root.grid_rowconfigure(0, weight=0)  # Title row should not expand
    root.grid_rowconfigure(1, weight=1)  # Username row expands
    root.grid_rowconfigure(2, weight=1)  # Password row expands
    root.grid_rowconfigure(3, weight=0)  # Button row should not expand
    root.grid_rowconfigure(4, weight=0)  # Button row should not expand

    root.grid_columnconfigure(0, weight=1)  # First column expands
    root.grid_columnconfigure(1, weight=2)  # Second column expands more
    root.grid_columnconfigure(2, weight=0)  # Third column for the image does not expand

    root.mainloop()

# Create the users table if it doesn't exist
create_users_table()

# Function to run the Streamlit app
def run_streamlit():
    os.system('streamlit run financial_performance.py')

if __name__ == '__main__':
    show_login_page()
