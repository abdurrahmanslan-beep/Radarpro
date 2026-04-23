from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tatvan_radar_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    is_private = db.Column(db.Boolean, default=False) # Profil Gizleme
    is_anonymous = db.Column(db.Boolean, default=False) # Anonim Mod

with app.app_context():
    db.create_all()
    # Veritabanını eksik sütunlara karşı tamir eder
    for column in ['is_private', 'is_anonymous']:
        try:
            db.session.execute(text(f"ALTER TABLE user ADD COLUMN {column} BOOLEAN DEFAULT 0"))
            db.session.commit()
        except:
            db.session.rollback()

@app.route('/')
def ana_sayfa():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return '<h1>Tatvan Radar</h1><p>Lütfen giriş yapın.</p><a href="/login">Giriş Yap</a>'

# Profil Gizleme ve Anonim Modu Tetikleyen Fonksiyon
@app.route('/ayarlari-guncelle', methods=['POST'])
def ayarlari_guncelle():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Formdan gelen veriye göre modları değiştiriyoruz
        mod = request.form.get('mod')
        if mod == 'gizlilik':
            user.is_private = not user.is_private
        elif mod == 'anonim':
            user.is_anonymous = not user.is_anonymous
        db.session.commit()
    return redirect(url_for('ana_sayfa'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

