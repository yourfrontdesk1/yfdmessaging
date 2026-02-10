s.get('X-Api-Key', SMOOBU_API_KEY)
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            url = f"https://login.smoobu.com/api/reservations?from={today[:8]}01&to={today}"
            req = urllib.request.Request(url, headers={'Api-Key': api_key, 'Content-Type': 'application/json'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            bookings = data.get('bookings', [])
            revenue = sum(float(b.get('price', 0)) for b in bookings)
            checkins = sum(1 for b in bookings if b.get('arrival') == today)
            checkouts = sum(1 for b in bookings if b.get('departure') == today)
            active = sum(1 for b in bookings if b.get('arrival', '') <= today <= b.get('departure', ''))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'month_revenue': revenue,
                'today_checkins': checkins,
                'today_checkouts': checkouts,
                'active_stays': active,
                'total_bookings': len(bookings)
            }).encode())
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
