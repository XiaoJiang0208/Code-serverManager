from flask import *
import json
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
@webapp.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html',msg="")
    elif request.method=='POST':
        if request.form.get('password')!=request.form.get('confpassword'):
            return render_template('signup.html',msg="密码不匹配！")
        
   

def adduser(username,password,pwoer):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)


if __name__ == "__main__":
    webapp.run(host='0.0.0.0',port=5000,debug=True)
    adduser("1","1","1")