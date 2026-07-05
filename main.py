# Importación
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
# Conexión de la biblioteca de bases de datos
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
# Establecer la clave secreta para la sesión.
app.secret_key = 'my_top_secret_123'
# Estableciendo conexión SQLite
db_url = os.environ.get('DATABASE_URL')

# Corregimos el prefijo si viene como postgres:// en vez de postgresql://
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creando la DB
db = SQLAlchemy(app)
# Creando la tabla

class Card(db.Model):
    # Estableciendo los campos de enrada
    # id
    id = db.Column(db.Integer, primary_key=True)
    # título
    title = db.Column(db.String(100), nullable=False)
    # Descripción
    subtitle = db.Column(db.String(300), nullable=False)
    # Texto
    text = db.Column(db.Text, nullable=False)
    # El correo electrónico del propietario de la tarjeta.
    user_email = db.Column(db.String(100), nullable=False)

    # Objeto de salida y su ID
    def __repr__(self):
        return f'<Card {self.id}>'
    
    
# Tarea #1. Crear la tabla de usuarios
class User(db.Model):
    # Crear campos
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # email
    email = db.Column(db.String(100),  nullable=False)
    # contraseña
    password = db.Column(db.String(200), nullable=False)


# Lanzamiento de la página de contenido
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
            
        # Tarea #4. Implementar la verificación de usuario
        users_db = User.query.all()
        for user in users_db:
            if user.email == form_login and check_password_hash(user.password, form_password):
                session['user_email'] = user.email
                return redirect('/index')
        error = 'Incorrect username or password'
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')



@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']
        
        # Tarea #3. Implementar grabación de usuarios
        user = User(email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()  
        return redirect('/')
    
    else:    
        return render_template('registration.html')


# Iniciar página de contenido
@app.route('/index')
def index():
    email = session.get('user_email')
    cards = Card.query.filter_by(user_email=email).all()
    return render_template('index.html', cards=cards)

# Lanzando la página de la tarjeta
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)
    
# Iniciando la página de creación de tarjetas
@app.route('/create')
def create():
    return render_template('create_card.html')

# la forma de la tarjeta
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']

        # Creando objeto para la transferencia de la base de datos.
        email = session['user_email']
        card = Card(title=title, subtitle=subtitle, text=text, user_email=email)

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    card = Card.query.get_or_404(id)
    if card.user_email != session.get('user_email'):
        return redirect('/index')

    db.session.delete(card)
    db.session.commit()
    return redirect('/index')
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/')

@app.route('/profile')
def profile():
    # Si no hay sesión iniciada, lo mandamos al login
    email = session.get('user_email')
    if not email:
        return redirect('/')

    # Buscamos los datos del usuario
    user = User.query.filter_by(email=email).first()
    return render_template('profile.html', user=user)

if __name__ == "__main__":
    app.run(debug=True)
