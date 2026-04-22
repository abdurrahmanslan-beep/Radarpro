import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "yusuf_aslan_v39_final_boss_secure"

# Dosya ve DB Ayarları
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///radar_v39_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- AYARLAR ---
MY_IBAN = "TR49 0006 2001 0950 0006 6536 08"
MY_NAME = "ABDURRAHMAN ASLAN"
PRICE = "79 TL"
ADMIN_USER = "yusufadmin"
ADMIN_PASS = "v39_ozel"

# Tam liste senin istediğin gibi güncellendi
CAFES = {
    "nova": "Nova Coffee ✨", "luuq": "Luuq Coffee ☕", "vonal": "Vonal Coffee 🌟", 
    "laura": "Laura Coffee 🌸", "andalus": "Andalus Coffee 🕌", "florya": "Florya Coffee 🌿",
    "mavibeyaz": "Mavi Beyaz Coffee ⚓", "nomad": "Nomad Coffee ⛺", "tahtivan": "Tahtivan Coffee 🏰",
    "guzelbahce": "Güzelbahçe Coffee 🍃", "mackbear": "Mackbear Coffee 🐻"
}

# --- MODELLER ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10))
    full_name = db.Column(db.String(100), default="")
    birth_date = db.Column(db.String(20), default="")
    avatar = db.Column(db.String(200), default="https://cdn-icons-png.flaticon.com/512/149/149071.png")
    insta = db.Column(db.String(200), default="")
    is_premium = db.Column(db.Boolean, default=False)
    pay_status = db.Column(db.String(20), default="Yok")

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    cafe_id = db.Column(db.String(50))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username=ADMIN_USER).first():
        db.session.add(User(username=ADMIN_USER, password=ADMIN_PASS, full_name="Yusuf Admin", is_premium=True, gender="Erkek"))
        db.session.commit()

