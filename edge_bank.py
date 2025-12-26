import pandas as pd
import hashlib
from datetime import datetime

# --- Security Utility ---


def hash_pin(pin):
    """Converts a plain-text PIN into a secure SHA-256 hash."""
    # hashlib requires bytes, so we convert the int to a string then encode it

    return hashlib.sha256(str(pin).encode()).hexdigest()


# --- Core Banking Functions ---

def register_user():
    """Handles new user registration and saves data securely to CSV."""
    try:
        # Load existing data or create new DataFrame with standard columns

        try:
            registration_df = pd.read_csv("registered_users.csv")
        except FileNotFoundError:
            columns = [
                "Name",
                "Date_of_birth",
                "Gender",
                "Address",
                "N I N / BVN",
                "Phone_number",
                "Email_address",
                "Account_Type",
                "PIN",
                "Security Question",
            ]
            registration_df = pd.DataFrame(columns=columns)
        # User Input Section

        key = input("Enter your name initials (e.g., DA)--> ").upper()
        name = input("Enter your full name --> ").title()

        dob_input = input("Enter your date of birth (DD/MM/YYYY): ")
        birthdate = datetime.strptime(dob_input, "%d/%m/%Y").date()

        gender = input("Enter your gender: ")
        address = input("Enter your home address: ")
        nin = int(input("Enter your National Identification Number: "))
        phone = input("Enter your 11-digit phone number: ")
        email = input("Enter your email address: ").strip().lower()
        acc_type = input("Enter S for Savings and C for Current: ").title()

        # SECURE: Hash the PIN before saving to the CSV

        raw_pin = int(input("Set your 4-digit PIN: "))
        hashed_pin = hash_pin(raw_pin)

        security_q = (
            input("Security Question: What is your mother's maiden name? ")
            .strip()
            .capitalize()
        )

        # Update the DataFrame

        registration_df.loc[key] = [
            name,
            birthdate,
            gender,
            address,
            nin,
            phone,
            email,
            acc_type,
            hashed_pin,
            security_q,
        ]

        # FIX: Save with index=False to prevent "Unnamed: 0" columns

        registration_df.to_csv("registered_users.csv", index=False)
        print(f"\n✅ User {name} registered successfully!")
    except Exception as e:
        print(f"\n❌ Registration failed: {e}")


def user_login():
    """Verifies user credentials and returns the email for the current session."""
    try:
        registration_df = pd.read_csv("registered_users.csv")
    except FileNotFoundError:
        print("\n❌ No registered users found yet! Please register first.")
        return None
    email = input("Enter your email address: ").strip().lower()
    try:
        raw_pin = int(input("Enter your 4-digit PIN: "))
        # Hash the input to compare it against the stored scrambled PIN

        hashed_input = hash_pin(raw_pin)
    except ValueError:
        print("\n❌ PIN must be a number!")
        return None
    # Check if the email exists and the hashed PIN matches

    condition = (registration_df["Email_address"] == email) & (
        registration_df["PIN"] == hashed_input
    )

    if condition.any():
        print("\n✅ Login Successful! Welcome back.")
        return email  # SESSION: Returns email so main.ipynb can track the user
    else:
        print("\n❌ Wrong email or PIN.")
        return None


def perform_transaction(user_email):
    """Processes deposits and withdrawals for the logged-in user."""
    try:
        # Load transaction history [cite: 2]

        try:
            df = pd.read_csv("transactions.csv")
        except FileNotFoundError:
            df = pd.DataFrame(
                columns=[
                    "user_email",
                    "transaction_type",
                    "amount",
                    "balance",
                    "t_time",
                ]
            )
        trans_type = input("Do you want to deposit or withdraw? ").strip().lower()
        amount = float(input("Enter Amount: "))
        now_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        # Calculate current balance from the last transaction record [cite: 2]

        user_data = df[df["user_email"] == user_email]
        last_balance = user_data.iloc[-1]["balance"] if not user_data.empty else 0

        if trans_type == "deposit":
            new_balance = last_balance + amount
        elif trans_type == "withdraw":
            if amount > last_balance:
                print("\n❌ Insufficient balance!")
                return
            new_balance = last_balance - amount
        else:
            print("\n❌ Invalid transaction type.")
            return
        # Create a new record as a DataFrame to append [cite: 2]

        new_record = pd.DataFrame(
            [
                {
                    "user_email": user_email,
                    "transaction_type": trans_type,
                    "amount": amount,
                    "balance": new_balance,
                    "t_time": now_time,
                }
            ]
        )

        # Append and save without indices [cite: 2]

        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv("transactions.csv", index=False)

        print(f"\n✅ Transaction recorded! Current balance: ₦{new_balance}")
    except Exception as e:
        print(f"\n❌ Transaction error: {e}")


