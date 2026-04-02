import json
from getfirstdd import get_dd_cookie

session, UUID, dd_cookie_value, USER_AGENT = get_dd_cookie()

def get_access_token():
    try:

        with open('config.json', 'r') as f:

            config = json.load(f)
            

        access_token = config.get("access_token")
        
        if access_token:
            return access_token
        else:
            print("Access token not found in config.json")
            return None
            
    except FileNotFoundError:
        print("config.json file does not exist yet. Please log in first fr")
        return None


my_token = get_access_token()

if my_token:
    print(f"Successfully loaded token: {my_token[:15]}...")
    

getpm_headers = {
    "Accept-Encoding": "gzip",
    "Authorization": f"Bearer {my_token}",
    "Accept-Language": "fr-FR",
    "Connection": "Keep-Alive",
    "Content-Type": "application/json; charset=utf-8",
    "Cookie": f"datadome={dd_cookie_value};",
    "Host": "api.toogoodtogo.com",
    "User-Agent": USER_AGENT,
    "X-Correlation-ID": UUID
}

r6pl = {
  "supported_types": [
    {
      "provider": "ADYEN",
      "payment_types": [
        "CREDITCARD",
        "SOFORT",
        "IDEAL",
        "PAYPAL",
        "BCMCMOBILE",
        "BCMCCARD",
        "VIPPS",
        "TWINT",
        "MBWAY",
        "BLIK",
        "CASH_APP_PAY",
        "GOOGLEPAY"
      ]
    },
    {
      "provider": "VOUCHER",
      "payment_types": [
        "VOUCHER",
        "FAKE_DOOR"
      ]
    },
    {
      "provider": "CHARITY",
      "payment_types": [
        "CHARITY"
      ]
    },
    {
      "provider": "SATISPAY",
      "payment_types": [
        "SATISPAY"
      ]
    },
    {
      "provider": "EDENRED",
      "payment_types": [
        "EDENRED"
      ]
    }
  ]
}
r6 = session.post("https://api.toogoodtogo.com/api/paymentMethod/v2/item/163201674422169728", headers=getpm_headers, json=r6pl)
print(r6.text)