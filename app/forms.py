from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    BooleanField, \
    PasswordField
from wtforms.validators import DataRequired, \
    Email, \
    Length, \
    EqualTo


class SignIn(FlaskForm):
    email = StringField('E-mail: ',
                        validators=[DataRequired(), Email('Invalid e-mail')],
                        render_kw={'autofocus': True, 'placeholder': 'E-mail'})
    psw = PasswordField('Password: ',
                             validators=[DataRequired(),
                                         Length(min=4,
                                                max=100,
                                                message='Password must be between 4 and 100 characters')],
                             render_kw={'placeholder': 'Password'})
    remember = BooleanField('Remember',
                            default=False)
    submit = SubmitField('Sign In')


class SignUp(FlaskForm):
    email = StringField('E-mail: ',
                        validators=[DataRequired(), Email('Invalid e-mail')],
                        render_kw={'autofocus': True, 'placeholder': 'E-mail'})
    psw = PasswordField('Password: ',
                             validators=[DataRequired(),
                                         Length(min=4,
                                                max=100,
                                                message='Password must be between 4 and 100 characters')],
                             render_kw={'placeholder': 'Password'})
    psw2 = PasswordField('Password repeat: ',
                              validators=[DataRequired(),
                                          EqualTo('psw',
                                                  message='Passwords do not match')],
                              render_kw={'placeholder': 'Password repeat'})
    submit = SubmitField('Sign Up')


class SettingsForm(FlaskForm):
    url = StringField('Site: ',
                       validators=[DataRequired(),
                                   Length(min=4,
                                          max=100,
                                          message='Website URL must be between 4 and 100 characters')],
                       render_kw={'autofocus': True, 'placeholder': 'Site'})
    submit = SubmitField('Save')
