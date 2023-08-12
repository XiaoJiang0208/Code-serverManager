from flask import *
#import sqlite3
webapp = Flask(__name__)


#webapp
#登录系统
@webapp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        print(request.form.get('username'))
        return redirect(url_for('login'))

#注册系统
@webapp.route('/signup/')
def rtsignup():
    return redirect('/signup/welcome')
@webapp.route('/signup/<msg>/', methods=['GET', 'POST'])
def signup(msg):
    if request.method=='GET':
        return render_template('signup.html',msg=msg)
    elif request.method=='POST':
        if request.form.get('password')!=request.form.get('confpassword'):
            return redirect('/login/密码不匹配!')
        return redirect(url_for('login'))
   

def adduser(username,password,pwoer):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)


if __name__ == "__main__":
    webapp.run(host='0.0.0.0',port=5000,debug=True)
    adduser("1","1","1")