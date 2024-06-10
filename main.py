'''   
 Створіть веб-додаток з маршрутизацією для двох html сторінок: index.html та message.html.
Також:
Обробіть під час роботи програми статичні ресурси: style.css, logo.png;
Організуйте роботу з формою на сторінці message.html;
У разі виникнення помилки 404 Not Found повертайте сторінку error.html
''' 
import os
import json
import socket
import threading
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, abort

app = Flask(__name__)

# Конфігурація
HTTP_PORT = 3000
SOCKET_PORT = 5000
STORAGE_DIR = 'storage'
DATA_FILE = os.path.join(STORAGE_DIR, 'data.json')

# Перевірка наявності директорії storage
os.makedirs(STORAGE_DIR, exist_ok=True)

# Ініціалізація файлу data.json
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Маршрутизація
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        data = json.dumps({'username': username, 'message': message})
        
        # Відправка даних на socket сервер
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), ('127.0.0.1', SOCKET_PORT))
        
        return "Message sent!"
    
    return render_template('message.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Socket сервер для обробки повідомлень
def socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', SOCKET_PORT))
    
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        timestamp = datetime.now().isoformat()
        
        # Запис повідомлення у файл data.json
        with open(DATA_FILE, 'r+') as f:
            current_data = json.load(f)
            current_data[timestamp] = message
            f.seek(0)
            json.dump(current_data, f, indent=4)

# Запуск HTTP сервера і Socket сервера у різних потоках
if __name__ == '__main__':
    threading.Thread(target=socket_server, daemon=True).start()
    app.run(port=HTTP_PORT, debug=True)

'''
Для реалізації цього завдання створено найпростіший веб-додаток на Flask та Socket сервер. Весь код знаходиться в цьому одному файлі main.py.
Цей код створює простий веб-додаток, що містить дві сторінки (index та message), обробляє статичні файли, працює з формою і передає дані на Socket сервер, який зберігає ці дані у файл data.json.
'''

