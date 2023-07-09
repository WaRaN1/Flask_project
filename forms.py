from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль повинен бути від 4 до 100 символів")])
    remember = BooleanField("Запам'ятати", default=False)
    submit = SubmitField("Увійти")

class Registerform(FlaskForm):
    name = StringField("Ім'я: ", validators=[Length(min=4, max=100, message="Ім'я повино бути від 4 до 100 символів")])
    email = StringField("Email: ", validators=[Email("Некорректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль повинен бути від 4 до 100 символів")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Паролі не співпадають")])
    submit = SubmitField("Реєстрація")
