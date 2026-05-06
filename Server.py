#!/usr/bin/env python3
import os
import json
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yt_dlp

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

progress_store = {}

def get_progress_hook(url_id):
    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            percent = int((downloaded / total) * 100) if total > 0 else 0
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            progress_store[url_id] = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta
            }
        elif d['status'] == 'finished':
            progress_store[url_id] = {'status': 'converting', 'percent': 99}
    return hook

def download_mp3(url, url_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'progress_hooks': [get_progress_hook(url_id)],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            progress_store[url_id]['title'] = title
            progress_store[url_id]['duration'] = duration
            progress_store[url_id]['thumbnail'] = thumbnail
            ydl.download([url])
        
        mp3_file = None
        for f in os.listdir(DOWNLOAD_DIR):
            if f.endswith('.mp3'):
                mp3_file = f
        
        progress_store[url_id] = {
            'status': 'done',
            'percent': 100,
            'filename': mp3_file,
            'title': title,
            'duration': duration,
            'thumbnail': thumbnail
        }
    except Exception as e:
        progress_store[url_id] = {'status': 'error', 'message': str(e)}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/download':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            url = body.get('url', '').strip()
            if not url:
                return self.send_json({'error': 'No URL provided'}, 400)
            
            import hashlib
            url_id = hashlib.md5(url.encode()).hexdigest()[:8]
            progress_store[url_id] = {'status': 'starting', 'percent': 0}
            thread = threading.Thread(target=download_mp3, args=(url, url_id), daemon=True)
            thread.start()
            self.send_json({'id': url_id})

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/progress':
            params = parse_qs(parsed.query)
            url_id = params.get('id', [''])[0]
            data = progress_store.get(url_id, {'status': 'not_found'})
            self.send_json(data)
        
        elif parsed.path == '/api/file':
            params = parse_qs(parsed.query)
            filename = params.get('name', [''])[0]
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.exists(filepath) and filename.endswith('.mp3'):
                with open(filepath, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', len(data))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_json({'error': 'File not found'}, 404)
        
        elif parsed.path == '/' or parsed.path == '/Test.html':
            filepath = os.path.join(os.path.dirname(__file__), 'Test.html')
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_json({'error': 'Not found'}, 404)

if __name__ == '__main__':
    port = 7860
    print(f"Server running at http://localhost:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()