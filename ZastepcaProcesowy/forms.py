from flask_wtf import FlaskForm
from wtforms import Form, validators, StringField, PasswordField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from wtforms.widgets import TextArea
import wtforms.fields.html5 as html5
from wtforms_components import TimeField


class RegistrationForm(FlaskForm):


    username = StringField('Nazwa użytkownika',
                           validators=[DataRequired(), Length(min=2, max=50)])

    email = StringField("Email", validators=[DataRequired(), Email()])

    name = StringField('Imię',
                        validators=[DataRequired(), Length(min=2, max=25)])
    lastname = StringField('Nazwisko',
                        validators=[DataRequired(), Length(min=2, max=35)])

    phonenumber = StringField('Numer telefonu',
                        validators=[DataRequired(), Length(min=8, max=12)])

    profession = SelectField(u'Zawód', choices=[(None, ''), ("Adwokat", "Adwokat"), ("Radca prawny", "Radca prawny"), ("Rzecznik patentowy", "Rzecznik patentowy"),
                                               ("Aplikant adwokacki", "Aplikant adwokacki"), ("Aplikant radcowski", "Aplikant radcowski"), ("Aplikant rzecznikowski",
                                                "Aplikant rzecznikowski"), ("inne", "inne")])

    region = SelectField(u'Apelacja', choices=[(None, ''), ("Szczecin", "Szczecin"), ("Gdańsk", "Gdańsk"), ("Poznań", "Poznań"), ("Białystok", "Białystok"),
                                              ("Warszawa", "Warszawa"), ("Łódź", "Łódź"), ("Katowice", "Katowice"), ("Wrocław", "Wrocław"), ("Kraków", "Kraków"),
                                              ("Lublin", "Lublin"), ("Rzeszów", "Rzeszów")])                                   
    town = StringField('Miasto',
                              validators=[DataRequired(), Length(min=2, max=30)])

    password = PasswordField('Hasło', validators=[DataRequired()])

    confirm_password = PasswordField('Potwierdź hasło',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Zarejstruj się')


class LoginForm(FlaskForm):


    username = StringField('Nazwa użytkownika',
                        validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')



class AdvertisementForm(Form):

    name = StringField('Nazwa użytkownika',
                           validators=[DataRequired(), Length(min=2, max=50)])


    start_date = html5.DateField("Date Time Sample", validators=[DataRequired()])
    start_time = TimeField('Start time', validators=[DataRequired()])
    


