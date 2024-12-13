from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db import db
from database import Book, User, create_database
from flask_login import current_user, LoginManager

app = Flask(__name__)

# Конфигурация для подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:1234@localhost:5432/books_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Для работы сессий и flash-сообщений

# Инициализируем SQLAlchemy с приложением
db.init_app(app)

# Flask-Login настройка
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/books')
def books_page():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/progress')
def progress():
    user = get_current_user()  # Получаем текущего пользователя
    if user is None:  # Проверяем, авторизован ли пользователь
        return redirect(url_for('login'))  # Перенаправляем на страницу логина

    # Фильтруем книги, принадлежащие пользователю
    books = Book.query.filter_by(whos=user.id).all()
    return render_template('progress.html', books=books, user=user)

@app.route("/update_progress", methods=["POST"])
def update_progress():
    book_id = request.form["book_id"]
    action = request.form["action"]

    book = Book.query.get(book_id)
    if book:
        # Обновляем прогресс в зависимости от действия
        if action == "increase" and book.progress < 100:
            book.progress += 10
        elif action == "decrease" and book.progress > 0:
            book.progress -= 10

        # Сохраняем изменения в базе данных
        db.session.commit()

    return redirect("/progress")

@app.route('/reports')
def reports_page():

    user = get_current_user()  # Получаем текущего пользователя
    if user is None:
        return redirect(url_for('login'))

    reports = Book.query.filter_by(whos=user.id).all()
    return render_template('reports.html', reports=reports, user=user)

@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['book-title']
        author = request.form['book-author']
        year = request.form['book-year']
        description = request.form['book-description']
        user = get_current_user().id
        new_book = Book(title=title, author=author, year=year, description=description, whos=user)
        db.session.add(new_book)
        db.session.commit()


        return redirect(url_for('books_page'))

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Хеширование пароля (рекомендуется использовать библиотеку werkzeug для этого)
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)

        # Создание нового пользователя
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Находим пользователя по email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):  # Проверка пароля
            session['user_id'] = user.id  # Сохраняем ID пользователя в сессии
            flash('Вы успешно вошли', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверный email или пароль', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем ID пользователя из сессии
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Проверяем и создаём базы данных
    create_database()

    # Инициализируем таблицы базы данных
    with app.app_context():
        db.create_all()

    app.run(debug=True)


@app.before_request
def check_login():
    """Проверка на наличие пользователя в сессии для доступа к защищенным страницам"""
    if 'user_id' not in session and request.endpoint not in ['login', 'registration']:
        return redirect(url_for('login'))
