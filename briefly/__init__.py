# -*- coding: utf-8 -*-
import uuid
from flask import Flask, render_template, flash, request, redirect, url_for, current_app, jsonify, escape, make_response, g
from briefly.email import send_async_email
from threading import Thread
from flask_redis import FlaskRedis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging.handlers as handlers
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


redis_client = FlaskRedis()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    from briefly.models.users import Users
    from briefly.models.authors import Authors

    redis_client.init_app(app)

    ch_file = handlers.RotatingFileHandler('logs/briefly.log', maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch_file.setFormatter(formatter)

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[],  # [count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
        headers_enabled=True,
        strategy='fixed-window-elastic-expiry'
    )
    limiter.logger.addHandler(ch_file)
    limiter.init_app(app)

    @limiter.request_filter
    def ip_whitelist():
        return request.remote_addr == "127.0.0.1"

    from briefly.api.v1 import endpoints as api_v1
    limiter.limit("20 per second")(api_v1.bp)
    app.register_blueprint(api_v1.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/api')
    def api():
        return render_template('api.html')

    @app.route('/reg', methods=['GET'])
    def reg():
        return render_template('reg.html', email=email)

    @app.route('/regme', methods=['POST'])
    @limiter.limit('5 per day')
    def regme():
        if request.method == 'POST' and request.form['emailaddress']:
            token = uuid.uuid4()
            email = request.form['emailaddress']
            ip = request.remote_addr

            if not email:
                message = 'E-mail is required.'
            else:
                is_user_present = Users.query.filter_by(user_email=email).first()
                if is_user_present is None:
                    new_user = Users(user_email=email, user_token=str(token), user_reg_ip=ip)
                    db.session.add(new_user)
                    db.session.commit()

                    message = 'Token was sent to your e-mail'
                    text_body = render_template('emails/new_user.txt', token=token)
                    Thread(target=send_async_email, args=(current_app._get_current_object(), email, text_body)).start()
                else:
                    message = 'E-mail is already registered.'

            flash(message)
            return redirect(url_for('reg'))

    @app.route('/authors/<letter>', methods=['GET'])
    @limiter.limit('100/second')
    def letter(letter):
        answer = {
            'status': False,
            'number_of_records': 0,
            'authors': []
        }
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
                   'Х', 'Ц', 'Ч', 'Ш', 'Э', 'Ю', 'Я']
        if len(letter) == 1 and letter in letters:
            answer['status'] = True
            sql = f'SELECT id, author_fullname, author_url ' \
                f'FROM authors ' \
                f'WHERE author_fullname ' \
                f'REGEXP "[а-яА-Я]+ [а-яА-Я]+ {letter}"'
            authors = Authors.query.from_statement(text(sql)).all()
            if authors:
                answer['number_of_records'] = len(authors)
                for author in authors:
                    answer['authors'].append({
                        'id': author.id,
                        'author_fullname': author.author_fullname,
                        'author_url': author.author_url
                    })

        return jsonify(answer), 200

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return make_response(jsonify(error="Too Many Requests"), 429)

    @app.errorhandler(400)
    def badrequest_handler(e):
        return make_response(jsonify(error="Bad Request"), 400)

    @app.errorhandler(405)
    def method_not_allowd_handler(e):
        return make_response(jsonify(error="Method Not Allowed"), 405)

    return app