# TASARIM VE MOBİL AYARLARI
STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    :root { --gold: #ffd60a; --bg: #000; --card: #121212; --red: #ff4d4d; --gray: #222; }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { margin:0; background:var(--bg); color:white; font-family: -apple-system, sans-serif; text-align:center; overflow-x: hidden; }
    .container { padding: 15px; width: 100%; max-width: 500px; margin: auto; min-height: 100vh; }
    .card { background: var(--card); border-radius: 12px; padding: 16px; border: 1px solid #222; margin-bottom: 12px; text-align:left; transition: 0.2s; }
    .card:active { transform: scale(0.98); }
    .btn { background: var(--gold); color: black; border: none; padding: 14px; border-radius: 10px; width: 100%; font-weight: bold; cursor: pointer; text-decoration: none; display: block; text-align: center; font-size: 16px; }
    .btn-red { background: var(--red); color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; text-decoration: none; display: block; margin-top:15px; font-size: 14px;}
    .vip-btn { background: linear-gradient(45deg, #ff4d4d, #ffd60a); color: black; padding: 20px; border-radius: 15px; font-weight: 900; text-decoration: none; display: block; margin: 15px 0; border: 2px solid white; animation: pulse 1.5s infinite; font-size: 18px; }
    .input-pro { width: 100%; padding: 14px; background: #1a1a1a; border: 1px solid #333; color: white; border-radius: 10px; margin-bottom: 12px; font-size: 16px; outline: none; }
    @keyframes pulse { 0% {transform: scale(1.01);} 50% {transform: scale(1);} 100% {transform: scale(1.01);} }
    
    /* Modern Sohbet Ekranı */
    .chat-header { position: sticky; top: 0; background: var(--bg); padding: 10px 0; border-bottom: 1px solid var(--gray); margin-bottom: 10px; z-index: 10; display:flex; align-items:center; justify-content:center; }
    .chat-box { height: 65vh; overflow-y: auto; background: #080808; padding: 10px; border-radius: 10px; margin-bottom: 10px; display: flex; flex-direction: column; border: 1px solid #111; }
    .msg { padding: 10px 14px; border-radius: 18px; margin-bottom: 8px; max-width: 80%; font-size: 15px; line-height: 1.4; position: relative; }
    .sent { background: var(--gold); color: black; align-self: flex-end; border-bottom-right-radius: 4px; }
    .rcvd { background: #262626; color: white; align-self: flex-start; border-bottom-left-radius: 4px; }
    
    /* Profil Büyütme Modal */
    #modal { display: none; position: fixed; z-index: 99; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); align-items: center; justify-content: center; }
    #modal img { width: 90%; max-width: 400px; border-radius: 15px; border: 2px solid var(--gold); }
</style>

<script>
    window.onload = function() {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(function(position) {
                console.log("Konum Alındı");
            }, function(error) {
                console.log("İzin Verilmedi");
            });
        }
    };
    function showModal(src) { 
        document.getElementById('modalImg').src = src;
        document.getElementById('modal').style.display = 'flex';
    }
    function hideModal() { 
        document.getElementById('modal').style.display = 'none'; 
    }
</script>
"""

@app.route('/')
def home():
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    cafe_stats = {cid: {'k': sum(1 for c in CheckIn.query.filter_by(cafe_id=cid).all() if db.session.get(User, c.user_id) and db.session.get(User, c.user_id).gender == 'Kadın'),
                        'e': sum(1 for c in CheckIn.query.filter_by(cafe_id=cid).all() if db.session.get(User, c.user_id) and db.session.get(User, c.user_id).gender == 'Erkek')} for cid in CAFES}
    
    admin_btn = "<a href='/admin' style='color:cyan; font-size:14px; margin-right:15px; text-decoration:none;'>⚙️</a>" if u.username == ADMIN_USER else ""
    msg_btn = f"<a href='/mesajlar' style='text-decoration:none; font-size:24px; margin-right:15px;'>💬</a>"

    return render_template_string(f"<html><head>{STYLE}</head><body>"
        "<div id='modal' onclick='hideModal()'><img id='modalImg' src=''></div>"
        "<div class='container'>"
        "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>"
        "<h1 style='color:var(--gold); margin:0; font-size:24px;'>RADAR PRO</h1>"
        "<div style='display:flex; align-items:center;'>" + admin_btn + msg_btn + f" <a href='/profil'><img src='{u.avatar}' style='width:42px; height:42px; border-radius:50%; border:2px solid var(--gold); object-fit:cover;'></a></div></div>"
        
        "{% if not u.is_premium %}"
        f"<a href='/odeme' class='vip-btn'>💎 VIP OL: {PRICE} 💎</a>"
        "{% endif %}"
        
        "{% for cid, name in cafes.items() %}"
        "<div class='card' onclick=\"location.href='/mekan/{{cid}}'\" style='display:flex; justify-content:space-between; align-items:center;'>"
        "<div><b style='font-size:18px;'>{{name}}</b><div style='margin-top:5px; font-size:13px;'><span style='color:#ff4d94;'>👩 {{stats[cid]['k']}}</span> | <span style='color:#4d94ff;'>👨 {{stats[cid]['e']}}</span></div></div>"
        "<span style='color:var(--gold); font-size:20px;'>→</span></div>{% endfor %}"
        "<a href='/logout' class='btn-red'>ÇIKIŞ YAP</a></div></body></html>", u=u, cafes=CAFES, stats=cafe_stats)

@app.route('/mesajlar')
def mesajlar():
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if not u.is_premium: return redirect(url_for('odeme'))
    all_msgs = Message.query.filter(or_(Message.sender_id == u.id, Message.receiver_id == u.id)).order_by(Message.timestamp.desc()).all()
    chat_partners = {}
    for m in all_msgs:
        partner_id = m.receiver_id if m.sender_id == u.id else m.sender_id
        if partner_id not in chat_partners:
            partner = db.session.get(User, partner_id)
            if partner: chat_partners[partner_id] = {'user': partner, 'last_msg': m.content[:35]}

    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'><h3>MESAJLAR</h3>"
        "{% for pid, data in partners.items() %}"
        "<div class='card' onclick=\"location.href='/chat/{{pid}}'\" style='display:flex; align-items:center;'>"
        "<img src='{{data.user.avatar}}' onclick='event.stopPropagation(); showModal(this.src)' style='width:50px; height:50px; border-radius:50%; margin-right:15px; border:1px solid var(--gold); object-fit:cover;'>"
        "<div><b>{{data.user.full_name or data.user.username}}</b><br><small style='color:#aaa;'>{{data.last_msg}}...</small></div></div>"
        "{% else %}<p style='color:#666;'>Henüz mesajınız yok.</p>{% endfor %}"
        "<a href='/' class='btn' style='margin-top:20px; background:#333; color:white;'>ANASAYFA</a></div></body></html>", partners=chat_partners)

@app.route('/mekan/<cid>')
def mekan(cid):
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if not u.is_premium: return redirect(url_for('odeme'))
    people = [db.session.get(User, c.user_id) for c in CheckIn.query.filter_by(cafe_id=cid).all() if db.session.get(User, c.user_id)]
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'>"
        "<div id='modal' onclick='hideModal()'><img id='modalImg' src=''></div>"
        f"<h3>{CAFES[cid]}</h3><a href='/checkin/{cid}' class='btn' style='margin-bottom:20px;'>📍 BURADAYIM</a>"
        "{% for p in people %}"
        "<div class='card' onclick=\"location.href='/chat/{{p.id}}'\" style='display:flex; align-items:center;'>"
        "<img src='{{p.avatar}}' onclick='event.stopPropagation(); showModal(this.src)' style='width:55px; height:55px; border-radius:50%; margin-right:15px; border:1px solid var(--gold); object-fit:cover;'>"
        "<div><b style='font-size:16px;'>{{p.full_name or p.username}}</b><br><small style='color:#aaa;'>{{p.birth_date}} | @{{p.insta}}</small></div></div>{% endfor %}"
        "<a href='/' style='display:block; margin-top:20px; color:white;'>← Geri Dön</a></div></body></html>", people=people)

@app.route('/chat/<int:rid>', methods=['GET', 'POST'])
def chat(rid):
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if not u.is_premium: return redirect(url_for('odeme'))
    receiver = db.session.get(User, rid)
    if request.method == 'POST':
        db.session.add(Message(sender_id=u.id, receiver_id=rid, content=request.form['msg'])); db.session.commit()
    msgs = Message.query.filter(or_( (Message.sender_id==u.id) & (Message.receiver_id==rid), (Message.sender_id==rid) & (Message.receiver_id==u.id) )).order_by(Message.timestamp).all()
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'>"
        "<div class='chat-header'><b>{{r.full_name or r.username}}</b></div>"
        "<div class='chat-box' id='chatBox'>{% for m in msgs %}<div class='msg {{ \"sent\" if m.sender_id == uid else \"rcvd\" }}'>{{m.content}}</div>{% endfor %}</div>"
        "<form method='POST' style='display:flex; gap:8px;'><input name='msg' class='input-pro' placeholder='Mesajınızı yazın...' required autocomplete='off'><button class='btn' style='width:90px;'>OK</button></form>"
        "<a href='/mesajlar' style='color:#888; display:block; margin-top:10px;'>Kapat</a>"
        "<script>var c=document.getElementById('chatBox'); c.scrollTop=c.scrollHeight;</script></div></body></html>", msgs=msgs, uid=u.id, r=receiver)

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if request.method == 'POST':
        u.full_name, u.insta, u.birth_date = request.form['full_name'], request.form['insta'], request.form['birth_date']
        if 'photo' in request.files and request.files['photo'].filename:
            f = request.files['photo']; fname = secure_filename(f"u{u.id}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname)); u.avatar = "/static/uploads/" + fname
        db.session.commit(); return redirect(url_for('home'))
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'><h2>PROFİLİM</h2>"
        f"<div class='card'><form method='POST' enctype='multipart/form-data' style='text-align:center;'>"
        f"<img src='{u.avatar}' style='width:100px; height:100px; border-radius:50%; margin-bottom:15px; border:2px solid var(--gold); object-fit:cover;'>"
        "<input type='file' name='photo' class='input-pro'>"
        f"<input name='full_name' value='{u.full_name}' class='input-pro' placeholder='Ad Soyad'>"
        f"<input name='birth_date' value='{u.birth_date}' class='input-pro' placeholder='Doğum Yılı'>"
        f"<input name='insta' value='{u.insta}' class='input-pro' placeholder='Instagram'>"
        "<button class='btn'>KAYDET</button></form></div>"
        "<a href='/' style='color:#888;'>İptal</a></div></body></html>")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['u'], password=request.form['p']).first()
        if u: session["uid"] = u.id; return redirect(url_for('home'))
        else: return "Hatalı Giriş! <a href='/login'>Tekrar Dene</a>"
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container' style='display:flex; flex-direction:column; justify-content:center;'>"
        "<h1 style='color:var(--gold); font-size:40px; margin-bottom:30px;'>RADAR</h1>"
        "<div class='card'><form method='POST'><input name='u' class='input-pro' placeholder='Kullanıcı Adı'><input name='p' type='password' class='input-pro' placeholder='Şifre'>"
        "<button class='btn'>GİRİŞ YAP</button></form></div>"
        "<a href='/reg' style='color:#888; text-decoration:none; margin-top:15px;'>Kaydol</a></div></body></html>")

@app.route('/reg', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['u'] == ADMIN_USER: return "Geçersiz kullanıcı adı!"
        db.session.add(User(username=request.form['u'], password=request.form['p'], gender=request.form['g'])); db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'><h2>KAYIT</h2>"
        "<div class='card'><form method='POST'><input name='u' class='input-pro' placeholder='Kullanıcı Adı'><input name='p' type='password' class='input-pro' placeholder='Şifre'>"
        "<select name='g' class='input-pro'><option value='Erkek'>Erkek</option><option value='Kadın'>Kadın</option></select>"
        "<button class='btn'>KAYDOL</button></form></div></div></body></html>")

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/odeme', methods=['GET', 'POST'])
def odeme():
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if request.method == 'POST':
        u.pay_status = "Beklemede"; db.session.commit()
        return "Bildirim Yusuf Admin'e iletildi! <a href='/'>Dön</a>"
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'><div class='card'><h2>💎 VIP</h2>"
        f"<p>Ücret: {PRICE}</p><div style='border:1px dashed var(--gold); padding:20px;'><b>{MY_NAME}</b><br>{MY_IBAN}</div>"
        "<form method='POST' style='margin-top:15px;'><button class='btn'>ÖDEDİM ✅</button></form></div></div></body></html>")

@app.route('/admin')
def admin():
    if "uid" not in session: return redirect(url_for('login'))
    u = db.session.get(User, session["uid"])
    if u.username != ADMIN_USER: return "Yetkisiz!"
    bekleyenler = User.query.filter_by(pay_status="Beklemede").all()
    return render_template_string(f"<html><head>{STYLE}</head><body><div class='container'><h2>ADMİN</h2>"
        "{% for b in bekleyenler %}<div class='card'><b>{{b.username}}</b><br><a href='/admin/onay/{{b.id}}' class='btn'>ONAYLA</a></div>{% endfor %}"
        "<a href='/' style='color:white;'>←</a></div></body></html>", bekleyenler=bekleyenler)

@app.route('/admin/onay/<int:uid>')
def onay(uid):
    u = db.session.get(User, session.get("uid"))
    if u and u.username == ADMIN_USER:
        user = db.session.get(User, uid); user.is_premium = True; user.pay_status = "Onaylandı"; db.session.commit()
    return redirect(url_for('admin'))

@app.route('/checkin/<cid>')
def do_checkin(cid):
    if "uid" not in session or not db.session.get(User, session["uid"]).is_premium: return redirect(url_for('odeme'))
    CheckIn.query.filter_by(user_id=session["uid"]).delete()
    db.session.add(CheckIn(user_id=session["uid"], cafe_id=cid)); db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