def reset_pin():
    """Allows user to change PIN if they verify their security answer."""
    try:
        registration_df = pd.read_csv("registered_users.csv")
    except FileNotFoundError:
        print("\n❌ Database not found. Please register first.")
        return
    email = input("Enter your email address: ").strip().lower()
    security_answer = (
        input("Recovery Check: What is your mother's maiden name? ")
        .strip()
        .capitalize()
    )

    condition = (registration_df["Email_address"] == email) & (
        registration_df["Security Question"] == security_answer
    )

    if condition.any():
        try:
            new_pin = int(input("Verified! Enter your new 4-digit PIN: "))
            hashed_new_pin = hash_pin(new_pin)
            registration_df.loc[condition, "PIN"] = hashed_new_pin
            registration_df.to_csv("registered_users.csv", index=False)
            print("\n✅ PIN reset successfully!")
        except ValueError:
            print("\n❌ Invalid input! PIN must be a number.")
    else:
        print("\n❌ Incorrect email or security answer.")


def get_balance(user_email):
    """Retrieves the latest balance for a specific user from the transactions file."""
    try:
        # Load the transaction database 
        df = pd.read_csv("transactions.csv")
        # Filter rows to only show this user 
        user_data = df[df["user_email"] == user_email]
        
        if not user_data.empty:
            # Return the balance from the very last row for this user 
            return user_data.iloc[-1]["balance"]
        return 0
    except FileNotFoundError:
        # If the file doesn't exist yet, the balance is 0 
        return 0


def view_history(user_email):
    """Displays a filtered table of all actions taken by the logged-in user."""
    try:
        # Load the transaction database 
        df = pd.read_csv("transactions.csv")
        # Filter the DataFrame to only include this user's records 
        user_history = df[df["user_email"] == user_email]
        
        if user_history.empty:
            print("\nEmpty: You have no transaction records yet.")
        else:
            print(f"\n--- Transaction History for {user_email} ---")
            # Display only relevant columns for the user to see 
            # .tail(10) ensures they aren't overwhelmed by too much data 
            print(user_history[["t_time", "transaction_type", "amount", "balance"]].tail(10))
    except FileNotFoundError:
        print("\n❌ Error: No transaction records found.")       
        
           
def transfer_funds(sender_email):
    """Handles sending money between two registered users."""
    try:
        #  Load Data
        users_df = pd.read_csv("registered_users.csv")
        try:
            trans_df = pd.read_csv("transactions.csv")
        except FileNotFoundError:
            trans_df = pd.DataFrame(columns=["user_email", "transaction_type", "amount", "balance", "t_time"])

        #  Get Recipient and Amount
        recipient_email = input("Enter Recipient's Email: ").strip().lower()
        
        # Check if recipient exists
        if not (users_df["Email_address"] == recipient_email).any():
            print("❌ Recipient email not found in our system.")
            return

        if recipient_email == sender_email:
            print("❌ You cannot transfer money to yourself.")
            return

        amount = float(input(f"Enter amount to transfer to {recipient_email}: ₦"))
        
        if amount <= 0:
            print("❌ Invalid amount.")
            return

        #  Check Sender's Balance
        sender_data = trans_df[trans_df["user_email"] == sender_email]
        sender_balance = sender_data.iloc[-1]["balance"] if not sender_data.empty else 0

        if amount > sender_balance:
            print(f"❌ Insufficient funds. Your balance is ₦{sender_balance}")
            return

        #  Perform the Transfer (Double Entry)
        now_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        #  Update Sender Record
        new_sender_balance = sender_balance - amount
        sender_entry = pd.DataFrame([{
            "user_email": sender_email,
            "transaction_type": f"Transfer to {recipient_email}",
            "amount": amount,
            "balance": new_sender_balance,
            "t_time": now_time
        }])

        #  Update Recipient Record
        recipient_data = trans_df[trans_df["user_email"] == recipient_email]
        recipient_balance = recipient_data.iloc[-1]["balance"] if not recipient_data.empty else 0
        new_recipient_balance = recipient_balance + amount
        
        recipient_entry = pd.DataFrame([{
            "user_email": recipient_email,
            "transaction_type": f"Transfer from {sender_email}",
            "amount": amount,
            "balance": new_recipient_balance,
            "t_time": now_time
        }])

        # Save everything
        trans_df = pd.concat([trans_df, sender_entry, recipient_entry], ignore_index=True)
        trans_df.to_csv("transactions.csv", index=False)

        print(f"\n✅ Transfer Successful! ₦{amount} sent to {recipient_email}.")
        print(f"💰 Your new balance: ₦{new_sender_balance}")

    except ValueError:
        print("❌ Invalid input! Please enter a numerical amount.")
    except Exception as e:
        print(f"❌ Error during transfer: {e}")
