# Code-serverManager
### 为code-server实现了多用户和管理(测试平台:Ubuntu)


# 本项目还待完善慎重使用

# 安装教程
## 根据这个[教程](https://coder.com/docs/code-server/latest/install#debian-ubuntu)安装code-server
## 创建一个用户和目录来供示例使用
创建主目录供用户，使用这里以`/home/code-server`为例
```
sudo mkdir /home/code-server
```

创建用于管理的账户，这里以`webapp`为例
```
sudo groupadd webapp
sudo useradd -s /bin/bash -g webapp -d /home/code-server -m webapp
```
## 克隆并配置项目
拉取项目后打开配置文件`webapp.json`
```
git clone https://github.com/XiaoJiang0208/Code-serverManager.git
cd Code-serverManager
vim config/webapp.json
```
更具要求更改`webapp.json`
```
{
    "ip": "0.0.0.0:5000",  #web需要监听的地址
    "outip": "0.0.0.0:5000",  #外网地址或域名
    "code-server-port": "5002~5010",  #可分配给用户的端口范围，端口多少决定可同时使用用户的多少
    "user-dir": "/home/code-server-dir",  #刚刚创建的主目录,路径必须为绝对路径且末尾没“/”
    "user-group": "webapp",  #刚刚创建的用户组
    "keeptime": 10,  #保持时间，用户在关闭工作区后在保持之间内没有重连就会关闭服务(单位为分钟)
    "cansignup": "true"  #是否可以自行注册
}
```
## 启动！
首先得安装screen保持服务
```
sudo apt-get install screen
```
新建screen工作区并用`sudo`启动`Code-serverManager.py`
```
screen -S csm   #创建叫csm的工作区
sudo python3 Code-serverManager.py
#按快捷键Ctrl+a然后后按d退出工作区
```
## 后记
可以写个开机脚本或者注册个服务实现开机启动，但是你们自己研究我懒😊
注意`Code-serverManager.py`必须以管理员(需要创建和删除用户)启动

# 创建管理员
先登录`http://{url}/signup`注册账户
再修改`webapp/userdata.json`的`power`为`admin`

# 页面说明
```
http://{url}/login    登录页面
http://{url}/signup   注册页面
http://{url}/admin    管理页面(需要管理员权限)
http://{url}/main     主页面
```

# 待实现功能
> - [ ] 数据库存储数据
> - [ ] ...