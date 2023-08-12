from flask import *
#import sqlite3
webapp = Flask(__name__, static_url_path='', static_folder='templates', template_folder='templates')



#webapp
@webapp.route('/login/')
def login():
    return render_template('login.html')

@webapp.route("/api/login/",methods=['POST'])
def apilogin():
    print(request.form.get('username'))
    return redirect(url_for('login'))

@webapp.route('/signup/<msg>')
def test(msg):
    return render_template('signup.html',msg=msg)
    
if __name__ == "__main__":
    webapp.run(host='0.0.0.0',port=5000,debug=True)