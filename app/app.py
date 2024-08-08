from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'habitos_ninos'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        if conn.is_connected():
            print("Conexión a la base de datos exitosa")
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Ruta de las plantillas
app.template_folder = os.path.join(os.getcwd(), 'templates')

# Preguntas del quiz
questions = [
    {
        "question": "¿Cómo se llama el lugar donde viven muchos animales y plantas?",
        "img": "images/pregunta1.png.png",
        "answers": ["Fábrica", "Bosque", "Oficina"],
        "correct": 1,
        "points": 50
    },
    {
        "question": "¿Por qué es importante apagar las luces cuando no las estamos usando?",
        "img": "images/pregunta2.png.png",
        "answers": ["Para ahorrar energía y cuidar el planeta", "Para que la casa esté más oscura", "Para que las luces no se rompan"],
        "correct": 0,
        "points": 50
    },
    {
        "question": "¿Qué es el calentamiento global?",
        "img": "images/pregunta3.png.png",
        "answers": ["Es cuando la temperatura de la Tierra disminuye debido a la lluvia y la nieve", "Es cuando la temperatura de la Tierra se mantiene igual y no cambia con el tiempo", "Es cuando la temperatura de la Tierra aumenta debido a la acumulación de gases de efecto invernadero en la atmósfera"],
        "correct": 2,
        "points": 100
    },
    {
        "question": "¿Qué es la atmósfera y cuál es su función?",
        "img": "images/pregunta4.png.png",
        "answers": ["Es una capa de gases que rodea la Tierra y su función es protegernos de los rayos del sol y mantener el calor del planeta.", "Es una capa de agua alrededor de la Tierra y su función es mantener el planeta húmedo", "Es una capa de rocas y minerales que cubre la superficie de la Tierra y su función es proporcionar suelo para las plantas"],
        "correct": 0,
        "points": 100
    },
    {
        "question": "¿Cuál de los siguientes animales se encuentran en peligro de extinción?",
        "img": "images/pregunta5.png.png",
        "answers": ["Tigre de Bengala, chimpancé, ajolote, mandril, Oso polar.", "Vaca, caballos, perro doméstico, gato doméstico y oso panda", "Todos los anteriores"],
        "correct": 0,
        "points": 100
    },
    {
        "question": "¿Sabes cuántos árboles deben ser talados para producir una tonelada de papel?",
        "img": "images/pregunta6.png.png",
        "answers": ["39 árboles", "150 árboles", "17 árboles"],
        "correct": 2,
        "points": 150
    },
    {
        "question": "¿Qué es la deforestación y cómo afecta a las personas y a los animales?",
        "img": "images/pregunta7.png.png",
        "answers": ["Es el crecimiento natural de los bosques que ayuda a aumentar la biodiversidad y proporciona recursos para las comunidades locales", "Es la quema controlada de bosques para crear nuevos espacios para la agricultura, lo que mejora la producción de alimentos", "Es la tala excesiva de árboles y afecta negativamente a las personas y animales al destruir sus hábitats y contribuir al cambio climático"],
        "correct": 2,
        "points": 150
    },
    {
        "question": "Este ecosistema se caracteriza por tener árboles altos y densos que forman un dosel cerrado, con una gran variedad de plantas, animales e insectos. Recibe mucha lluvia durante el año, y la humedad es alta. Alberga una biodiversidad increíble, incluyendo especies como jaguares, monos, ranas venenosas. ¿Qué ecosistema es?",
        "img": "images/pregunta8.png.png",
        "answers": ["Selva tropical", "Desierto", "Tundra"],
        "correct": 0,
        "points": 150
    },
    {
        "question": "¿Qué significa cada una de las tres R: Reducir, Reutilizar y Reciclar?",
        "img": "images/pregunta9.png.png",
        "answers": ["Reducir: Tirar menos basura a la calle. Reutilizar: Comprar productos nuevos. Reciclar: Separar la basura en diferentes contenedores.", "Reducir: Comprar más cosas nuevas. Reutilizar: Usar productos una sola vez. Reciclar: Quemar basura para deshacerse de ella.", "Reducir: Usar menos recursos y generar menos residuos desde el principio. Reutilizar: Usar objetos o materiales varias veces antes de desecharlos. Reciclar: Transformar materiales usados en nuevos productos."],
        "correct": 2,
        "points": 200
    },
    {
        "question": "En 1876 se creó la primera área protegida de México, con el propósito de preservar los manantiales que abastecían de agua a la Ciudad de México. ¿Cuál es esta área?",
        "img": "images/pregunta10.png.png",
        "answers": ["Desierto de los Leones", "Reserva de la Biósfera del Santuario de la Mariposa Monarca", "Reserva de la Biósfera de la Sierra Gorda"],
        "correct": 0,
        "points": 200
    }
]

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f'Intentando iniciar sesión para el usuario: {username}')

        conn = get_db_connection()
        if conn is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            print(f'Usuario encontrado: {user}')
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('index'))
            else:
                print('Contraseña incorrecta')
                flash('Nombre de usuario o contraseña incorrectos', 'danger')
        else:
            print('Usuario no encontrado')
            flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('register'))

        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                           (username, hashed_password, role))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error al registrar usuario: {err}', 'danger')
            print(f"Error al registrar usuario: {err}")
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Por favor inicia sesión primero', 'danger')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', role=session['role'])

@app.route('/actividades')
def actividades():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('actividades.html')

@app.route('/progreso')
def progreso():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('progreso.html')

@app.route('/configuracion')
def configuracion():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('configuracion.html')

@app.route('/quiz')
def quiz():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('quiz.html')

@app.route('/juego')
def juego():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('juego.html')

@app.route('/manualidades')
def manualidades():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('manualidades.html')

@app.route('/experimentos')
def experimentos():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('experimentos.html')

@app.route('/lectura1')
def lectura1():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('lectura1.html')

@app.route('/lectura2')
def lectura2():
     if 'username' not in session:
        return redirect(url_for('login'))
     return render_template('lectura2.html')

@app.route('/glosario')
def glosario():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('glosario.html')

@app.route('/referencias')
def referencias():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('referencias.html')

@app.route('/historias')
def historias():
    # Define las variables que pasarás a la plantilla
    lecturas = [
        {'title': 'Lectura 1', 'page_url': 'lectura1', 'page_text': 'Leer más sobre Lectura 1'},
        {'title': 'Lectura 2', 'page_url': 'lectura2', 'page_text': 'Leer más sobre Lectura 2'}
    ]
    glosario = {'page_url': 'glosario', 'page_text': 'Ir al glosario'}
    referencias = {'page_url': 'referencias', 'page_text': 'Ver referencias'}

    # Pasa las variables a la plantilla
    return render_template('historias.html', lecturas=lecturas, glosario=glosario, referencias=referencias)

@app.route('/logros')
def logros():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('logros.html')

@app.route('/estadisticas')
def estadisticas():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('estadisticas.html')

@app.route('/metas')
def metas():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('metas.html')

@app.route('/actividades_completadas')
def actividades_completadas():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('actividades_completadas.html')

@app.route('/ranking')
def ranking():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('ranking.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Cierre de sesión exitoso', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
