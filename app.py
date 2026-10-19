from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurar carpeta de subida de imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect('database.db')
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
    conn.commit()
    conn.close()

init_db()

# Ruta Principal (Catálogo protegido contra errores)
@app.route('/')
def index():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos ORDER BY id DESC')
        productos = cursor.fetchall()
        conn.close()
        return render_template('index.html', productos=productos)
    except Exception:
        return render_template('index.html', productos=[])

# Ruta del Panel Admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        calidad = request.form.get('calidad', '')
        genero = request.form.get('genero', '')
        precio = float(request.form.get('precio', 0))
        tallas = request.form.get('tallas', '')
        
        file = request.files.get('imagen')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            imagen_db = f'uploads/{filename}'
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productos (nombre, calidad, genero, precio, tallas, imagen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, calidad, genero, precio, tallas, imagen_db))
            conn.commit()
            conn.close()
            
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos ORDER BY id DESC')
    productos = cursor.fetchall()
    conn.close()
    return render_template('admin.html', productos=productos)

# Ruta para eliminar producto
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)