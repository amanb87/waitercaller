import hashlib  #ships by default with Python 2.6+
from flask import Flask,render_template, redirect, url_for,request
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user, current_user
from mockdbhelper import MockDBHelper as DBHelper
from passwordhelper import PasswwordHelper
from user import User
import config
from bitlyhelper import BitlyHelper



DB = DBHelper()
PH = PasswwordHelper()
BH = BitlyHelper()

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
    stored_user = DB.get_user(email)
    if stored_user and PH.validate_password(password.encode(),stored_user['salt'],stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True)                #add remember argument for persistent login session
        return redirect(url_for('account'))
    return home()

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get("email")
    pw1 = request.form.get("password")
    pw2 = request.form.get("password2")
    if not pw1 == pw2:
        return redirect(url_for('home'))
    if DB.get_user(email):
        return redirect(url_for('home'))
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1.encode() + salt)
    DB.add_user(email, salt, hashed)
    return redirect(url_for('home'))

"""The decorator below indicates to Flask-Login that this is the function we want to use to handle users who already have a cookie assigned, 
  and it'll pass the user_id variable from the cookie to this function whenever a user visits our site, which already has one."""

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)

@app.route("/account")
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html",tables=tables)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/account/createtable',methods=['POST'])
@login_required
def account_createtable():
    tablename = request.form.get("tablenumber")
    tableid = DB.add_table(tablename, current_user.get_id())
    new_url = BH.shorten_url(config.base_url + "newrequest/" + tableid)
    DB.update_table(tableid,new_url)
    return redirect(url_for('account'))

@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get("tableid")
    DB.delete_table(tableid)
    return redirect(url_for('account'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)