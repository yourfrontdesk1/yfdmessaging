import json
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime

SMOOBU_API_KEY = 'B1r7Y46f1A0oD88WM7H3t5YTybsCfUXecPMNiAhLvW'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key = self.headers.get('X-Api-Key', SMOOBU_API_KEY)
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            url = f"https://login.smoobu.com/api/reservations?from={today}&to=2026-12-31"
            req = urllib.request.Request(url, headers={'Api-Key': api_key, 'Content-Type': 'application/json'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            bookings = []
            for b in data.get('bookings', []):
                bookings.append({
                    'id': b.get('id'),
                    'guest_name': f"{b.get('firstname', '')} {b.get('lastname', '')}".strip() or 'Guest',
                    'checkin': b.get('arrival'),
                    'checkout': b.get('departure'),
                    'property': b.get('apartment', {}).get('name', 'Property'),
                    'channel': b.get('channel', {}).get('name', 'Direct'),
                    'price': b.get('price', 0)
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'bookings': bookings}).encode())
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
