from flask import *
import secrets
import datetime
import json
import os
import signal
import random
#import sqlite3
webapp = Flask(__name__)


#webapp
#登录系统
@webapp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        if checkuser(request.form.get('username'),request.form.get('password')):
            red=redirect(url_for('main'))
            red.set_cookie('username',request.form.get('username'))
            red.set_cookie('token',settoken(request.form.get('username')))
            return red
        return render_template('login.html',msg='用户名或密码错误！')

#注册系统
@webapp.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html',msg="")
    elif request.method=='POST':
        if adduser(request.form.get('username'),request.form.get('password'),'admin'):
            return render_template('signup.html',msg='注册成功!')
        return render_template('signup.html',msg='用户已存在!')

#主管理界面
@webapp.route('/main/',methods=['GET', 'POST'])
def main():
    if checktoken(request.cookies.get('username'),request.cookies.get('token')):
        return "test"
    return redirect(url_for('login'))

        

#用户数据操作
#添加用户
def adduser(username,password,pwoer):
    #添加数据
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            return 0
    data['users'].append({'username':username,'password':password,'pwoer':pwoer,'token':'','tokendate':''})
    with open('./config/userdata.json','w') as f:
        json.dump(data,f)
    #系统操作
    with open('./config/webapp.json','r') as f:
        data=json.load(f)
    os.system(f'useradd -s /bin/bash -g {data["user-group"]} -d {data["user-dir"]}/{username} -m {username}')
    return 1

#验证用户
def checkuser(username,password):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            if i['password']==password:
                return 1
    return 0

#生成用户token
def settoken(username):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    tk=secrets.token_urlsafe(32)
    t=datetime.datetime.now()
    t+=datetime.timedelta(days=7)
    tkt=t.strftime('%Y-%m-%d')
    for i in data['users']:
        if i['username']==username:
            i['token']=tk
            i['tokendate']=tkt
            break
    with open('./config/userdata.json','w') as f:
        json.dump(data,f)
    return tk

def checktoken(username,token):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            #判断token是否相同         验证token是否过期
            if i['token']==token and (datetime.datetime.strptime(i['tokendate'],'%Y-%m-%d')-datetime.datetime.now()).days>=0:
                return 1
    return 0
    
    

def done():
    pass
    #systemctl list-units --type=service --state=active | grep code-server
    
def startserver():
    status=os.popen('systemctl list-units --type=service --state=active | grep code-server').readlines()
    with open('./config/webapp.json','r') as f:
        setting=json.load(f)
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        for j in status:
            if j.split('@')[1].split('.')[0]==i['username']:
                break
            with open(f'{setting["user-dir"]}/{i["username"]}','w') as f:
                while True:
                    if len(usedport)>setting["user-port"].split('~')[1]-setting["user-port"].split('~')[0]:
                        return 0
                    p=random.randint(setting["user-port"].split('~')[0], setting["user-port"].split('~')[1])
                    if p not in usedport:
                        usedport.append(p)
                        break
                f.write(f'''
                    bind-addr: 0.0.0.0:{p}
                    auth: password
                    password: {i["password"]}
                    cert: false
                ''')
            os.popen(f'systemctl start code-server@{i["username"]}')
            

usedport=[]


if __name__ == "__main__":
    signal.signal(signal.SIGKILL, done)
    signal.signal(signal.SIGINT, done)
    webapp.run(host='0.0.0.0',port=5000,debug=True)