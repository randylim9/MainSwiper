import http.server
import socketserver
import json
import sqlite3
import hashlib
import secrets

PORT = 8000
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching for active development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/api/register':
            self.handle_register()
        elif self.path == '/api/login':
            self.handle_login()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_register(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                self.send_json_response(400, {"success": False, "message": "Username dan password diperlukan"})
                return

            username = username.strip()
            if len(username) < 3:
                self.send_json_response(400, {"success": False, "message": "Username minimal 3 karakter"})
                return
            if len(password) < 6:
                self.send_json_response(400, {"success": False, "message": "Password minimal 6 karakter"})
                return

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Check user exists
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                self.send_json_response(400, {"success": False, "message": "Username sudah terdaftar"})
                return
            
            salt = secrets.token_hex(16)
            password_hash = hash_password(password, salt)
            
            cursor.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)", 
                           (username, salt, password_hash))
            conn.commit()
            conn.close()
            
            self.send_json_response(200, {"success": True, "message": "Registrasi berhasil! Silakan login."})
            
        except Exception as e:
            self.send_json_response(500, {"success": False, "message": f"Terjadi kesalahan: {str(e)}"})

    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                self.send_json_response(400, {"success": False, "message": "Username dan password diperlukan"})
                return
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result is None:
                # Fake hashing delay to prevent timing attacks
                dummy_salt = secrets.token_hex(16)
                hash_password(password, dummy_salt)
                self.send_json_response(401, {"success": False, "message": "Username atau password salah"})
                return
            
            salt, stored_hash = result
            input_hash = hash_password(password, salt)
            
            if input_hash == stored_hash:
                self.send_json_response(200, {"success": True, "message": "Login berhasil!"})
            else:
                self.send_json_response(401, {"success": False, "message": "Username atau password salah"})
                
        except Exception as e:
            self.send_json_response(500, {"success": False, "message": f"Terjadi kesalahan: {str(e)}"})

    def send_json_response(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        response_bytes = json.dumps(payload).encode('utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

if __name__ == '__main__':
    init_db()
    print(f"Database {DB_NAME} diinisialisasi.")
    
    server_address = ('', PORT)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, AuthHandler) as httpd:
        print(f"Server berjalan secara lokal di: http://localhost:{PORT}")
        print("Buka browser dan buka http://localhost:8000/login.html")
        print("Tekan Ctrl+C untuk menghentikan server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
