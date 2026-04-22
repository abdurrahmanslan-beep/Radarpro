from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tatvan2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    is_private = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN is_private BOOLEAN DEFAULT 0"))
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/')
def ana_sayfa():
    # Kim giriş yapmışsa onun profilini, kimse yoksa ilk kullanıcıyı göster (test için)
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else User.query.first()
    
    if user:
        return render_template('index.html', user=user)
    return "<h1>Tatvan Radar</h1><p>Kullanıcı bulunamadı, lütfen kayıt olun.</p>"

@app.route('/gizlilik-degistir', methods=['POST'])
def gizlilik_degistir():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else User.query.first()
    
    if user:
        user.is_private = not user.is_private
        db.session.commit()
    return redirect(url_for('ana_sayfa'))

if __name__ == '__main__':
    app.run(debug=True)

