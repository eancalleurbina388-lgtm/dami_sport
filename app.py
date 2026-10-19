from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dami_sport_secreto_seguro_2026'

# CONTRASEÑA DE ADMINISTRADOR (Puedes cambiarla aquí cuando quieras)
ADMIN_PASSWORD = "admin123"

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(app.root_path, 'database.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            calidad TEXT NOT NULL,
            genero TEXT NOT NULL,
            precio REAL NOT NULL,
            tallas TEXT NOT NULL,
            imagen TEXT NOT NULL
        )
    ''')
    cursor.execute("PRAGMA table_info(productos)")
    columnas = [column[1] for column in cursor.fetchall()]
    if 'marca' not in columnas:
        cursor.execute("ALTER TABLE productos ADD COLUMN marca TEXT DEFAULT 'Punto Original'")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, nombre, calidad, genero, precio, tallas, imagen FROM productos ORDER BY id DESC')
        productos = cursor.fetchall()
        conn.close()
        return render_template('index.html', productos=productos)
    except Exception:
        return render_template('index.html', productos=[])

# Ruta del Panel Admin con Contraseña
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Si intenta iniciar sesión
    if request.method == 'POST' and 'password' in request.form:
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Contraseña incorrecta. Inténtalo de nuevo.")

    # Si no ha iniciado sesión, mostrar pantalla de login
    if not session.get('admin_logged'):
        return render_template('login.html')

    # Si es POST para agregar producto
    if request.method == 'POST':
        marca = request.form.get('marca', 'Punto Original').strip()
        nombre = request.form.get('nombre', '').strip()
        calidad = request.form.get('calidad', '').strip()
        genero = request.form.get('genero', '').strip()
        precio = float(request.form.get('precio', 0))
        tallas = request.form.get('tallas', '').strip()
        
        file = request.files.get('imagen')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            imagen_db = f'uploads/{filename}'
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productos (marca, nombre, calidad, genero, precio, tallas, imagen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (marca, nombre, calidad, genero, precio, tallas, imagen_db))
            conn.commit()
            conn.close()
            
        return redirect(url_for('admin'))

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, nombre, calidad, genero, precio, tallas, imagen FROM productos ORDER BY id DESC')
        productos = cursor.fetchall()
        conn.close()
    except Exception:
        productos = []

    return render_template('admin.html', productos=productos)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('admin_logged', None)
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    except Exception:
        pass
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)