import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.secret_key = b'HbfGMYwEOnLdm3USo5k7JRAzn0P3oVEHPdLSoNKku3qmKfWUjt6tsgbbnPuoYWmXNiGIjpyXtm7DZ1DbAYxx1F8LmerBW1DsaeSf'
db_path = os.path.join(os.path.dirname(__file__), 'vt.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class W2Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    name = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(120), unique=True, nullable=False)
    is_public = db.Column(db.Boolean(), default=True, nullable=False)
    u_name = db.Column(db.String(100), unique=True, nullable=False) #unikal name

    def __repr__(self):
        return '<W2Media %r>' % self.u_name

db.create_all()
#//////////////////////////////////////////////////////////////////////

class RegistrationForm(Form):
    username = StringField('User Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control"})
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35), validators.EqualTo('confirm', message='Passwords must match')], render_kw={"class":"form-control"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired()], render_kw={"class":"form-control"})
    submitbutton = SubmitField("Register")

class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35)], render_kw={"class":"form-control"})
    submitbutton = SubmitField("Login")

#//////////////////////////////////////////////////////////////////////

@app.template_filter("idToName")
def idToName(id):
    us = User.query.filter_by(id=id).first()
    return us.username


#//////////////////////////////////////////////////////////////////////


@app.route("/")
def index():
    name = None
    us_medias = None
    if "user_name" in session:
        name = session['user_name']
        us = User.query.filter_by(username=name).first()
        us_medias = W2Media.query.filter_by(user_id=us.id).all()
    p_medias = W2Media.query.filter_by(is_public='True').all()
    if us_medias != None:
        p_medias.extend(us_medias)
    return render_template("index.html", user_name=name, medias=p_medias)

@app.route("/register", methods=['POST', 'GET'])
def reg_user():
    if ("user_name" in session):
        session.pop('user_name', None)
    if request.method == 'POST' :
        user_name = request.form['username']
        user_email = request.form['email']
        user_pass = request.form['password']
        user_confirm = request.form['confirm']
        if not(User.query.filter_by(email=user_email).count()>0):
            if not(User.query.filter_by(username=user_name).count()>0):
                if user_pass == user_confirm:
                    new_user = User(username=user_name, email=user_email, password=user_pass)
                    db.session.add(new_user)
                    db.session.commit()
                    session['user_name'] = user_name
                else:
                    return render_template('message.html', msg="Passwords do not match!")
            else:
                return render_template('message.html', msg="This username is used!")
        else:
            return render_template('message.html', msg="This email is being used!")
        return redirect(url_for('index'))
    form = RegistrationForm()
    return render_template("register.html", form=form)

@app.route("/login", methods=['POST', 'GET'])
def login_user():
    if ("user_name" in session):
        session.pop('user_name', None)
    if request.method == 'POST' :
        user_email = request.form['email']
        user_pass = request.form['password']
        if User.query.filter_by(email=user_email).count()>0:
            us = User.query.filter_by(email=user_email).first()
            if us.password == user_pass:
                session['user_name'] = us.username
            else:
                return render_template('message.html', msg="Passwords do not match!")
        else:
            return render_template('message.html', msg="This email is wrong!")
        return redirect(url_for('index'))
    form = LoginForm()
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
	session.pop('user_name', None)
	return redirect(url_for('index'))

    

if __name__ == "__main__":
    app.run(debug=True)