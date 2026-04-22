from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cok-gizli-anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_private = db.Column(db.Boolean, default=False) # Gizlilik sütunu burada

# Veritabanını otomatik güncelleme/oluşturma
with app.app_context():
    db.create_all()
    # Eğer sütun yoksa zorla ekle
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN is_private BOOLEAN DEFAULT 0"))
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/')
def ana_sayfa():
    return "Tatvan Radar Çalışıyor! /profil sayfasına git."

@app.route('/profil')
def profil():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profil.html', user=user)
    return "Giriş yapmalısınız."

@app.route('/gizle', methods=['POST'])
def gizle():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.is_private = not user.is_private
        db.session.commit()
    return redirect(url_for('profil'))

if __name__ == '__main__':
    app.run(debug=True)

