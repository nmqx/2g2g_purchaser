import json
import sys
import time
from getfirstdd import get_dd_cookie

def scrape_item():
    print("===== TGTG Item Scraper =====")
    item_id = input("Enter Item ID: ").strip()
    if not item_id:
        print("Invalid ID.")
        return

    print("\n[+] Getting DataDome cookie and UUID...")
    session, UUID, dd_cookie_value, USER_AGENT = get_dd_cookie()

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception:
        print("[-] Error: config.json not found. Run Finder and Login first.")
        return
        
    tk = config.get("access_token")
    lat = config.get("latitude")
    lng = config.get("longitude")
    
    if not tk:
        print("[-] Error: access_token not found in config.json. Please Login first.")
        return
        
    if lat is None or lng is None:
        print("[-] Warning: latitude/longitude not found in config.json. Using fallback coordinates.")
        lat = 47.1064143
        lng = -1.5318723

    headers = {
        "Accept-Encoding": "gzip",
        "Accept-Language": "fr-FR",
        "Authorization": f"Bearer {tk}",
        "Connection": "Keep-Alive",
        "Content-Type": "application/json; charset=utf-8",
        "Cookie": f"datadome={dd_cookie_value};",
        "Host": "api.toogoodtogo.com",
        "User-Agent": USER_AGENT,
        "X-24HourFormat": "true",
        "X-Correlation-ID": UUID,
        "X-TimezoneOffset": "+02:00"
    }

    payload = {
        "origin": {
            "latitude": float(lat),
            "longitude": float(lng)
        }
    }
    
    url = f"https://api.toogoodtogo.com/api/item/v9/{item_id}"
    print(f"[+] Surveillance en cours pour l'Item ID: {item_id}")
    
    while True:
        res = session.post(url, json=payload, headers=headers)
        
        if res.status_code != 200:
            print(f"[!] Erreur HTTP {res.status_code}. Retry dans 30s...")
            time.sleep(30)
            continue
            
        try:
            data = res.json()
            items_available = data.get("items_available", 0)
            
            if items_available == 0:
                name = data.get("display_name", "L'item")
                print(f"[-] {time.strftime('%H:%M:%S')} | {name} n'est pas disponible (0). Attente 30 secondes...")
                time.sleep(30)
            else:
                qty = items_available
                name = data.get('display_name', 'Item')
                print(f"\n[✓] SUCCÈS ! {qty} panier(s) de '{name}' disponible(s) !!")
                
                # Check for discord webhook link in config
                webhook_url = config.get("webhook_url")
                if webhook_url:
                    import requests
                    try:
                        wh_data = {"content": f"🚨 **RESTOCK TOO GOOD TO GO** 🚨\n🛒 Il y a **{qty} panier(s)** disponible(s) chez **{name}** !"}
                        requests.post(webhook_url, json=wh_data, timeout=5)
                        print("[✓] Notification Discord envoyée avec succès !")
                    except Exception as e:
                        print(f"[x] Erreur lors de l'envoi de la notification Discord: {e}")
                        
                break
                
        except Exception:
            print(f"[!] Erreur d'analyse JSON (Status {res.status_code}). Retry 30s...")
            time.sleep(30)

if __name__ == "__main__":
    scrape_item()
