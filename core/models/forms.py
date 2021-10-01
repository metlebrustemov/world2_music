from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField, FileRequired

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
    music_is_public = BooleanField("Can be accessed for each user", render_kw={"class":"form-check-input","checked":"checked","value":"1"})
    submitbutton = SubmitField("Upload")
