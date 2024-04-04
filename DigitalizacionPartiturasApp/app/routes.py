from app import app
from flask import render_template
from app.forms import LoginForm, RegistrationForm

@app.route('/')
def home():
    return 'Página Principal'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            return redirect(url_for('home'))
        else:
            return 'Usuario o contraseña inválida'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

