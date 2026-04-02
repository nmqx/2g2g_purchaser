import tls_client
import re
import uuid
import json

UUID = str(uuid.uuid4())
USER_AGENT = "TGTG/26.3.20 Dalvik/2.1.0 (Linux; U; Android 9; SM-G988N Build/NRD90M)"

EMAIL = input("Enter your email address: ").strip()
print(f"\nUsing UUID: {UUID}")

session = tls_client.Session(
    client_identifier="okhttp4_android_9",
    random_tls_extension_order=True
)

anon1_headers = {
    "User-Agent": USER_AGENT,
    "Pragma": "no-cache",
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "Host": "api.toogoodtogo.com",
    "X-Correlation-ID": UUID
}
anon1_payload = {
    "uuid": UUID, "event_type": "BEFORE_COOKIE_CONSENT", 
    "country_code": "FR", "is_logged_in": False, "is_from_deeplink": False
}
res1 = session.post("https://api.toogoodtogo.com/api/tracking/v1/anonymousEvents", headers=anon1_headers, json=anon1_payload)
print(f"Status: {res1.status_code}")

session.cookies.clear()

dd_headers = {
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "api-sdk.datadome.co",
    "User-Agent": "okhttp/5.3.2"
}

dd_payload = "cid=DpmUhwAZvRiia3eh4qTRSGm2UYlEchrZfrV_1Qd4lYEO2AZ4XIilixoX1pDyaxxV2fsm9mQnD6akS1Bm6nzDJBAFdv8XRzjNKQ09WTkVjWwYlma7oVaye%7EDiKQX8GRS5&ddk=1D42C2CA6131C526E09F294FE96F94&request=https%3A%2F%2Fapi.toogoodtogo.com%2Fapi%2Ftracking%2Fv1%2FanonymousEvents&ua=TGTG%2F26.3.20+Dalvik%2F2.1.0+%28Linux%3B+U%3B+Android+9%3B+SM-G988N+Build%2FNRD90M%29&events=%5B%7B%22id%22%3A1%2C+%22message%22%3A%22response+validation%22%2C+%22source%22%3A%22sdk%22%2C+%22date%22%3A1775135415613%7D%5D&inte=android-java-okhttp&ddv=3.0.8&ddvc=26.3.20&os=Android&osr=9&osn=P&osv=28&screen_x=1080&screen_y=1920&screen_d=2.0&camera=%7B%22auth%22%3A%22false%22%2C+%22info%22%3A%22%7B%7D%22%7D&mdl=SM-G988N&prd=z3qksx&mnf=samsung&dev=z3q&hrd=exynos8895&fgp=samsung%2Fz3qksx%2Fz3q%3A9%2FNRD90M%2F901250224%3Auser%2Frelease-keys&tgs=release-keys&d_ifv=885427b715f1954e"

res_dd = session.post("https://api-sdk.datadome.co/sdk/", headers=dd_headers, data=dd_payload)
print(f"Status: {res_dd.status_code}")

dd_cookie_match = re.search(r'datadome=([^;]+)', res_dd.text)
dd_cookie_value = dd_cookie_match.group(1) if dd_cookie_match else ""
print(f"Extracted DD Cookie: {dd_cookie_value[:20]}...")

anon2_headers = {
    "Accept-Encoding": "gzip",
    "Accept-Language": "fr-FR",
    "Connection": "Keep-Alive",
    "Content-Type": "application/json; charset=utf-8",
    "Host": "api.toogoodtogo.com",
    "User-Agent": USER_AGENT,
    "Cookie": f"datadome={dd_cookie_value};",
    "X-Correlation-ID": UUID
}
anon2_payload = {
    "uuid": UUID, "event_type": "AFTER_COOKIE_CONSENT", 
    "country_code": "FR", "is_logged_in": False, "is_from_deeplink": False
}
res2 = session.post("https://api.toogoodtogo.com/api/tracking/v1/anonymousEvents", headers=anon2_headers, json=anon2_payload)
print(f"Status: {res2.status_code}")

session.cookies.clear()

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