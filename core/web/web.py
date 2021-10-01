import datetime
import os
from flask import Blueprint, session, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from ..models import W2Media, User, LoginForm, RegistrationForm, FileUploadForm, db, app
from ..functions import csrf_text, ext_cont
from ..constants import M_UPLOAD_FOLDER

bp_web = Blueprint("__bp_web__", __name__, template_folder="../../templates", static_folder='../../static/', static_url_path="/")

@bp_web.route("/")
def index():
    name = None
    us_medias = None
    if "user_name" in session:
        name = session['user_name']
        us = User.query.filter_by(username=name).first()
        us_medias = W2Media.query.filter_by(user_id=us.id).all()
    p_medias = W2Media.query.filter_by(is_public=True).all()
    if us_medias != None:
        p_medias.extend(us_medias)
        p_medias = list(dict.fromkeys(p_medias))
    return render_template("index.html", user_name=name, medias=p_medias)

@bp_web.route("/register", methods=['POST', 'GET'])
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
        return redirect(url_for('__bp_web__.index'))
    form = RegistrationForm()
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    return render_template("register.html", form=form, csrf_token=csrf_token)

@bp_web.route("/login", methods=['POST', 'GET'])
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
        return redirect(url_for('__bp_web__.index'))
    form = LoginForm()
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    return render_template("login.html", form=form, csrf_token=csrf_token)

@bp_web.route("/upload", methods=['POST', 'GET'])
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
                        us = User.query.filter_by(username=session["user_name"]).first()
                        au = request.form["music_author"]
                        nm = request.form['music_name']
                        pb = False
                        if 'music_is_public' in request.form:
                            if str(request.form["music_is_public"]) == "1":
                                pb = True
                        new_media = W2Media(user_id=us.id, name=nm ,author=au, is_public=pb, u_name=file_name)
                        db.session.add(new_media)
                        db.session.commit()
                        if not os.path.exists(M_UPLOAD_FOLDER):
                            os.mkdir(os.path.join("./static", "media"))
                        m_file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                        return redirect(url_for('__bp_web__.index'))
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


@bp_web.route("/delete/<m_id>", methods=['POST', 'GET'])
def delete(m_id):
    if "user_name" in session:
        name = session['user_name']
        us = User.query.filter_by(username=name).first()
        if W2Media.query.filter_by(id=m_id).count() > 0:
            media = W2Media.query.filter_by(id=m_id).first()
            if (media.user_id) != (us.id):
                return render_template("message.html", msg="This music is not yours!")
            if request.method == "POST" and request.form['csrf_token'] == session["csrf_token"]:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], media.u_name))
                db.session.delete(media)
                db.session.commit()
                session.pop('csrf_token', None)
                return redirect(url_for("__bp_web__.index")) # !!! Bura hazir deyik
            csrf = csrf_text(size=64)
            session["csrf_token"] = csrf
            return render_template("delete.html", csrf=csrf, media=media, user_name=name)
        return render_template("message.html", msg="The music you wanted to delete could not be found!")
    else:
        return render_template("message.html", msg="You don't have permission to this page!")


@bp_web.route("/user/<uid>") 
def user_home(uid):
    if not(User.query.filter_by(id=uid).count()>0):
        return render_template('message.html', msg="This user does not exist!")
    us = User.query.filter_by(id=uid).first()
    us_medias = None
    name = None 
    if ("user_name" in session) and (us.username == session['user_name']):
        name = session['user_name']
        us_medias = W2Media.query.filter_by(user_id=us.id).all()
    else: 
        if W2Media.query.filter_by(is_public=True).count() > 0:
            us_medias = [m for m in W2Media.query.filter_by(is_public=True).all() if str(m.user_id)==uid]
    return render_template("index.html", user_name=name, medias=us_medias)
    
    

@bp_web.route("/logout")
def logout():
	session.pop('user_name', None)
	return redirect(url_for('__bp_web__.index'))