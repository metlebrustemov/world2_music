import os
import time
import base64
import datetime
from flask import Blueprint, request, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from .. model import User, W2Media, db, app
from .. functions import is_email, encrypt, decrypt, ext_cont
from .. constants import M_UPLOAD_FOLDER

bp_api = Blueprint("__bp_api__", __name__, template_folder="../../templates")
api = Api(bp_api)

user_parser = reqparse.RequestParser()
user_parser.add_argument("user_name", type=str, default="default", help="User name is required.")
user_parser.add_argument("user_email", required=True, type=str, help="User email is required.")
user_parser.add_argument("user_pass", required=True, type=str, help="User password is required.")

media_parser = reqparse.RequestParser()
media_parser.add_argument("user_email", required=True, type=str, help="User email is required.")
media_parser.add_argument("u_token", required=True, type=str, help="User token is required.")
media_parser.add_argument("m_token", type=str, default="default", help="Media token is required.")
media_parser.add_argument("music_author", required=False, type=str, default="default", help="Author name is required.")
media_parser.add_argument("music_name", required=False, type=str, default="default", help="Media name is required.")
media_parser.add_argument("music_is_public", required=False, type=bool, default=True, help="Set the content's privacy policy.")
media_parser.add_argument("music_file", required=False, type=FileStorage, location="files")


class UserResource(Resource):
    def post(self):
        data = user_parser.parse_args()
        if data["user_name"] == "default":
            return '{"type":"error", "code":400, "error":"User name (user_name) is required!"}', 400
        user_name = str(data['user_name'])
        print(user_name)
        if not len(user_name) in range(4, 25) :
            return '{"type":"error", "code":"400", "error":"Username does not comply with the rules."}', 400
        user_email = str(data['user_email'])
        if not len(user_email) in range(8, 35) :
            return '{"type":"error", "code":"400", "error":"User email does not comply with the rules."}', 400
        if not is_email(user_email) :
            return '{"type":"error", "code":"400", "error":"The user email is not a valid email."}', 400
        user_pass = str(data['user_pass'])
        if not len(user_pass) in range(10, 35) :
            return '{"type":"error", "code":"400", "error":"User password does not comply with the rules."}', 400
        if not(User.query.filter_by(email=user_email).count()>0):
            if not(User.query.filter_by(username=user_name).count()>0):
                new_user = User(username=user_name, email=user_email, password=user_pass)
                db.session.add(new_user)
                db.session.commit()
                return '{"type":"success", "code":"201", "message":"New user created!"}', 201
            else:
                return '{"type":"error", "code":"409", "error":"This username is used!"}', 409
        else:
            return '{"type":"error", "code":"409", "error":"This email is being used!"}', 409
    def get(self):
        data = user_parser.parse_args()
        user_email = str(data['user_email'])
        if not len(user_email) in range(8, 35) :
            return '{"type":"error", "code":400, "error":"User email does not comply with the rules."}', 400
        if not is_email(user_email) :
            return '{"type":"error", "code":400, "error":"The user email is not a valid email."}', 400
        user_pass = str(data['user_pass'])
        if not len(user_pass) in range(10, 35) :
            return '{"type":"error", "code":400, "error":"User password does not comply with the rules."}', 400
        if User.query.filter_by(email=user_email).count()>0:
            us = User.query.filter_by(email=user_email).first()
            if us.password == user_pass:
                cur_time = str(time.time())
                cur_token = base64.b64encode(encrypt(data=us.username+us.email+cur_time, password=str(app.secret_key))).decode("utf-8")
                us.last_login = cur_time
                us.u_token = cur_token
                db.session.commit()
                return '{"type":"success", "code":"200", "token":%s}' % cur_token, 200
            else:
                return '{"type":"error", "code":"400", "error":"Password do not match!"}', 400
        else:
            return '{"type":"error", "code":"400", "error":"This email is wrong!"}', 400

