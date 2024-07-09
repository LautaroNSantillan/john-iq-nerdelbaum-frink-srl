from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from config import config

from models.ModelUser import ModelUser

from models.entities.User import User

app = Flask(__name__)

db = MySQL(app)

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = User(0, request.form['logemail'], request.form['logpass'])
        logged_user= ModelUser.login(db, user)
        if logged_user != None:
            print(logged_user.password)
            if logged_user.password:
                return redirect(url_for('index'))
            else:
                flash("Contraseña incorrecta")   
                return render_template('auth/login.html')
        else:
            flash("Usuario no econtrado")   
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()