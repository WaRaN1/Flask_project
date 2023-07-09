import sqlite3
import os

from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from  forms import LoginForm, Registerform
from admin.admin import admin



# конфігурація
DATABASE = '/tmp/main.db'
DEBUG = True
SECRET_KEY = 'sadsadsa45dadsad534asdadas65'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'main.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступу до закритих сторінок"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Допоміжна функція для створення таблиці БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Зєднання з БД, якщо воно ще не встановлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    '''Встановлюємо зєднання з БД перед виконанням запиту'''
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    ''''Закриваємо зєднання з БД, якщо воно було встановлене'''

    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route("/")
def index():
    return render_template("flask_index.html", menu=dbase.getMenu(), posts=dbase.getPostsAnonce())

@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Помилка додавання статті', category='error')
            else:
                flash('Статтю додано успішно', category='success' )
        else:
            flash('Помилка додавання статті', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Додовання татті")



@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Невірна пара логін/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизація", form=form)

    # if request.method == "POST":
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get("next") or url_for("profile"))
    #
    #     flash("Невірна пара логін/пароль", "error")
    #
    # return render_template("login.html", menu=dbase.getMenu(), title="Авторизація")


@app.route("/register", methods=["POST", "GET"])
def register():
    form = Registerform()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Ви успішно зареєстровані", "success")
            return redirect(url_for('login'))
        else:
            flash("Помилка при додаванні у БД", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Реєстрація", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профіль")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'images_html/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Помилка оновлення аватару", "error")
                flash("Аватар оновлено", "success")
            except FileNotFoundError as e:
                flash("Помилка читання файла", "error")
        else:
            flash("Помилка оновлення аватару", "error")

    return redirect(url_for('profile'))




if __name__ == '__main__':
    app.run(debug=True)

