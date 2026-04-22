is_private = db.Column(db.Boolean, default=False)
@app.route('/gizlilik-ayari', methods=['POST'])
def gizlilik_ayari():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.is_private = not user.is_private  # True ise False, False ise True yapar
        db.session.commit()
    return redirect(url_for('profil')) # Profil sayfana geri döner
<form action="/gizlilik-ayari" method="POST">
    <button type="submit" style="padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 5px;">
        {% if user.is_private %}
            Profilimi Herkese Aç
        {% else %}
            Profilimi Gizle (Görünmez Ol)
        {% endif %}
    </button>
</form>
# Sadece gizli olmayanları (is_private=False) getirir
aktif_kullanicilar = User.query.filter_by(is_private=False).all()