class MediaResource(Resource):
    def get(self):
        data = media_parser.parse_args()
        user_email = str(data['user_email'])
        if not User.query.filter_by(email=user_email).count() > 0:
            return '{"type":"error", "code":400, "error":"This email is wrong!"}', 400
        u_token = str(data['u_token'])
        m_token = str(data['m_token'])
        user = User.query.filter_by(email=user_email).first()
        if not user.u_token == u_token:
            return '{"type":"error", "code":400, "error":"The user token is incorrect!"}', 400
        if m_token == "default":
            user_medias = W2Media.query.filter_by(user_id=user.id).all()
            user_medias.extend(W2Media.query.filter_by(is_public=True).all())
            user_medias = list(dict.fromkeys(user_medias))
            user_media_tokens = []
            for media in user_medias:
                user_media_tokens.extend([media.m_token])
            return '{"type":"success", "code":200, "tokens":%s}' %user_media_tokens, 200
        else:
            if not W2Media.query.filter_by(m_token=m_token).count() > 0:
                return '{"type":"error", "code":400, "error":"This media token is wrong!"}', 400
            media = W2Media.query.filter_by(m_token=m_token).first()
            if user.id != media.user_id and not media.is_public:
                return '{"type":"error", "code":400, "error":"This music is not yours!"}', 400
            return '{"type":"success", "code":200, "media_url":'+request.url_root+url_for('__bp_web__.static', filename='media/'+media.u_name)+', "media_name":'+media.name+', "media_author":'+media.author+'}', 200
    def post(self):
        data = media_parser.parse_args()
        user_email = str(data['user_email'])
        if not User.query.filter_by(email=user_email).count() > 0:
            return '{"type":"error", "code":400, "error":"This email is wrong!"}', 400
        u_token = str(data['u_token'])
        user = User.query.filter_by(email=user_email).first()
        if not user.u_token == u_token:
            return '{"type":"error", "code":400, "error":"The user token is incorrect!"}', 400
        if data["music_name"] == "default":
            return '{"type":"error", "code":400, "error":"Media name (music_name) is required!"}', 400
        if data["music_author"] == "default":
            return '{"type":"error", "code":400, "error":"Media author name (music_author) is required!"}', 400
        if "music_file" not in data:
            return '{"type":"error", "code":400, "error":"File not found!"}', 400
        m_file = data["music_file"]
        if m_file.filename == '':
            return '{"type":"error", "code":400, "error":"File not named!"}', 400
        if m_file and ext_cont(m_file.filename):
            file_name = secure_filename(m_file.filename)
            file_name = "{}-{}".format(datetime.datetime.strftime(datetime.datetime.utcnow(), "%s"),file_name)
            if "music_author" in data and len(data["music_author"]) >= 5:
                if "music_name" in data and len(data["music_name"]) >= 5:
                    au = data["music_author"]
                    nm = data['music_name']
                    pb = False
                    if 'music_is_public' in data:
                        pb = data["music_is_public"]
                    cur_time = str(time.time())
                    med_token = base64.b64encode(encrypt(data=file_name+str(user.id)+cur_time, password=str(app.secret_key))).decode("utf-8")
                    new_media = W2Media(user_id=user.id, name=nm ,author=au, is_public=pb, u_name=file_name, m_token=med_token)
                    db.session.add(new_media)
                    db.session.commit()
                    if not os.path.exists(M_UPLOAD_FOLDER):
                        os.mkdir(os.path.join("./static", "media"))
                    m_file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                    return '{"type":"success", "code":200, m_token='+med_token+', message="New media created!"}', 201
                else:
                    return '{"type":"error", "code":400, "error":"The name of the music is very short!"}', 400
            else:
                return '{"type":"error", "code":400, "error":"The author\'s name is very short!"}', 400
        else:
            return '{"type":"error", "code":400, "error":"Disallowed file extension!"}', 400
    def patch(self):
        data = media_parser.parse_args()
        user_email = str(data['user_email'])
        m_token = str(data['m_token'])
        if m_token == "default":
            return '{"type":"error", "code":400, "error":"Media token (m_token) is required!"}', 400
        u_token = str(data['u_token'])
        if not User.query.filter_by(email=user_email).count() > 0:
            return '{"type":"error", "code":400, "error":"This email is wrong!"}', 400
        if not User.query.filter_by(u_token=u_token).count() > 0:
            return '{"type":"error", "code":400, "error":"This user token is wrong!"}', 400
        if not W2Media.query.filter_by(m_token=m_token).count() > 0:
            return '{"type":"error", "code":400, "error":"This media token is wrong!"}', 400
        user = User.query.filter_by(u_token=u_token).first()
        if not user.email == user_email:
            return '{"type":"error", "code":400, "error":"This user token and email is do not match!"}', 400
        if data["music_name"] == "default":
            return '{"type":"error", "code":400, "error":"Media name (music_name) is required!"}', 400
        if data["music_author"] == "default":
            return '{"type":"error", "code":400, "error":"Media author name (music_author) is required!"}', 400
        media = W2Media.query.filter_by(m_token=m_token).first()
        if "music_name" in data and len(data["music_name"]) >= 5:
            media.name = data["music_name"]
        if "music_author" in data  and len(data["music_author"]) >= 5:
            media.author = data["music_author"]
        if "music_is_public" in data:
            media.is_public = data["music_is_public"]
        db.session.commit()
        return '{"type":"success", "code":200, "m_token":'+media.m_token+', message="Media updated!"}', 200 
    def delete(self):
        data = media_parser.parse_args()
        user_email = str(data['user_email'])
        m_token = str(data['m_token'])
        if m_token == "default":
            return '{"type":"error", "code":400, "error":"Media token (m_token) is required!"}', 400
        u_token = str(data['u_token'])
        if not User.query.filter_by(email=user_email).count() > 0:
            return '{"type":"error", "code":400, "error":"This email is wrong!"}', 400
        if not User.query.filter_by(u_token=u_token).count() > 0:
            return '{"type":"error", "code":400, "error":"This user token is wrong!"}', 400
        if not W2Media.query.filter_by(m_token=m_token).count() > 0:
            return '{"type":"error", "code":400, "error":"This media token is wrong!"}', 400
        user = User.query.filter_by(u_token=u_token).first()
        if not user.email == user_email:
            return '{"type":"error", "code":400, "error":"This user token and email is do not match!"}', 400
        media = W2Media.query.filter_by(m_token=m_token).first()
        if (media.user_id) != (user.id):
            return '{"type":"error", "code":400, "error":"This music is not yours!"}', 400
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], media.u_name))
        db.session.delete(media)
        db.session.commit()
        return '{"type":"success", "code":200, "message":"Media deleted!"}', 200

api.add_resource(UserResource, "/u")
api.add_resource(MediaResource, "/m")

    
            