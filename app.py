import os
import string
import random
import hashlib
import datetime
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = b'HbfGMYwEOnLdm3USo5k7JRAzn0P3oVEHPdLSoNKku3qmKfWUjt6tsgbbnPuoYWmXNiGIjpyXtm7DZ1DbAYxx1F8LmerBW1DsaeSf'
db_path = os.path.join(os.path.dirname(__file__), 'vt.db')
db_uri = 'sqlite:///{}'.format(db_path)
M_UPLOAD_FOLDER = "static/media"
M_EXTENTIONS = set(['mp3','wav'])
app.config['UPLOAD_FOLDER'] = M_UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000 #uploaded file max size


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
    username = StringField('User Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"4"})
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35), validators.EqualTo('confirm', message='Passwords must match')], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired()], render_kw={"class":"form-control"})
    submitbutton = SubmitField("Register")

class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    submitbutton = SubmitField("Login")


class FileUploadForm(Form):
    music_name = StringField('Music Name', [validators.DataRequired(), validators.Length(min=5, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"5"})
    music_author = StringField('Music Author Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"5"})
    music_file = FileField("Select File", validators=[FileRequired()],render_kw={"class":"form-control"})
    submitbutton = SubmitField("Upload")

#//////////////////////////////////////////////////////////////////////

@app.template_filter("idToName")
def idToName(id):
    us = User.query.filter_by(id=id).first()
    return us.username

def ext_cont(file_name):
   return '.' in file_name and \
   file_name.rsplit('.', 1)[1].lower() in M_EXTENTIONS

def csrf_text(size=32, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


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
        p_medias = list(dict.fromkeys(p_medias))
    return render_template("index.html", user_name=name, medias=p_medias)

@app.route("/register", methods=['POST', 'GET'])
def reg_user():
    if ("user_name" in session):
        session.pop('user_name', None)
    if request.method == 'POST' and  request.form['csrf_token'] == session["csrf_token"]:
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
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    return render_template("register.html", form=form, csrf_token=csrf_token)

@app.route("/login", methods=['POST', 'GET'])
def login_user():
    if ("user_name" in session):
        session.pop('user_name', None)
    if request.method == 'POST'  and  request.form['csrf_token'] == session["csrf_token"]:
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
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    return render_template("login.html", form=form, csrf_token=csrf_token)

@app.route("/upload", methods=['POST', 'GET'])
def upload_file():
    if "user_name" in session:
        if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
            if "music_file" not in request.files:
                return render_template("message.html", msg="File not found!")
            m_file = request.files["music_file"]
            if m_file.filename == '':
                return render_template("message.html", msg="File not named!")
            if m_file and ext_cont(m_file.filename):
                file_name = secure_filename(m_file.filename)
                file_name = "{}-{}".format(datetime.datetime.strftime(datetime.datetime.utcnow(), "%s"),file_name)
                if "music_author" in request.form and len(request.form["music_author"]) >= 5:
                    if "music_name" in request.form and len(request.form["music_name"]) >= 5:
                        m_file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                        us = User.query.filter_by(username=session["user_name"]).first()
                        au = request.form["music_author"]
                        nm = request.form['music_name']
                        new_media = W2Media(user_id=us.id, name=nm ,author=au, is_public=True, u_name=file_name)
                        db.session.add(new_media)
                        db.session.commit()
                        return redirect(url_for('index'))
                    else:
                        return render_template("message.html", msg="The name of the music is very short!")
                else:
                    return render_template("message.html", msg="The author's name is very short!")
            else:
                return render_template("message.html", msg="Disallowed file extension!")
        else:
            name = session['user_name']
            form = FileUploadForm()
            csrf_token = csrf_text()
            session["csrf_token"] = csrf_token
            return render_template("upload.html", form=form, user_name=name, csrf_token=csrf_token)
    else:
        return render_template("message.html", msg="You don't have permission to this page!")

@app.route("/user/<uid>")
def user_home(uid):
    if not(User.query.filter_by(id=uid).count()>0):
        return render_template('message.html', msg="Thisthis does not exist!")
    us = User.query.filter_by(id=uid).first()
    us_medias = None
    name = None 
    if "user_name" in session:
        name = session['user_name']
        if us.username == session['user_name']:
            us_medias = W2Media.query.filter_by(user_id=us.id).all()
    else:
        us_medias = [m for m in W2Media.query.filter_by(is_public='True').all() if str(m.user_id)==uid]
    return render_template("index.html", user_name=name, medias=us_medias)
    
    

@app.route("/logout")
def logout():
	session.pop('user_name', None)
	return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=False)