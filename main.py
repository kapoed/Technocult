import secrets
from flask import Flask, render_template, redirect
from data.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from forms.registerform import RegistrationForm
from forms.loginform import LoginForm
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)


current_user = None


def add_new_user(login, email, hashed_password):
    user = User()
    user.login = login
    user.email = email
    user.hashed_password = hashed_password
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    global current_user
    current_user = user


@app.route('/')
def index():
    return render_template('base.html', current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        add_new_user(form.login.data, form.email.data, generate_password_hash(form.password.data))
        return redirect('.')
    return render_template('register.html', title='Авторизация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('.')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1', debug=True)