from flask import *
import secrets
import datetime
import json
import os
#import signal
import random
#import sqlite3
import asyncio
import websockets
import time
from multiprocessing import Process


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
    global setting
    if setting['cansignup']=='true':
        if request.method=='GET':
            return render_template('signup.html',msg="")
        elif request.method=='POST':
            if adduser(request.form.get('username'),request.form.get('password'),'user'):
                return render_template('signup.html',msg='注册成功!')
            return render_template('signup.html',msg='用户已存在!')
    return redirect(url_for('login'))

#主界面
@webapp.route('/main/',methods=['GET', 'POST'])
def main():
    global setting
    if checktoken(request.cookies.get('username'),request.cookies.get('token')):
        p=startserver(request.cookies.get('username'))#启动服务
        if p:
            return render_template('main.html',URL='http://'+setting['outip'].split(':')[0]+':'+p,ip=setting['outip'],wsip=setting['outip'].split(':')[0]+':'+str(int(setting['outip'].split(':')[1])+1))
        return '启动服务失败'
    return redirect(url_for('login'))

#管理界面
@webapp.route('/admin/',methods=['GET', 'POST'])
def admin():
    if request.method=='GET':
        if checktoken(request.cookies.get('username'),request.cookies.get('token')):
            if isadmin(request.cookies.get('username')):
                return render_template('admin.html')
            return redirect(url_for('main'))
        return redirect(url_for('login'))
    elif request.method=='POST':
        if request.form.get('model') == 'signup':#注册
            if adduser(request.form.get('username'),request.form.get('password'),'user'):
                return render_template('admin.html',msg='注册成功!')
            return render_template('admin.html',msg='用户已存在!')
        if request.form.get('model') == 'deluser':#用户删除
            if deluser(request.form.get('username')):
                return render_template('admin.html',msg='删除成功!')
            return render_template('admin.html',msg='删除失败!')
        if request.form.get('model') == 'changepower':#更改用户权限
            if cgadmin(request.form.get('username'),request.form.get('power')):
                return render_template('admin.html',msg='修改成功!')
            return render_template('admin.html',msg='修改失败!')
        if request.form.get('model') == 'cansignup':#更改是否可以自行注册
            global setting
            setting['cansignup']=request.form.get('can')
            with open('./config/webapp.json','w') as f:
                json.dump(setting,f)
            return render_template('admin.html',msg='修改完成!')
        return redirect(url_for('admin'))



#用户数据操作
#添加用户
def adduser(username,password,power):
    #添加数据
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            return 0
    data['users'].append({'username':username,'password':password,'power':power,'token':'','tokendate':''})
    with open('./config/userdata.json','w') as f:
        json.dump(data,f)
    #系统操作
    with open('./config/webapp.json','r') as f:
        data=json.load(f)
    os.system(f'sudo -u webapp mkdir {data["user-dir"]}/{username}')
    os.system(f'useradd -s /bin/bash -g {data["user-group"]} -d {data["user-dir"]}/{username} -m {username}')
    os.system(f'chown -R {username}:{data["user-group"]} {data["user-dir"]}/{username}')
    return 1

#删除用户
def deluser(username):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            data['users'].remove(i)
            os.system(f'userdel -r {username}')
            return 1
    with open('./config/userdata.json','w') as f:
        json.dump(data,f)
    return 0

#验证用户是否为管理员
def isadmin(username):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            if i['power']=='admin':
                return 1
    return 0

#设置管理员
def cgadmin(username,power):
    with open('./config/userdata.json','r') as f:
        data=json.load(f)
    for i in data['users']:
        if i['username']==username:
            i['power']=power
            break
        return 0
    with open('./config/userdata.json','w') as f:
        json.dump(data,f)
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
    
    

def stopallserver():
    status=os.popen('systemctl list-units --type=service --state=active | grep code-server').readlines()
    print('EXIT!')
    for s in status:
        os.popen(f'sudo systemctl stop code-server@{s.split("@")[1].split(".")[0]}')
    #systemctl list-units --type=service --state=active | grep code-server
    
def stopserver(username):
    os.popen(f'sudo systemctl stop code-server@{username}')

def startserver(username):
    '''启动code-server服务,输入用户名,输出使用的端口,如当前用户的服务已启用直接返回在使用的端口'''
    status=os.popen('sudo systemctl list-units --type=service --state=active | grep code-server').readlines()
    for j in status:
        if j.split('@')[1].split('.')[0]==username:
            with open(f'{setting["user-dir"]}/{username}/.config/code-server/config.yaml','r') as f:
                port=f.readlines()
                for i in port:
                    if 'bind-addr' in i:
                        return i.split(':')[2]
                return 0
    os.system(f'sudo -u webapp mkdir -p {setting["user-dir"]}/{username}/.config/code-server')
    with open(f'{setting["user-dir"]}/{username}/.config/code-server/config.yaml','w+') as of:
        while True: #抽一个端口
            if len(usedport)>=int(setting["code-server-port"].split('~')[1])-int(setting["code-server-port"].split('~')[0]):
                return 0
            p=random.randint(int(setting["code-server-port"].split('~')[0]), int(setting["code-server-port"].split('~')[1]))
            if p not in usedport:
                usedport.append(p)
                break
        with open('./config/userdata.json','r') as inf:
            data=json.load(inf)
        for i in data['users']:
            if i['username']==username:
                password=i['password']
                break
        of.write(f'bind-addr: 0.0.0.0:{p}\nauth: password\npassword: {password}\ncert: false')
    os.popen(f'sudo systemctl start code-server@{username}')
    return str(p)


#利用ws实现用户保持
async def echo(websocket, path):
    async for message in websocket:
        global setting
        username=message.split('!')[1]
        #print(message)
        #message = "I got your message: {}".format(message)
        #await websocket.send(message)
        ot=time.time()
        while 'keep!' in message:
            if time.time()-ot>=setting['keeptime']*60:
                ot=time.time()
                await websocket.send("keep?")
                break
    stopserver(username)


if __name__ == "__main__":
    global setting #服务设置
    global usedport #已使用的端口
    usedport=[]
    #global onlineuser #在线用户
    onlineuser=[]
    with open('./config/webapp.json','r') as f:
        setting=json.load(f)
    def ws():
        asyncio.get_event_loop().run_until_complete(websockets.serve(echo, setting['ip'].split(':')[0], int(setting['ip'].split(':')[1])+1))
        asyncio.get_event_loop().run_forever()
    p=Process(target=ws)
    p.start()
    webapp.run(host=setting['ip'].split(':')[0],port=setting['ip'].split(':')[1])
    p.close
    stopallserver()
    #signal.signal(signal.SIGTERM, stop)
    #signal.signal(signal.SIGINT, stop)