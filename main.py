#!/usr/bin/env python
from flask import Flask, url_for, render_template, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from db import init_db, get_db
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

import MySQLdb
import jinja2.exceptions

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)
init_db(app)
login_manager_app = LoginManager(app)
# login_manager.login_view = 'login'

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route('/')
@app.route('/index')
@login_required
def index():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM visitor')
    data = cur.fetchall()
    cur.close()
    if current_user.is_authenticated:
        redirect((url_for('index')))
    return render_template('index.html', data=data)

@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename+'.html')

# 회원가입 페이지
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼으로부터 입력받은 데이터 가져오기
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

         # 비밀번호 암호화
        hashed_password = generate_password_hash(password).decode('utf-8')

        # MySQL에 회원 정보 저장하기
        db = get_db()
        cur = db.cursor()
        sql = "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, hashed_password)
        cur.execute(sql, val)
        db.commit()
        cur.close()

        # 회원가입이 성공적으로 완료됨을 알리는 메시지 표시
        message = "Registration successful! Please log in."
        return render_template('login.html', message=message)

    # GET 요청인 경우 회원가입 양식을 표시
    return render_template('register.html')

# 로그인 기능
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # db = get_db()
        # cur = db.cursor()
        # if user:
        #     # 첫 번째 사용자 선택
        #     if user.password:
        #         login_user(user)
        #         print('login success!')
        #         # 로그인 성공
        #         return redirect(url_for('index'))
        #     else:
        #         # 비밀번호가 일치하지 않는 경우
        #         error = 'Invalid email or password'
        #         return render_template('login.html', error=error)
        # else:
        #     flash("User not found...")
        #     return render_template('login.html')
        return render_template('login.html')
    else:
        # 해당 이메일로 등록된 사용자가 없는 경우
        error = 'Invalid email or password'
        return render_template('login.html', error=error)

# 로그아웃 페이지
@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('logout success!')
    return redirect(url_for('login'))

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    # csrf.init_app(app)
    app.run(debug=True)
