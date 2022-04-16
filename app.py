from flask import Flask,url_for,render_template,session,redirect,request
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import sha256
from configparser import ConfigParser
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

parser = ConfigParser()
parser.read('config.ini')


app = Flask(__name__)
app.secret_key = parser.get('APP','SECRET_KEY')
oauth = OAuth(app)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = parser.get('APP','SQLALCHEMY_DATABASE_URI')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024


db = SQLAlchemy(app)

admin = Admin(app)


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    questions_solved = db.Column(db.Integer)
    last_action = db.Column(db.DateTime,default = datetime.now)

class Answers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    question_number = db.Column(db.Integer)
    answer = db.Column(db.String(64))

class Leaderboard(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    questions_solved = db.Column(db.Integer)

google = oauth.register(
    name='google',
    client_id=parser.get('GOOGLE','CLIENT_ID'),
    client_secret=parser.get('GOOGLE','CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

def updatedaleaderboardkek():
    user_list = [[user.name,user.email,user.questions_solved,user.last_action] for user in User.query.all()]
    sorted_list = sorted(user_list,key=lambda x: (x[2]),reverse=True)
    num_list = []
    for i in sorted_list:
        if(i[2] not in num_list):
            num_list.append(i[2])
    final_list=[]
    for i in num_list:
        temp_list = []
        for j in sorted_list:
            if(j[2]==i):
                temp_list.append(j)
        sorted_temp = sorted(temp_list,key = lambda x: (x[3]))
        for j in sorted_temp:
            final_list.append(j)
    x=Leaderboard.query.delete()
    db.session.commit()
    final_list=final_list[0:10]
    for x in final_list:
        user_obj = Leaderboard(name=x[0],email=x[1],questions_solved=x[2])
        db.session.add(user_obj)
        db.session.commit()
    return True

@app.route('/update_leaderboard')
def updateboard():
   updatedaleaderboardkek()
   return "doen"

@app.route('/leaderboard')
def leaderboard():
    user_list = Leaderboard.query.all()
    return render_template('leaderboard.html',user_list=user_list)




@app.route('/')
def home():
    if "email" in session:
        return redirect('/challenges')
    else:
        return render_template('landing.html')


""" Challenges screen that renders the questions and validates answers """

@app.route('/challenges',methods=['POST','GET'])
def challenges():
    if 'email' not in session:
        return redirect('/')
    else:
        if request.method == "POST":
            user = User.query.filter_by(email = session['email']).first()         
            answer = sha256(request.form['ans'].encode(encoding='utf-8',errors='replace')).hexdigest()
            print(answer)
            if answer == Answers.query.filter_by(question_number = user.questions_solved+1).first().answer:
                user.questions_solved+=1
                user.last_action = datetime.now()
                db.session.commit()
                updatedaleaderboardkek()
                return render_template('yay.html')
        
        user = User.query.filter_by(email = session['email']).first()
        template = str(user.questions_solved + 1) + '.html'
        if user.questions_solved >= 8:
            return render_template('yayfinal.html')

    return render_template(template,email = user.email)

# OAUTH LOGIN

@app.route('/login')
def login():
    if 'email' in session:
        return redirect('/challenges')
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)



# OAUTH AUTH CALLBACK
@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    # do something with the token and profile
    registration_check = User.query.filter_by(email = user_info['email']).first()
    if registration_check:
        session['email'] = user_info['email']
        return redirect('/')
    else:
        user = User(
            name=user_info['name'],
            email = user_info['email'],
            questions_solved=0
        )
        db.session.add(user)
        db.session.commit()
        session['email'] = user_info['email']
        return redirect('/')


@app.route('/VeryPremiumAntivirus',methods=['POST','GET'])
def VeryPremiumAntivirus():
    if request.method=='POST':
        if request.form['productKey'] == 'TX9XD-98N7V-6WMQ6-BX7FG-H8Q99':
            return render_template('virusCleaned.html')
    return render_template('virus.html')

@app.route('/TheAlphaConsipracy')
def TheAlphaConsipracy():
    cheat = request.args.get('cheat').lower().replace(' ','')
    if cheat == 'XYZZY'.lower():
        return render_template('aka.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


"""
-------------------Admin Panel---------------------
"""
        

class AbstruseAdminView(ModelView):
    def is_accessible(self):
        admins_list=parser.get('APP','ADMINS')
        if 'email' in session:
            if session['email'] in admins_list:
                return True
            else:
                return False
        else:
            return False



admin.add_view(AbstruseAdminView(User,db.session))
admin.add_view(AbstruseAdminView(Leaderboard,db.session))
admin.add_view(AbstruseAdminView(Answers,db.session))


if __name__ == "__main__":
    app.run(debug=True)
