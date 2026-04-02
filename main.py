import threading
import sys
import time
import os
import json
import subprocess

def mode_finder():
    import server
    print("\nStarting Finder...")
    lat, lng = server.get_coordinates()
    
    server_thread = threading.Thread(target=server.start_dashboard, args=(lat, lng), daemon=True)
    server_thread.start()
    
    time.sleep(1.5)
    print("Server running in background.")

def mode_autobuy():
    print("\nMode Autobuy: Coming soon...")

def mode_notification():
    print("\nMode Notification: Coming soon...")

def mode_account_login():
    print("\nStarting Account Login...")
    subprocess.run([sys.executable, "login.py"])
    print("Login process finished.")

def mode_settings():
    print("\nSettings Mode")
    
    has_token = False
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                if config.get("access_token") and len(config.get("access_token")) > 10:
                    has_token = True
        except Exception:
            pass
            
    if not has_token:
        print("Error: No access_token found in config.json. Please login first.")
        return
        
    
    
    result = subprocess.run([sys.executable, "getpm.py"], capture_output=True, text=True)
    out_lower = result.stdout.lower()
    
    if "401" in out_lower or "unauthorized" in out_lower or "invalid_token" in out_lower:
        print("Error: Unauthorized (401). Token expired. ")
        return

    try:
        json_str = result.stdout[result.stdout.find('{'):]
        data = json.loads(json_str)
        
        methods = data.get("payment_methods", [])
        saved_cards = [m for m in methods if m.get("type") == "adyenSavedPaymentMethod" or m.get("identifier")]
        
        if not saved_cards:
            print("No saved cards found.")
        
        for i, card in enumerate(saved_cards, 1):
            brand = card.get("brand", card.get("payment_type", "Unknown"))
            display = card.get("display_value", "****")
            status = card.get("status", "ACTIVE")
            identifier = card.get("identifier", card.get("id", ""))
            
            expiry_str = ""
            payload_str = card.get("adyen_api_payload")
            if payload_str:
                try:
                    payload = json.loads(payload_str)
                    if "expiryMonth" in payload and "expiryYear" in payload:
                        expiry_str = f"| Exp: {payload['expiryMonth']}/{payload['expiryYear']} "
                    if "holderName" in payload:
                        expiry_str += f"| Name: {payload['holderName']} "
                except:
                    pass
                    
            print(f"[{i}] {brand} {display} {expiry_str}| Status: {status} | ID: {identifier}")
        
    except Exception as e:
        print(f"Error parsing data: {e}")
        print("Raw output:")
        print(result.stdout)

def main_menu():
    while True:
        print("\n" + "="*45)
        print("         2Good2Go / Bot by Nmqx      ")
        print("="*45)
        print(" 1. Mode Finder (Dashboard Interface)")
        print(" 2. Mode Autobuy")
        print(" 3. Mode Notification")
        print(" 4. Account Login")
        print(" 5. Settings (Vérification carte & tokens)")
        print(" 6. Quitter")
        print("="*45)
        
        choix = input("\nChoisissez une option (1-6): ").strip()
        
        if choix == '1':
            mode_finder()
        elif choix == '2':
            mode_autobuy()
        elif choix == '3':
            mode_notification()
        elif choix == '4':
            mode_account_login()
        elif choix == '5':
            mode_settings()
        elif choix == '6':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
