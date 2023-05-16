from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, DecimalField, PasswordField, SubmitField, SelectField, widgets
from wtforms.validators import DataRequired, Optional, Length, Email, EqualTo, StopValidation, InputRequired
import wtforms.fields.html5 as html5
from wtforms.widgets import html5 as h5widgets
from wtforms_components import TimeField
from wtforms.fields import SelectMultipleField
import decimal
from decimal import Decimal


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except with the option of rounding
    the data always.
    """
    def __init__(self, label=None, validators=[Optional()], places=2, rounding=None,
                 round_always=False, **kwargs):
        super(BetterDecimalField, self).__init__(
            label=label, validators=validators, places=places, rounding=
            rounding, **kwargs)
        self.round_always = round_always

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                valuelist[0] = valuelist[0].replace(",", ".")
                self.data = decimal.Decimal(valuelist[0])
                if self.round_always and hasattr(self.data, 'quantize'):
                    exp = decimal.Decimal('.1') ** self.places
                    if self.rounding is None:
                        quantized = self.data.quantize(exp)
                    else:
                        quantized = self.data.quantize(
                            exp, rounding=self.rounding)
                    self.data = quantized
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(self.gettext('Niepoprawny format'))



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

    # TODO do zmiany na (1, "Adwokat") itd.... W BAZIE DANYCH TEŻ ZMIENIĆ NA INT POLE !!!!!!!!!!!!!

    profession = SelectField(u'Zawód', choices=[(None, ''), ("Adwokat", "Adwokat"), ("Radca prawny", "Radca prawny"), ("Rzecznik patentowy", "Rzecznik patentowy"),
                                               ("Aplikant adwokacki", "Aplikant adwokacki"), ("Aplikant radcowski", "Aplikant radcowski"), ("Aplikant rzecznikowski",
                                                "Aplikant rzecznikowski"), ("inne", "inne")], validators=[DataRequired()])

    # TODO do zmiany na (1, "Warszawa") itd.... W BAZIE DANYCH TEŻ ZMIENIĆ NA INT POLE !!!!!!!!!!!!!!!

    region = SelectField(u'Apelacja', choices=[(None, ''), ("Warszawa", "Warszawa"), ("Białystok", "Białystok"), ("Poznań", "Poznań"), ("Gdańsk", "Gdańsk"),
                                              ("Szczecin", "Szczecin"), ("Łódź", "Łódź"), ("Katowice", "Katowice"), ("Wrocław", "Wrocław"), ("Kraków", "Kraków"),
                                              ("Lublin", "Lublin"), ("Rzeszów", "Rzeszów")], validators=[DataRequired()])                                   
    town = StringField('Miasto',
                              validators=[DataRequired(), Length(min=2, max=30)])

    password = PasswordField('Hasło', validators=[DataRequired()])

    confirm_password = PasswordField('Potwierdź hasło',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Zarejstruj się')



def get_order_types():
    return [(1, 'Prawo cywilne'), (2, 'Prawo karne'), (3, 'Prawo handlowe'), (4, 'Mandarin'), (5, 'Prawo administracyjne'), (6, 'Prawo finansowe'),
           (7, 'Prawo gospodarcze'), (8, 'Prawo autorskie'), (9, 'Prawo bankowe'), (10, 'Prawo pracy'), (11, 'Prawo konstytucyjne i ustrojowe'),
           (12, 'Prawo międzynarodowe'), (13, 'Prawo Unii Europejskiej'), (14, 'Nieruchomości'), (14, 'Prawo własności intelektualnej'),
           (15, 'Prawo własności przemysłowej'), (15, 'Zamówienia publiczne'), (16, 'Prawo drogowe'), (17, 'inne')]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ol', prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxAtLeastOne():
    def __init__(self, message=None):
        if not message:
            message = 'Wybierz co najmniej jeden rodzaj.'
        self.message = message

    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation(self.message)



class LoginForm(FlaskForm):


    username = StringField('Nazwa użytkownika',
                        validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')



class AdvertisementForm(FlaskForm):


    title = StringField('Tytuł ogłoszenia', validators=[DataRequired(), Length(min=2, max=50)]) 
    start_date = html5.DateField('Data rozpoczęcia', validators=[DataRequired()]) 
    start_time = TimeField('Godzina rozpoczęcia', validators=[DataRequired()]) 
    advertisement_type = SelectField('Typ zlecenia', choices=[("", "---"), (1, 'Rozprawa'), (2, 'Inna czynność'), (3, 'Dyżur w sądzie 24h'),
                                               (4, 'Sporządzenie pisma')], validators=[DataRequired()])

    appeal = SelectField('', choices=[("", "---")], coerce=int, validators=[DataRequired('Wybierz element z listy')], id='select_appeal')
    court_of_appeal = SelectField('', choices=[("", "---")], coerce=int, validators=[Optional()], id='select_court_of_appeal')
    district_court = SelectField('', choices=[("", "---")], coerce=int, validators=[Optional()], id='select_district_court')
    district_court_department = SelectField('', choices=[("", "---")], coerce=int, validators=[Optional()], id='select_district_court_department')
    regional_court_department = SelectField('', choices=[("", "---")], coerce=int, validators=[Optional()], id='select_regional_court_department')


    file_review = SelectField('Wymagane przejrzenia akt', choices=[("", "---"), (1, "Tak"), (2, "Nie")], validators=[DataRequired()])

    contact_method = SelectField('Preferowany kontakt', choices=[("", "---"), (1, "Telefoniczny"), (2, "E-mail"), 
                                                                 (3, "Osobisty")], validators=[DataRequired()])

    salary = BetterDecimalField('Wynagrodzenie', round_always=True)

    duration= html5.IntegerField("Czas trwania (godziny)", widget=h5widgets.NumberInput(min=0, max=24, step=1), validators=[DataRequired()]) 

    address = StringField('Adres, numer budynku i sali', validators=[DataRequired(), Length(min=2, max=150)]) 

    description = TextAreaField('Opis', validators=[DataRequired(), Length(min=10, max=255)]) 

    order_type = MultiCheckboxField('Rodzaj zlecenia', choices=get_order_types(), validators=[MultiCheckboxAtLeastOne()], coerce=int)

    submit = SubmitField('Dodaj')





    


