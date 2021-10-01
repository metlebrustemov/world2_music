from flask import Blueprint, request, jsonify

bp_api = Blueprint("__bp_api__", __name__, template_folder="../../templates")

@bp_api.route("/login", methods=['POST',])
def api_login():
    pass

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