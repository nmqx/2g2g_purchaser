import json
from getfirstdd import get_dd_cookie

EMAIL = input("Enter your email address: ").strip()

session, UUID, dd_cookie_value, USER_AGENT = get_dd_cookie()
print(f"\nUsing UUID: {UUID}")

auth_headers = {
    "Accept-Encoding": "gzip",
    "Accept-Language": "fr-FR",
    "Connection": "Keep-Alive",
    "Content-Type": "application/json; charset=utf-8",
    "Cookie": f"datadome={dd_cookie_value};",
    "Host": "api.toogoodtogo.com",
    "User-Agent": USER_AGENT,
    "X-Correlation-ID": UUID
}
auth_payload = {"device_type": "IOS", "email": EMAIL}
res3 = session.post("https://api.toogoodtogo.com/api/auth/v5/authByEmail", headers=auth_headers, json=auth_payload)
print(f"Status: {res3.status_code}")

try:
    res3_data = res3.json()
    print(f"Response: {res3_data}")
    
    if res3_data.get("state") == "WAIT":
        polling_id = res3_data.get("polling_id")
        
        PIN = input("\nEnter the PIN code here: ").strip()
        
        pin_payload = {
            "device_type": "IOS",
            "email": EMAIL,
            "request_pin": PIN,
            "request_polling_id": polling_id
        }
        
        res4 = session.post("https://api.toogoodtogo.com/api/auth/v5/authByRequestPin", headers=auth_headers, json=pin_payload)
        
        print(f"Status: {res4.status_code}")
        
        try:
            final_data = res4.json()
            if "access_token" in final_data:
                print("\nLogged in")
                print(f"Access Token: {final_data['access_token'][:30]}...")
                print(f"Refresh Token: {final_data['refresh_token'][:30]}...")
                config_data = {
                    "access_token": final_data["access_token"],
                    "refresh_token": final_data["refresh_token"],
                }
                with open('config.json', 'w') as f:
                    json.dump(config_data, f, indent=4)
                    
                print("Tokens saved to config.json")
            else:
                print("\nError uknown: Server response:")
                print(final_data)
        except json.JSONDecodeError:
            print("\nFailed to parse tk")
            print(res4.text)
            
    else:
        print("Did not receive 'WAIT' state. Cannot proceed to PIN verification.")
except json.JSONDecodeError:
    print("Failed to parse Auth response as JSON.")
    print(res3.text)