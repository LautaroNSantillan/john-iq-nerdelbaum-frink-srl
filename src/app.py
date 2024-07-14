from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from datetime import datetime

import re

from models.ModelUser import ModelUser
from models.entities.User import User
from models.ModelReview import ModelReview
from models.entities.Review import Review
from models.ModelCompany import ModelCompany
from models.entities.Company import Company



app = Flask(__name__)
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

csrf = CSRFProtect(app)
db = MySQL(app)

@app.context_processor
def inject_year():
    return {'yearnow': datetime.now().year}

@app.context_processor
def is_user_logged_in():
    return{'is_logged': current_user.is_authenticated} 

@app.route("/")
@app.route("/home")
def index():
    companies = ModelCompany.get_all_companies(db)
    return render_template('index.html', companies=companies)

@app.route('/company', methods=['GET', 'POST'])
@login_required
def create_company():
    if current_user.role != 'ADMIN':
        flash('Unauthorized access', 'error')
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form['name']
        img = request.form['img']
        location = request.form['location']
        new_company = Company(name,img,location, None)

        try:
            if ModelCompany.create_company(db, new_company):  
                flash('Company created successfully!', 'success')
                return redirect('/')  # Redirect to homepage or appropriate page
            else:
                flash('Error creating company', 'danger')
                return render_template('auth/companies.html')  # Render form again on failure
        except Exception as ex:
            flash(f'Error creating company: {str(ex)}', 'danger')
            return render_template('auth/companies.html')  # Render form again on exception

    return render_template('auth/companies.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['regname']
        fullname = request.form['regfullname']
        password = request.form['regpass']

        errmsg = []
        if len(username) > 20:
            errmsg.append('Username must be shorter than 20 characters.')
        if len(fullname) > 50:
            errmsg.append('Full name must be shorter than 50 characters.')
        if not re.search(r'[A-Z]', password):
            errmsg.append('Password must include at least one uppercase letter.')
        if not re.search(r'\d', password):
            errmsg.append('Password must include at least one number.')

        if errmsg:
            flash('\n'.join(errmsg), 'error')
            return render_template('auth/login.html', errbool=True,regname=username, regfullname=fullname)
           
        new_user = User(None, username, password, fullname)  

        if ModelUser.register(db, new_user): 
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
#---------------------------REVIEWS
@app.route('/review')
@login_required
def review():
    user_review = ModelReview.get_review_by_user_id(db, current_user.id)
    return render_template('site_reviews/new_review.html', review=user_review)


@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    if request.method == 'POST':
        review_text = request.form.get('comment')
        rating = request.form.get('rating')
        
        new_review = Review.from_form_data(review_text, rating)
        
        if ModelReview.create_review(db, new_review):
            flash('Review submitted successfully', 'success')
            return redirect(url_for('review'))
        else:
            flash('Failed to submit review', 'error')
            return redirect(url_for('review'))


@app.route('/update_review', methods=['GET', 'POST'])
@login_required
def update_review():
    if request.method == 'POST':
        review = ModelReview.get_review_by_user_id(db, current_user.id)
        new_review_text = request.form.get('new_comment')
        new_rating = request.form.get('new_rating')

        if review:
            success, message = ModelReview.update_review(db, review.review_id, new_review_text, new_rating)
            if success:
                flash(message, 'success')
                return redirect(url_for('review'))
            else:
                flash(message, 'error')
                review = ModelReview.get_review_by_user_id(db, current_user.id)
                return render_template('site_reviews/update_review.html', review=review)
        else:
            flash("No review found for the current user.", 'error')
            review = ModelReview.get_review_by_user_id(db, current_user.id)
            return render_template('site_reviews/review.html')
        
    else:
        review = ModelReview.get_review_by_user_id(db, current_user.id)
        return render_template('site_reviews/update_review.html', review=review)


@app.route('/delete_review', methods=['POST'])
@login_required  
def delete_review():
    review_id = request.form.get('review_id')
    success, message = ModelReview.disable_review(db, review_id)
    if success:
        flash('Review disabled successfully.', 'success')
    else:
        flash(f'Error disabling review: {message}', 'error')
    return redirect(url_for('review'))

#---------------------------PROFILE
@app.route('/my_profile')
def profile():
    user = ModelUser.get_by_id(db, current_user.id) 
    if user:
        review = ModelReview.get_review_by_user_id(db, current_user.id)
        return render_template('profile/profile.html', user=user, review=review)
    else:
        return "User not found", 404
    
@app.route('/user/<string:username>')
def visit_user(username):
    user = ModelUser.get_by_username(db, username)
    if user:
        review = ModelReview.get_review_by_user_id(db, user.id)
        return render_template('profile/user.html', user=user, review=review)
    else:
        return "User not found", 404
    
    

@app.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    if request.method == 'POST':
        new_fullname = request.form.get('fullname')
        new_username = request.form.get('username')

        success, message = ModelUser.update_user_info(db, current_user.id, new_fullname, new_username)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('profile'))
        else:
            flash(message, 'error')
    
    return render_template('profile/update_profile.html')

#---------------------------CONTACT
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        clientName = request.form.get('clientName')
        clientInquiry = request.form.get('clientInquiry')
        clientSpecies = request.form.get('clientSpecies')
        if len(clientName) == 0 or len(clientInquiry) == 0 or clientSpecies is None:
                flash("Por favor complete los campos Nombre, Consulta y Especie", 'error')
                return render_template('contact/contact.html')
        else:
             flash("Recibimos su consulta!", 'success')
             return render_template('contact/contact.html')
    return render_template('contact/contact.html')
#---------------------------ERROR HANDLERS
def status_401(err):
    return redirect(url_for('login'))

def status_404(err):
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True)