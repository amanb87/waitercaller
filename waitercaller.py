import hashlib  #ships by default with Python 2.6+
from flask import Flask,render_template, redirect, url_for,request
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user, current_user

from passwordhelper import PasswwordHelper
from forms import RegistrationForm
from forms import LoginForm, CreateTableForm
from user import User
# import config
from bitlyhelper import BitlyHelper
import datetime
import config

if config.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper


DB = DBHelper()
PH = PasswwordHelper()
BH = BitlyHelper()

app = Flask(__name__)
app.secret_key = 'xxxxxxx'
login_manager = LoginManager(app)

@app.route("/")
def home():
    registrationform = RegistrationForm()
    return render_template("home.html", loginform=LoginForm(), registrationform=registrationform)

@app.route("/login", methods=['POST'])
def login():
    form = LoginForm()
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data.encode(), stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user,remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("Email or password invalid.")
    return render_template("home.html", loginform=form, registrationform=RegistrationForm())
    
    # email = request.form.get("email")
    # password = request.form.get("password")
    # stored_user = DB.get_user(email)
    # if stored_user and PH.validate_password(password.encode(),stored_user['salt'],stored_user['hashed']):
    #     user = User(email)
    #     login_user(user, remember=True)                #add remember argument for persistent login session
    #     return redirect(url_for('account'))

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered.")
            return render_template("home.html", loginform=LoginForm(), registrationform=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data.encode() + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registration successful. Please log in.")
    return render_template("home.html", loginform=LoginForm(), registrationform=form)

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
    return render_template("account.html", createtableform=CreateTableForm(), tables=tables)

@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).total_seconds()
        mins, secs = divmod(deltaseconds, 60)
        req['wait_minutes'] = '%d:%d' % (mins, secs)
    return render_template("dashboard.html", requests=requests)

@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id = request.args.get("request_id")
    DB.delete_request(request_id)
    return redirect(url_for("dashboard"))

@app.route('/account/createtable',methods=['POST'])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = BH.shorten_url(config.base_url + "newrequest/" + str(tableid))
        DB.update_table(tableid, new_url)
        return redirect(url_for("account"))
    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))


@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get("tableid")
    DB.delete_table(tableid)
    return redirect(url_for('account'))

@app.route('/newrequest/<tid>')
def new_request(tid):
    DB.add_request(tid,datetime.datetime.now())
    return "Your request has been logged and a waiter will be with you shortly"


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
