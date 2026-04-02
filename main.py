import threading
import sys
import time
import os
import json
import subprocess

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def mode_finder():
    import server
    print("\nStarting Finder...")
    
    lat = None
    lng = None
    conf = load_config()
    lat = conf.get("latitude")
    lng = conf.get("longitude")
            
    if not lat or not lng:
        print("Coordonnées introuvables. Lancement du mode Set Address...")
        lat, lng = mode_set_address()
        if not lat:
            return
            
    print(f"Loaded coordinates: {lat}, {lng}")
    server_thread = threading.Thread(target=server.start_dashboard, args=(lat, lng), daemon=True)
    server_thread.start()
    
    time.sleep(1.5)
    print("Server running in background.")

def mode_autobuy():
    print("\nMode Autobuy: Coming soon...")

def mode_notification():
    print("\n--- Mode Notification (Scraper) ---")
    
    config = load_config()
    wh_url = config.get("webhook_url")
    if not wh_url or len(wh_url) < 10:
        print("[!] Error: No Discord Webhook configured!")
        print("[!] Please go to 'Settings Menu' (5) -> 'Webhook Setup' (1) to add it first.\n")
        return
        
    subprocess.run([sys.executable, "scraper.py"])
    print("--- Fin du Mode Notification ---\n")

def mode_set_address():
    import tls_client
    print("\n--- Set Address ---")
    b = input("Ta ville : ").strip()
    a = input("Ton adresse (rue): ").strip()

    c, d = a.replace(" ", "+"), b.replace(" ", "+")
    session = tls_client.Session(client_identifier="chrome_130")
    print("Recherche des coordonnées géographiques...")
    
    try:
        getcoord = session.get(f"https://api-adresse.data.gouv.fr/search/?q={c}+{d}")
        data = getcoord.json()
        
        if not data.get("features"):
            print("[-] Erreur : Adresse introuvable.")
            return None, None
            
        coordinates = data["features"][0]["geometry"]["coordinates"]
        lat, lng = coordinates[1], coordinates[0]
        
        config = load_config()
        config["latitude"] = lat
        config["longitude"] = lng
        config["address"] = f"{a}, {b}"
        save_config(config)
            
        print(f"Localisation {lat}, {lng} sauvegardée avec succès !")
        return lat, lng
    except Exception as e:
        print(f"Erreur de recherche: {e}")
        return None, None

def mode_set_webhook():
    print("\nConfigurer Discord Webhook")
    wh_url = input("Entrez votre URL de webhook Discord (ou laissez vide pour annuler): ").strip()
    if not wh_url:
        print("Annulé.")
        return
        
    config = load_config()
    config["webhook_url"] = wh_url
    save_config(config)
    print("Webhook Discord sauvegardé avec succès dans config.json !")

def mode_check_payment_method():
    print("\nVérification des cartes de paiement")
    
    config = load_config()
    has_token = bool(config.get("access_token") and len(config.get("access_token")) > 10)
            
    if not has_token:
        print("Error: No access_token found in config.json. Please login first.")
        return
        
    print("Checking token via getpm.py...\n")
    
    result = subprocess.run([sys.executable, "getpm.py"], capture_output=True, text=True)
    out_lower = result.stdout.lower()
    
    if "401" in out_lower or "unauthorized" in out_lower or "invalid_token" in out_lower:
        print("Error: Unauthorized (401). Token expired. Please login again.")
        return

    try:
        json_str = result.stdout[result.stdout.find('{'):]
        data = json.loads(json_str)
        
        methods = data.get("payment_methods", [])
        saved_cards = [m for m in methods if m.get("type") == "adyenSavedPaymentMethod" or m.get("identifier")]
        
        if not saved_cards:
            print("No saved cards found.")
        else:
            print("=== Cartes de paiement enregistrées ===")
        
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

def mode_account_login():
    print("\nStarting Account Login...")
    subprocess.run([sys.executable, "login.py"])
    print("Login process finished.")

def settings_menu():
    while True:
        print("\n" + "-"*35)
        print("          SETTINGS MENU          ")
        print("-"*35)
        print(" 1. Webhook Setup")
        print(" 2. Location Setup (Set Address)")
        print(" 3. Check Payment Methods")
        print(" 4. Retour au Menu Principal")
        print("-"*35)
        
        choix = input("\nChoisissez une option (1-4): ").strip()
        
        if choix == '1':
            mode_set_webhook()
        elif choix == '2':
            mode_set_address()
        elif choix == '3':
            mode_check_payment_method()
        elif choix == '4':
            break
        else:
            print("Invalid choice.")

def main_menu():
    while True:
        print("\n" + "="*45)
        print("         2Good2Go / Bot by Nmqx      ")
        print("="*45)
        print(" 1. Mode Finder (Dashboard Interface)")
        print(" 2. Mode Autobuy")
        print(" 3. Mode Notification (Poll & Webhook)")
        print(" 4. Account Login")
        print(" 5. Settings Menu")
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
            settings_menu()
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
