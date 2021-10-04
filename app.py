import os
import string
import random
import datetime
from flask import request, render_template, jsonify
from core.api import bp_api
from core.web import bp_web
from core.model import User, app



app.register_blueprint(bp_api, url_prefix="/api")
app.register_blueprint(bp_web)


@app.template_filter("idToName")
def idToName(id):
    us = User.query.filter_by(id=id).first()
    return us.username


#//////////////////////////////////////////////////////////////////////


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify(type="error", code=str(e.code), error=str(e)), e.code
    return render_template('404.html'), 404

@app.errorhandler(405)
def page_not_allowed(e):
    if request.path.startswith("/api/"):
        return jsonify(type="error", code=str(e.code), error=str(e)), e.code
    return render_template('405.html'), 405


if __name__ == "__main__":
    app.run(debug=False)
    
