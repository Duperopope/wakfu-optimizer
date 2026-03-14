import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

# Ajouter la gestion CORS dans _json
old_json = 'def _json(self, data, code=200):'
new_json = '''def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _json(self, data, code=200):'''

c = c.replace(old_json, new_json)

# Ajouter _cors() dans _json apres send_response
old_send = 'self.send_header("Content-Type", "application/json")'
new_send = 'self._cors()\n            self.send_header("Content-Type", "application/json")'

c = c.replace(old_send, new_send)

f.write_text(c, 'utf-8')
print('CORS ajoute - dev_server.py:', f.stat().st_size, 'octets')
