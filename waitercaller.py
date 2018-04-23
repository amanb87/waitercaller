# /*
#  * @Author: aman.buttan 
#  * @Date: 2018-04-24 02:13:32 
#  * @Last Modified by:   aman.buttan 
#  * @Last Modified time: 2018-04-24 02:13:32 
#  */
from flask import Flask,render_template, redirect, url_for,request
from flask_login import LoginManager
from flask_login import login_required, login_user
from mockdbhelper import MockDBHelper as DBHelper
from user import User


DB = DBHelper()
app = Flask(__name__)
app.secret_key = 'PLM7rVfkgQDDSYo1dYZ1Ig=='
login_manager = LoginManager(app)

@app.route("/")
def home():
   return render_template("home.html")

@app.route("/login", methods=['POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_password = DB.get_user(email)
    if user_password and user_password == password:
        user = User(email)
        login_user(user)
        return redirect(url_for('account'))
    return home()

@app.route("/account")
@login_required
def account():
    return "You are logged in"

if __name__ == '__main__':
    app.run(port=5000, debug=True)