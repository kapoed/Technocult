import secrets
import sqlalchemy
from flask import Flask, render_template, redirect, flash, url_for, request, abort, current_app
from data.users import User
from data.questions import Question
from data.answers import Answer
from data.knowledge_entries import KnowledgeEntry
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms.registerform import RegistrationForm
from forms.loginform import LoginForm
from forms.questionform import QuestionForm
from forms.answerform import AnswerForm
from forms.knowledgeentryform import KnowledgeEntryForm
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markdown import markdown
import os
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER_QUESTIONS'] = 'static/uploads/questions'
app.config['UPLOAD_FOLDER_ANSWERS'] = 'static/uploads/answers'
app.config['UPLOAD_FOLDER_KNOWLEDGE'] = 'static/uploads/knowledge_entries'

for folder_key in ['UPLOAD_FOLDER_QUESTIONS', 'UPLOAD_FOLDER_ANSWERS', 'UPLOAD_FOLDER_KNOWLEDGE']:
    folder_path = app.config[folder_key]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

ADMIN_FILE = 'admins.txt'
VALID_ENTRY_TYPES = {
    'articles': 'Статьи',
    'instructions': 'Инструкции',
    'guides': 'Гайды'
}


@app.context_processor
def inject_valid_entry_types():
    return dict(VALID_ENTRY_TYPES=VALID_ENTRY_TYPES)


def get_admin_logins():
    if not os.path.exists(ADMIN_FILE):
        try:
            with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
                f.write("# Добавьте логины администраторов сюда, каждый с новой строки\n")
                f.write("admin\n")
            current_app.logger.info(f"Файл администраторов {ADMIN_FILE} создан с примером 'admin'.")
            return {"admin"}
        except IOError as e:
            current_app.logger.error(f"Не удалось создать файл администраторов {ADMIN_FILE}: {e}")
            return set()
    try:
        with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
            admins = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        current_app.logger.debug(f"Загруженные администраторы: {admins}")
        return admins
    except IOError as e:
        current_app.logger.error(f"Не удалось прочитать файл администраторов {ADMIN_FILE}: {e}")
        return set()
    except UnicodeDecodeError as e:
        current_app.logger.error(f"Ошибка кодировки при чтении файла {ADMIN_FILE}. Убедитесь, что он в UTF-8: {e}")
        return set()


def is_admin():
    if not current_user.is_authenticated:
        return False
    admin_logins = get_admin_logins()
    is_admin_result = current_user.login in admin_logins
    current_app.logger.debug(
        f"Проверка is_admin для {current_user.login}: {is_admin_result} (Список админов: {admin_logins})")
    return is_admin_result


