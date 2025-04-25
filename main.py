import secrets
from flask import Flask, render_template, redirect
from forms.registerform import RegistrationForm
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def login():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('register.html', title='Авторизация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1', debug=True)