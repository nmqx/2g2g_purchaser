import json
from getfirstdd import get_dd_cookie

def refresh_tokens():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json not found. You need to log in first.")
        return False

    print("refreshing tks....")

    session, UUID, dd_cookie_value, USER_AGENT = get_dd_cookie()

    print("GETTING NEW ATK FROM RTK")
    
    refresh_headers = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "api.toogoodtogo.com",
        "User-Agent": USER_AGENT,
        "Cookie": f"datadome={dd_cookie_value};",
        "X-Correlation-ID": UUID
    }

    refresh_payload = {
        "refresh_token": config["refresh_token"]
    }

    res_refresh = session.post("https://api.toogoodtogo.com/api/token/v1/refresh", headers=refresh_headers, json=refresh_payload)

    if res_refresh.status_code == 200:
        new_data = res_refresh.json()
        
        config["access_token"] = new_data["access_token"]
        config["refresh_token"] = new_data["refresh_token"]
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
        print("Tokens refreshed and saved to config.json!")
        return True
    else:
        print(f"Failed to refresh tokens. Status: {res_refresh.status_code}")
        print(res_refresh.text)

        return False

if __name__ == "__main__":
    refresh_tokens()