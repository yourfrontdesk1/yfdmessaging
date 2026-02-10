import json
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler

SMOOBU_API_KEY = 'B1r7Y46f1A0oD88WM7H3t5YTybsCfUXecPMNiAhLvW'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        api_key = self.headers.get('X-Api-Key', SMOOBU_API_KEY)
        
        try:
            url = "https://login.smoobu.com/api/reservations?from=2025-01-01&to=2026-12-31"
            req = urllib.request.Request(url, headers={'Api-Key': api_key, 'Content-Type': 'application/json'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            conversations = []
            for b in data.get('bookings', []):
                msg_url = f"https://login.smoobu.com/api/reservations/{b.get('id')}/messages"
                msg_req = urllib.request.Request(msg_url, headers={'Api-Key': api_key})
                try:
                    with urllib.request.urlopen(msg_req, context=ctx, timeout=10) as msg_resp:
                        messages = json.loads(msg_resp.read().decode())
                    last_msg = messages[-1] if messages else {}
                    is_unanswered = last_msg.get('type') == 1 if last_msg else False
                except:
                    messages = []
                    is_unanswered = False
                
                conversations.append({
                    'id': str(b.get('id')),
                    'guest_name': f"{b.get('firstname', '')} {b.get('lastname', '')}".strip() or 'Guest',
                    'property_name': b.get('apartment', {}).get('name', 'Property'),
                    'checkin': b.get('arrival'),
                    'checkout': b.get('departure'),
                    'channel': b.get('channel', {}).get('name', 'Direct'),
                    'last_message': last_msg.get('message', '')[:50] if last_msg else '',
                    'is_unanswered': is_unanswered
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'conversations': conversations}).encode())
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
