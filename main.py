import cv2
import numpy as np
import face_recognition
import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Balapavi03",
    database="bank"
)
cursor = db.cursor()

# Ensure tables are created correctly
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    dob DATE,
    address TEXT,
    phone VARCHAR(20),
    face_encoding LONGTEXT,
    account_number VARCHAR(20),
    balance FLOAT
)
""")

def capture_face():
    """Captures face from the webcam and returns the face encoding and the image."""
    cap = cv2.VideoCapture(0)
    success, image = cap.read()
    if not success:
        print("Failed to capture image")
        return None, None
    cap.release()

    # Show the captured image
    cv2.imshow("Captured Face", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    if face_encodings:
        return face_encodings[0], image
    else:
        return None, None

def gui_input(prompt):
    """Function to create input dialog using tkinter."""
    root = tk.Tk()
    root.withdraw()  # Hides the main window
    user_input = simpledialog.askstring("Input", prompt)
    root.destroy()
    return user_input

def gui_message(info):
    """Function to create message dialog using tkinter."""
    root = tk.Tk()
    root.withdraw()  # Hides the main window
    messagebox.showinfo("Information", info)
    root.destroy()

def loan_options():
    """Creates a new tkinter window with buttons for each loan type."""
    loan_window = tk.Tk()
    loan_window.title("Loan Options")

    def house_loan():
        gui_message("You selected House Loan. Please contact this mailid for further process rsssbank@gmail.com.")

    def vehicle_loan():
        gui_message("You selected Vehicle Loan. Please contact this mailid for further process rsssbank@gmail.com.")

    def education_loan():
        gui_message("You selected Education Loan. Please contact this mailid for further process rsssbank@gmail.com.")

    house_loan_button = tk.Button(loan_window, text="House Loan", command=house_loan)
    vehicle_loan_button = tk.Button(loan_window, text="Vehicle Loan", command=vehicle_loan)
    education_loan_button = tk.Button(loan_window, text="Education Loan", command=education_loan)

    house_loan_button.pack()
    vehicle_loan_button.pack()
    education_loan_button.pack()

    loan_window.mainloop()

def create_window(account_number):
    """Creates a new tkinter window with buttons for each action."""
    window = tk.Tk()
    window.title("Banking Operations")

    def deposit():
        amount = float(gui_input("Enter amount to be Deposited: "))
        cursor.execute("UPDATE customers SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
        db.commit()
        gui_message(f"Amount Deposited: {amount}")

    def withdraw():
        amount = float(gui_input("Enter amount to be Withdrawn: "))
        cursor.execute("SELECT balance FROM customers WHERE account_number = %s", (account_number,))
        balance = cursor.fetchone()[0]
        if balance >= amount:
            cursor.execute("UPDATE customers SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
            db.commit()
            gui_message(f"You Withdrew: {amount}")
        else:
            gui_message("Insufficient balance")

    def check_balance():
        cursor.execute("SELECT balance FROM customers WHERE account_number = %s", (account_number,))
        balance = cursor.fetchone()[0]
        gui_message(f"Net Available Balance: {balance}")

    deposit_button = tk.Button(window, text="Deposit", command=deposit)
    withdraw_button = tk.Button(window, text="Withdraw", command=withdraw)
    balance_button = tk.Button(window, text="Check Balance", command=check_balance)
    loan_button = tk.Button(window, text="Loan", command=loan_options)
    exit_button = tk.Button(window, text="Exit", command=window.destroy)

    deposit_button.pack()
    withdraw_button.pack()
    balance_button.pack()
    loan_button.pack()
    exit_button.pack()

    window.mainloop()

def register_new_customer():
    """Registers a new customer and captures their face using GUI for input and output."""
    name = gui_input("Enter your name:")
    age = gui_input("Enter your age:")
    gender = gui_input("Enter your gender (Male/Female/Other):")
    dob = gui_input("Enter your date of birth (YYYY-MM-DD):")
    address = gui_input("Enter your address:")
    phone = gui_input("Enter your phone number:")

    face_encoding, image = capture_face()
    if face_encoding is None:
        gui_message("No face detected. Try again.")
        return

    face_encoding_str = ','.join(map(str, face_encoding))
    account_number = f"AC{int(datetime.now().timestamp())}"

    cursor.execute("""
    INSERT INTO customers (name, age, gender, dob, address, phone, face_encoding, account_number, balance)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, age, gender, dob, address, phone, face_encoding_str, account_number, 0))
    db.commit()

    gui_message(f"Account created successfully. Your account number is: {account_number}\nName: {name}\nAge: {age}\nGender: {gender}\nDOB: {dob}\nAddress: {address}\nPhone: {phone}")

def recognize_customer():
    """Recognizes an existing customer from the webcam."""
    face_encoding, image = capture_face()
    if face_encoding is None:
        gui_message("No face detected.")
        return

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()  # Fetch all results before moving on
    for (id, name, age, gender, dob, address, phone, db_face_encoding, account_number, balance) in customers:
        try:
            db_face_encoding = np.fromstring(db_face_encoding, sep=',')
            if db_face_encoding.shape[0] != 128:
                raise ValueError("Invalid face encoding shape.")
            matches = face_recognition.compare_faces([db_face_encoding], face_encoding)
            if True in matches:
                gui_message(f"Welcome back, {name}! Age is {age}. And your account number is {account_number}.")
                create_window(account_number)
                return
        except Exception as e:
            print(f"Error processing customer {name} with account number {account_number}: {e}")

    gui_message("You are a new customer. Please register.")
    register_new_customer()

if __name__ == "__main__":
    recognize_customer()
