from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from config import config
import re

from models.ModelUser import ModelUser

from models.entities.User import User

app = Flask(__name__)
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)
csrf = CSRFProtect()
db = MySQL(app)

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['regname']
        fullname = request.form['regfullname']
        password = request.form['regpass']

        errmsg = []
         # Validation for username being shorter than 20 characters
        if len(username) > 20:
            errmsg.append('Username must be shorter than 20 characters.')

        # Validation for fullname being shorter than 50 characters
        if len(fullname) > 50:
            errmsg.append('Full name must be shorter than 50 characters.')

        # Validation for password including at least one uppercase letter and one number
        if not re.search(r'[A-Z]', password):
            errmsg.append('Password must include at least one uppercase letter.')
        if not re.search(r'\d', password):
            errmsg.append('Password must include at least one number.')

        if errmsg:
            flash('\n'.join(errmsg), 'error')
            # Preserve form data by passing it back to the template
            return render_template('auth/login.html', errbool=True,regname=username, regfullname=fullname)
           

        # Create a new user instance
        new_user = User(None, username, password, fullname)  # Adjust according to your User class

        # Example: save the new user to the database using ModelUser
        if ModelUser.register(db, new_user):  # Adjust ModelUser method according to your implementation
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/login.html')

    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = User(0, request.form['logemail'], request.form['logpass'])
        logged_user= ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('index'))
            else:
                flash("Contraseña incorrecta",'error')   
                return render_template('auth/login.html')
        else:
            flash("Usuario no econtrado",'error')   
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_comment')
@login_required
def create_comment():
    return "<h1>CREATE COMENt</h1>"

def status_401(err):
    return redirect(url_for('login'))

def status_404(err):
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()