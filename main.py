import pandas as pd
import time
# from art import text2art  
# Import all your secured functions from edge_bank.py

from edge_bank import (
    register_user, 
    user_login, 
    perform_transaction, 
    transfer_funds, 
    reset_pin, 
    view_history, 
    get_balance
)

def transaction_menu(current_user):
    """
    This is the Sub-Menu that only logged-in users see.
    It keeps the user session active.
    """
    while True:
        print(f"\n--- 🏦 DOMICOCO BANK: Welcome, {current_user} ---")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Money (P2P)")
        print("5. View Transaction History")
        print("6. Logout")
        
        sub_choice = input("Select an option (1-6): ")
        
        if sub_choice == '1':
            balance = get_balance(current_user)
            print(f"\n💰 Your current balance is: ₦{balance:,.2f}")
            
        elif sub_choice == '2':
            # Logic for Deposit
            perform_transaction(current_user) 
            
        elif sub_choice == '3':
            # Logic for Withdraw
            perform_transaction(current_user) 
            
        elif sub_choice == '4':
            # The new Day 2 Inter-Account Transfer feature
            transfer_funds(current_user)
            
        elif sub_choice == '5':
            # Shows filtered history of the logged-in user
            view_history(current_user)
            
        elif sub_choice == '6':
            print(f"Logging out {current_user}... Have a great day!")
            break
        else:
            print("❌ Invalid selection. Please choose 1-6.")
        time.sleep(3)  # Pause before showing the transaction menu again
        
def main_menu():
    """
    Area for registration and login. This is the Main Menu that all users see.
    """
    while True:
        # Visual branding
        # ascii_art = text2art("DOMICOCO BANKING SYSTEM", font='mini')
        # print(ascii_art)
        print("=== Welcome to DOMICOCO MINI BANK ===")  
        print("1. Register New Account")
        print("2. Log In")
        print("3. Forgot PIN (Reset)")
        print("4. Exit")

        try:
            choice = int(input("Enter a choice--> "))

            if choice == 1:
                register_user()

            elif choice == 2:
                attempts = 0
                max_attempts = 3
                logged_in_user = None

                # 3-Strike Security Loop
                while attempts < max_attempts:
                    logged_in_user = user_login()

                    if logged_in_user:
                        # Success! Enter the secure Sub-Menu
                        transaction_menu(logged_in_user)
                        break  
                    else:
                        attempts += 1
                        remaining = max_attempts - attempts
                        if remaining > 0:
                            print(f"❌ Incorrect credentials. {remaining} attempts left.")
                
                # Strike 3 logic
                if not logged_in_user and attempts == max_attempts:
                    print("\n🔒 Account locked due to too many failed attempts.")
                    choice_reset = input("Would you like to reset your PIN using your security question? (Y/N): ").upper()
                    if choice_reset == "Y":
                        reset_pin()

            elif choice == 3:
                reset_pin()

            elif choice == 4:
                print("Thank you for banking with DOMICOCO. Goodbye!")
                break
            
            else:
                print("❌ Please enter a valid option (1-4).")

        except ValueError:
            print("❌ Invalid input! Please enter a number (1, 2, 3, or 4).")
        time.sleep(3) # Pause before showing the menu again
        

if __name__ == "__main__":
    main_menu()