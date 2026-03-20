from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-for-production'
application = app

FULL_NAME = 'Николаев Алексей Владимирович'
GROUP = '241-3211'


class User(UserMixin):
    def __init__(self, user_id: str, username: str, password: str):
        self.id = user_id
        self.username = username
        self.password = password


USERS = {
    'user': User('1', 'user', 'qwerty')
}

USERS_BY_ID = {user.id: user for user in USERS.values()}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id: str):
    return USERS_BY_ID.get(user_id)


@app.context_processor
def inject_globals():
    return {
        'full_name': FULL_NAME,
        'group_number': GROUP,
    }


@app.route('/')
def index():
    return render_template('index.html', title='Главная')


@app.route('/counter')
def counter():
    visits = session.get('counter_visits', 0) + 1
    session['counter_visits'] = visits
    return render_template('counter.html', title='Счётчик посещений', visits=visits)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже вошли в систему.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = USERS.get(username)
        if user and user.password == password:
            login_user(user, remember=remember)
            flash('Вход выполнен успешно.', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))

        flash('Неверный логин или пароль.', 'danger')

    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')


if __name__ == '__main__':
    app.run(debug=True)