@app.context_processor
def inject_is_admin_to_templates():
    return dict(is_admin=is_admin)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('knowledge_base_default'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User(login=form.login.data, email=form.email.data, hashed_password=generate_password_hash(form.password.data))
        db_sess.add(user)
        db_sess.commit()
        flash("Регистрация успешна. Теперь войдите.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('knowledge_base_default'))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('knowledge_base_default'))
        else:
            flash("Неверный логин или пароль.", "danger")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из системы.", "info")
    return redirect(url_for('knowledge_base_default'))


@app.route('/')
def knowledge_base_default():
    return redirect(url_for('view_knowledge_section', entry_type_slug='articles'))


@app.route('/knowledge/<entry_type_slug>')
def view_knowledge_section(entry_type_slug):
    if entry_type_slug not in VALID_ENTRY_TYPES: abort(404)
    db_sess = db_session.create_session()
    entries = db_sess.query(KnowledgeEntry).filter(KnowledgeEntry.entry_type == entry_type_slug).order_by(
        sqlalchemy.desc(KnowledgeEntry.created_date)).all()
    section_title = VALID_ENTRY_TYPES[entry_type_slug]
    return render_template('knowledge_base.html', title=section_title, entries=entries, section_title=section_title,
                           current_entry_type_slug=entry_type_slug)


@app.route('/knowledge/add/<entry_type_slug>', methods=['GET', 'POST'])
@login_required
def add_knowledge_entry(entry_type_slug):
    if not is_admin():
        flash("У вас нет прав для добавления записей.", "danger")
        return redirect(url_for('view_knowledge_section', entry_type_slug=entry_type_slug))
    if entry_type_slug not in VALID_ENTRY_TYPES: abort(404)
    form = KnowledgeEntryForm()
    if request.method == 'GET': form.entry_type.data = entry_type_slug
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        image_file = form.main_image.data
        filename = secure_filename(image_file.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER_KNOWLEDGE'], unique_filename)
        try:
            image_file.save(image_path)
        except Exception as e:
            flash(f"Ошибка при сохранении основного изображения: {e}", "danger")
            return render_template('add_knowledge_entry.html',
                                   title=f"Добавить {VALID_ENTRY_TYPES.get(entry_type_slug, 'запись')}", form=form,
                                   current_entry_type_slug=entry_type_slug)
        new_entry = KnowledgeEntry(title=form.title.data, entry_type=form.entry_type.data,
                                   main_image_filename=unique_filename, content=form.content.data,
                                   user_id=current_user.id)
        db_sess.add(new_entry)
        db_sess.commit()
        flash(f"{VALID_ENTRY_TYPES.get(new_entry.entry_type, 'Запись')} '{new_entry.title}' успешно добавлена!",
              "success")
        # Перенаправляем на страницу просмотра только что созданной записи
        return redirect(url_for('view_knowledge_entry', entry_id=new_entry.id))
    human_readable_entry_type = VALID_ENTRY_TYPES.get(entry_type_slug, "запись")
    return render_template('add_knowledge_entry.html', title=f"Добавить {human_readable_entry_type}", form=form,
                           current_entry_type_slug=entry_type_slug)


@app.route('/knowledge/entry/<int:entry_id>')
def view_knowledge_entry(entry_id):
    db_sess = db_session.create_session()
    entry = db_sess.get(KnowledgeEntry, entry_id)
    if not entry:
        abort(404)

    # Преобразование Markdown в HTML
    html_content = markdown(entry.content, extensions=['fenced_code', 'tables', 'nl2br'])

    return render_template('view_knowledge_entry.html',
                           title=entry.title,
                           entry=entry,
                           html_content=html_content)


@app.route('/forum')
def forum_index():
    db_sess = db_session.create_session()
    search_query = request.args.get('search_query', '').strip()
    query_obj = db_sess.query(Question)
    if search_query: query_obj = query_obj.filter(Question.title.ilike(f'%{search_query}%'))
    questions_list = query_obj.order_by(sqlalchemy.desc(Question.created_date)).all()
    return render_template('forum.html', title='Форум - Главная', questions=questions_list, search_query=search_query)


@app.route('/create-question', methods=['GET', 'POST'])
@login_required
def create_question():
    form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_question = Question(title=form.title.data, content=form.content.data, user_id=current_user.id)
        if form.image.data:
            try:
                image_file = form.image.data
                filename = secure_filename(image_file.filename)
                if filename:
                    unique_filename = str(uuid.uuid4()) + "_" + filename
                    image_path = os.path.join(app.config['UPLOAD_FOLDER_QUESTIONS'], unique_filename)
                    image_file.save(image_path)
                    new_question.image_filename = unique_filename
                else:
                    new_question.image_filename = None
            except Exception as e:
                flash(f"Ошибка при загрузке файла для вопроса: {e}", "danger")
                return render_template(
                    'create_question.html', title='Задать новый вопрос', form=form)
        else:
            new_question.image_filename = None
        db_sess.add(new_question)
        db_sess.commit()
        flash('Ваш вопрос успешно опубликован!', 'success')
        return redirect(url_for('view_question', question_id=new_question.id))
    return render_template('create_question.html', title='Задать новый вопрос', form=form)


@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    db_sess = db_session.create_session()
    question = db_sess.get(Question, question_id)
    if not question: abort(404)
    answer_form = AnswerForm()
    if answer_form.validate_on_submit() and request.method == 'POST':
        if not current_user.is_authenticated: flash("Только авторизованные пользователи могут оставлять ответы.",
                                                    "warning"); return redirect(
            url_for('login', next=url_for('view_question', question_id=question_id)))
        new_answer = Answer(content=answer_form.content.data, user_id=current_user.id, question_id=question.id)
        if answer_form.image.data:
            try:
                image_file = answer_form.image.data
                filename = secure_filename(image_file.filename)
                if filename:
                    unique_filename = str(uuid.uuid4()) + "_" + filename
                    image_path = os.path.join(app.config['UPLOAD_FOLDER_ANSWERS'], unique_filename)
                    image_file.save(image_path)
                    new_answer.image_filename = unique_filename
                else:
                    new_answer.image_filename = None
            except Exception as e:
                flash(f"Ошибка при загрузке изображения для ответа: {e}", "danger"); new_answer.image_filename = None
        else:
            new_answer.image_filename = None
        db_sess.add(new_answer)
        db_sess.commit()
        flash('Ваш ответ успешно добавлен!', 'success')
        return redirect(url_for('view_question', question_id=question.id))
    return render_template('view_question.html', title=question.title, question=question, answer_form=answer_form)


if __name__ == '__main__':
    db_session.global_init("db/forum_app.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
