from flask import Flask, render_template, make_response, url_for, redirect

app = Flask(__name__)

menu = [
    {"title": "Головна", "url": "/"},
    {"title": "Додати статтю", "url": "/add_post"}]

@app.route("/")
def index():
    content = render_template("flask_index.html", menu=menu, posts=[])
    res = make_response(content)
    res.headers['Content-Type'] = 'text/plain'
    res.headers['Server'] = 'server_response'
    return res

@app.route('/transfer')
def transfer():
    return redirect(url_for('index'), 301)


@app.before_first_request
def before_first_request():
    print("before_first_request() called")

@app.before_request
def after_request():
    print("before_request() called")

@app.after_request
def before_request(response):
    print("before_request() called")
    return response

@app.teardown_request
def teardown_request(response):
    print("teardown_request() called")
    return response


if __name__ == "__main__":
    app.run(debug=True)