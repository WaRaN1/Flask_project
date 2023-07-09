from flask import Flask, make_response, request

app = Flask(__name__)

menu = [{"title": "Встановлення", "url": "/"},
        {"title": "Перший додаток", "url": "/addd_post"}]

@app.route("/")
def index():
    return "<h1>Main Page</h1>"

'''Збереження куків при логіні'''
@app.route("/login")
def login():
    log = ""
    if request.cookies.get('logged'):
        log = request.cookies.get('logged')

    res = make_response(f"<h1>Форма авторизації</h1><p>logged: {log}")
    res.set_cookie("logged", "yes")
    return res

'''Обнулення куків'''
@app.route("/logout")
def logout():
    res = make_response("<p>Ви вже не авторизовані!</p>")
    res.set_cookie("logged", "", 0)
    return res



if __name__ == "__main__":
    app.run(debug=True)