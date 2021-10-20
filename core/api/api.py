import time
import base64
from flask import Blueprint, request, jsonify
from .. model import User, db, app
from .. functions import is_email, encrypt, decrypt

bp_api = Blueprint("__bp_api__", __name__, template_folder="../../templates")


@bp_api.route("/register", methods=['POST'])
def api_register():
    data = request.json
    user_name = str(data['user_name'])
    if not len(user_name) in range(4, 25) :
        return jsonify(type="error", code=400, error="Username does not comply with the rules."), 400
    user_email = str(data['user_email'])
    if not len(user_email) in range(8, 35) :
        return jsonify(type="error", code=400, error="User email does not comply with the rules."), 400
    if not is_email(user_email) :
        return jsonify(type="error", code=400, error="The user email is not a valid email."), 400
    user_pass = str(data['user_pass'])
    if not len(user_pass) in range(10, 35) :
        return jsonify(type="error", code=400, error="User password does not comply with the rules."), 400
    if not(User.query.filter_by(email=user_email).count()>0):
        if not(User.query.filter_by(username=user_name).count()>0):
            new_user = User(username=user_name, email=user_email, password=user_pass)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(type="success", code=200, message="New user created!"), 201
        else:
            return jsonify(type="error", code=409, error="This username is used!"), 409
    else:
        return jsonify(type="error", code=409, error="This email is being used!"), 409

@bp_api.route("/login", methods=['POST',])
def api_login():
    data = request.json
    user_email = str(data['user_email'])
    if not len(user_email) in range(8, 35) :
        return jsonify(type="error", code=400, error="User email does not comply with the rules."), 400
    if not is_email(user_email) :
        return jsonify(type="error", code=400, error="The user email is not a valid email."), 400
    user_pass = str(data['user_pass'])
    if not len(user_pass) in range(10, 35) :
        return jsonify(type="error", code=400, error="User password does not comply with the rules."), 400
    if User.query.filter_by(email=user_email).count()>0:
        us = User.query.filter_by(email=user_email).first()
        if us.password == user_pass:
            cur_time = str(time.time())
            cur_token = base64.b64encode(encrypt(data=us.username+us.email+cur_time, password=str(app.secret_key))).decode("utf-8")
            us.last_login = cur_time
            us.u_token = cur_token
            db.session.commit()
            return jsonify(type="success", code=200, token=cur_token), 200
        else:
            return jsonify(type="error", code=400, error="Passwords do not match!"), 400
    else:
        return jsonify(type="error", code=400, error="This email is wrong!"), 400

@bp_api.route("/u/<u_token>", methods=['POST',])
def api_user_media_list(u_token):
    pass

@bp_api.route("/g/<u_token>/<m_token>", methods=['POST',])
def api_get_media(u_token, m_token):
    pass

@bp_api.route("/a/<u_token>", methods=['POST',])
def api_add_media(u_token):
    pass

@bp_api.route("/m/<u_token>/<m_token>", methods=['POST',])
def api_mod_media(u_token, m_token):
    pass

@bp_api.route("/d/<u_token>/<m_token>", methods=['POST'],)
def api_del_media(u_token, m_token):
    pass