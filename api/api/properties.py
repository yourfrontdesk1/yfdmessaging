import json
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler

SMOOBU_API_KEY = 'B1r7Y46f1A0oD88WM7H3t5YTybsCfUXecPMNiAhLvW'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key = self.headers.get('X-Api-Key', SMOOBU_API_KEY)
        
        try:
            url = "https://login.smoobu.com/api/apartments"
            req = urllib.request.Request(url, headers={'Api-Key': api_key, 'Content-Type': 'application/json'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            properties = []
            for apt in data.get('apartments', []):
                properties.append({
                    'id': str(apt.get('id')),
                    'name': apt.get('name', ''),
                    'address': apt.get('street', ''),
                    'city': apt.get('city', ''),
                    'country': apt.get('country', ''),
                    'rooms': apt.get('rooms', 0),
                    'max_guests': apt.get('maxOccupancy', 0)
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'properties': properties}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Api-Key')
        self.end_headers()
