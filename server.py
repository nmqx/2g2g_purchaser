import http.server
import socketserver
import urllib.parse
import json
import tls_client
import webbrowser
import threading
import re

PORT = 3001
global_lat = "47.1064143"
global_lng = "-1.5318723"
global_session = tls_client.Session(client_identifier="chrome_130")

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            try:
                with open('frontend.js', 'r', encoding='utf-8') as f:
                    frontend_code = f.read()
            except FileNotFoundError:
                self.wfile.write(b"frontend.js not found ")
                return
            

            frontend_code = re.sub(r'import React.*?;', 'const { useState, useEffect, useMemo } = React;', frontend_code)
            frontend_code = frontend_code.replace('export default function OffersDashboard', 'function OffersDashboard')
            

            frontend_code = re.sub(r'lat=[\d\.\-]+&lng=[\d\.\-]+', f'lat={global_lat}&lng={global_lng}', frontend_code)
            
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>TooGoodToGo Offers</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
                <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
                <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
                <style>
                    body {{ background-color: #f9fafb; display: none; }}
                </style>
            </head>
            <body>
                <div id="root"></div>
                <script type="text/babel">
                    {frontend_code}
                    
                    const root = ReactDOM.createRoot(document.getElementById('root'));
                    root.render(<OffersDashboard />);
                    document.body.style.display = 'block';
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            
        elif parsed_path.path == '/calendar':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            try:
                with open('calendar_frontend.js', 'r', encoding='utf-8') as f:
                    cal_code = f.read()
            except FileNotFoundError:
                self.wfile.write(b"calendar_frontend.js not found")
                return
                
            html = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>TGTG Calendar Setup</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
                <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
                <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
            </head>
            <body>
                <div id="root"></div>
                <script type="text/babel">
{cal_code}
                </script>
            </body>
            </html>"""
            self.wfile.write(html.encode("utf-8"))
            
        elif parsed_path.path == '/api/get_calendar':
            import os
            query = dict(urllib.parse.parse_qsl(parsed_path.query))
            t = query.get('type', 'usual')
            
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    
            schedule = config.get(f"calendar_{t}", {})
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"schedule": schedule}).encode('utf-8'))
            
        elif parsed_path.path == '/api/tgtg':
            tgtg_url = f"https://www.toogoodtogo.com/api/surprise-bags/item-list?{parsed_path.query}"
            
            headers = {
                "accept": "*/*",
                "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "none",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            
            res = global_session.get(tgtg_url, headers=headers)
            
            self.send_response(res.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res.content)
        else:
           
            super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/save_calendar':
            import os
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    
            t = data.get("type", "usual")
            config[f"calendar_{t}"] = data.get("schedule", {})
            
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

def start_dashboard(lat, lng, port=3001, open_browser=True):
    global global_lat, global_lng, PORT
    global_lat = lat
    global_lng = lng
    PORT = port
    
    handler = RequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        httpd = socketserver.TCPServer(("", PORT), handler)
        print(f"Backend started at http://localhost:{PORT}")
        
        if open_browser:
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        
        print(f"Ctrl+C to stop.")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048: 
            print(f"Port {PORT} is already in use.")
            webbrowser.open(f"http://localhost:{PORT}")
        else:
            raise

def get_coordinates():
    print("TGTG Local Dashboard")
    b = input("Ta ville : ")
    a = input("Ton adresse (rue): ")

    c, d = a.replace(" ", "+"), b.replace(" ", "+")

    session = tls_client.Session(client_identifier="chrome_130")
    getcoord = session.get(f"https://api-adresse.data.gouv.fr/search/?q={c}+{d}")
    
    try:
        data = getcoord.json()
        coordinates = data["features"][0]["geometry"]["coordinates"]
        lat, lng = coordinates[1], coordinates[0]
        
        # Save to config.json
        try:
            import json, os
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
            config["latitude"] = lat
            config["longitude"] = lng
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass
            
        return lat, lng
    except Exception as e:
        print(f"Erreur lors de la recherche des coordonnées : {e}")
        print("Utilisation des coordonnées par défaut (Nantes)...")
        return 47.1064143, -1.5318723


if __name__ == "__main__":
    lat, lng = get_coordinates()
    start_dashboard(lat, lng)
