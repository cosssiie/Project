from datetime import timezone, datetime
from sqlite3 import IntegrityError
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

from .models import User
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/api/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Please provide all required fields.'}), 400

    if not email.endswith('@ukma.edu.ua'):
        return jsonify({'error': 'Only ukma.edu.ua emails are allowed.'}), 400

    # Хешуємо пароль
    hashed_password = generate_password_hash(password)

    # Створюємо нового користувача
    new_user = User(username=username, email=email, password=hashed_password, bio=None)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration successful!'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User with this email or username already exists.'}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@auth.route('/api/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        # Якщо хтось хоче зайти на цю сторінку GET — повернути повідомлення
        return jsonify({'message': 'Login via POST'}), 401

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True, 'user_id': user.id}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@auth.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200