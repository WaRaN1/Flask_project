import datetime
from flask import Flask, make_response, request, session


app = Flask(__name__)
app.config['SECRET_KEY'] = '80e66bbe1db1b1d3ff5f1e8b54f26aa6d894cb2f'
app.permanent_session_lifetime = datetime.timedelta(days=10)


@app.route("/")
def index():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1  # оновлення даних сесії
    else:
        session['visits'] = 1   # Запис даних у сесію
    return f"<h1>Main Page</h1>Кількість переглядів: {session['visits']}"

data = [1, 2, 3, 4]
@app.route("/session")
def session_data():
    session.permanent = True
    if 'data' not in session:
        session['data'] = data
    else:
        session['data'][1] += 1
        session.modified = True

    return f"<p>session['data']: {session['data']}"



if __name__ == "__main__":
    app.run(debug=True)