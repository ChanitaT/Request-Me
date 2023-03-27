import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import datetime

 
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///requestme.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash('Unauthorized, Please login','warning')
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
# -------------------------------------------------Index-------------------------------------------------
@app.route("/")
@login_required
def index():

    user_id = session["user_id"]
    emails = db.execute("SELECT email FROM userinfo WHERE id = ?", user_id)
    email = emails[0]["email"]
    userinfo = db.execute("SELECT username, name, surname, email FROM userinfo WHERE id = ?", user_id)
    summarybypriority = db.execute("SELECT priority, count(no) FROM requestmeinfo WHERE toemail Like ? GROUP BY priority", "%" + email + "%")
    complete_count = db.execute("SELECT count(no) cp FROM requestmeinfo WHERE status='COMPLETED' AND toemail Like?", "%" + email + "%")
    totaltask_count = db.execute("SELECT count(*) tt FROM requestmeinfo WHERE toemail Like ?", "%" + email + "%")

    cp_count = int(complete_count[0]["cp"])
    tt_count = int(totaltask_count[0]["tt"])
    if not tt_count:
        tt_count = 1
    percent_complete = round(cp_count*100/tt_count, 2)

    fyi = db.execute("SELECT count(no) fyi FROM requestmeinfo WHERE priority='FYI' AND toemail Like ? GROUP BY priority", "%" + email + "%")
    low = db.execute("SELECT count(no) low FROM requestmeinfo WHERE priority='Low' AND toemail Like ? GROUP BY priority", "%" + email + "%")
    medium = db.execute("SELECT count(no) medium FROM requestmeinfo WHERE priority='Medium' AND toemail Like ? GROUP BY priority", "%" + email + "%")
    high = db.execute("SELECT count(no) high FROM requestmeinfo WHERE priority='High' AND toemail Like ? GROUP BY priority", "%" + email + "%")
    emergency = db.execute("SELECT count(no) emergency FROM requestmeinfo WHERE priority='Emergency' AND toemail Like ? GROUP BY priority", "%" + email + "%")

    if not fyi:
        fyi=0
    else:
        fyi = int(fyi[0]["fyi"])
    if not low:
        low=0
    else:
        low = int(low[0]["low"])
    if not medium:
        medium=0
    else:
        medium = int(medium[0]["medium"])
    if not high:
        high=0
    else:
        high = int(high[0]["high"])
    if not emergency:
        emergency=0
    else:
        emergency = int(emergency[0]["emergency"]) 

    fyi_p = round(fyi*100/tt_count, 2)
    low_p = round(low*100/tt_count, 2)
    medium_p = round(medium*100/tt_count, 2)
    high_p = round(high*100/tt_count, 2)
    emergency_p = round(emergency*100/tt_count, 2)

    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)

    next7days = db.execute("SELECT * FROM requestmeinfo WHERE duedate between CURRENT_DATE and ? AND toemail Like ? ORDER BY duedate", next_week, "%" + email + "%")

    return render_template("index.html", userinfo=userinfo,
                                        summarybypriority=summarybypriority,
                                        percent_complete=percent_complete,
                                        fyi_p=fyi_p,
                                        low_p=low_p,
                                        medium_p=medium_p,
                                        high_p=high_p,
                                        emergency_p=emergency_p,
                                        next7days=next7days
                                        )

# -------------------------------------------------Sign up-------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")


        # Check existed username
        rows = db.execute("SELECT COUNT(id) existusername FROM userinfo WHERE username = ?", username)
        rows2 = db.execute("SELECT COUNT(id) existemail FROM userinfo WHERE email = ?", email)
        
        if rows[0]["existusername"] > 0 or rows2[0]["existemail"] > 0:
            flash('This is username or email already exists', 'warning')
            return redirect("/signup")
        else:
            # Hash Password & Insert Password
            db.execute("INSERT INTO userinfo (username, name, surname, email, hash) VALUES (?, ?, ?, ?, ?)",username, name, surname, email, generate_password_hash(password))
            flash('You were successfully signed up', 'success')
            return redirect("/")

    else:
        return render_template("login.html")

# -------------------------------------------------Log in-------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        rows = db.execute("SELECT * FROM userinfo WHERE email = ?", email)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash('Invalid Login. Try Again','warning')
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]

        flash('You were successfully logged in', 'success')
        return redirect("/")

    else:
        return render_template("login.html")

# -------------------------------------------------Log out-------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out', 'success')
    return redirect("/login")

# -------------------------------------------------Request Form-------------------------------------------------
@app.route("/requestform", methods=["GET", "POST"])
@login_required
def requestform():

    if request.method == "POST":
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM userinfo where id = ?", user_id) 
        username = rows[0]["username"]
        toemail = request.form.get("tousername")
        cc = request.form.get("cc")
        project_name = request.form.get("projectname")
        priority = request.form.get("priority")
        duedate = request.form.get("duedate")
        duetime = request.form.get("duetime")
        detail = request.form.get("detail")
        files = request.form.get("file")
        
        if not toemail or not project_name or not priority:
            flash('Please fill email, project name and priority','warning')
            return render_template("requestform.html")

        db.execute("INSERT INTO requestmeinfo(user_id, username, toemail, cc, project_name, priority, duedate, duetime, detail, files) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",user_id, username, toemail, cc, project_name, priority, duedate, duetime, detail, files)
        flash('The task is successfully submit', 'success')
        return redirect("/requestform")

    else:
        return render_template("requestform.html")

# -------------------------------------------------Task-------------------------------------------------
@app.route("/yourtask", methods=["GET", "POST"])
@login_required
def yourtask():

    user_id = session["user_id"]
    emails = db.execute("SELECT email FROM userinfo WHERE id = ?", user_id)
    email = emails[0]["email"]
    info = db.execute("SELECT * FROM requestmeinfo WHERE status = 'IN PROGRESS' AND toemail Like ?", "%" + email + "%")
    
    return render_template("yourtask.html", info = info)

@app.route("/yourtask/<no>", methods=["GET", "POST"])
def get_yourtask(no):
    no = no
    info = db.execute("SELECT * FROM requestmeinfo WHERE no = ?", no)
    user_id = session["user_id"]
    comment = request.form.get("comment")
    files = request.form.get("file")

    if request.method == "POST":
        if request.form.get("complete"):
            db.execute("UPDATE requestmeinfo SET status = 'COMPLETED' WHERE no = ?",no)
            flash('Your task is completed', 'success')
            return redirect("/yourtask")
        else:
            if request.form.get("complete_reply"):
                db.execute("INSERT INTO replyinfo(user_id, project_no, detail, files) VALUES (?, ?, ?, ?)",user_id, no, comment, files)
                db.execute("UPDATE requestmeinfo SET status = 'COMPLETED' WHERE no = ?",no)
                return redirect("/yourtask")
                flash('You were successfully replied', 'success')
            return render_template("reply.html", info = info)

    else:
        return render_template("projectdetail.html", info = info)


# -------------------------------------------------history-------------------------------------------------
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    user_id = session["user_id"]
    emails = db.execute("SELECT email FROM userinfo WHERE id = ?", user_id)
    email = emails[0]["email"]
    info = db.execute("SELECT * FROM requestmeinfo WHERE toemail Like ?", "%" + email + "%")
    sendinfo = db.execute("SELECT * FROM requestmeinfo WHERE user_id = ?", user_id)
    return render_template("history.html", info = info, sendinfo=sendinfo)

@app.route("/history/<no>", methods=["GET", "POST"])
def get_history(no):
    no = no
    info = db.execute("SELECT * FROM requestmeinfo WHERE no = ?",no)
    notshow = True

    return render_template("projectdetail.html", info = info, notshow=notshow)

# -------------------------------------------------recieved-------------------------------------------------
@app.route("/recieved", methods=["GET", "POST"])
@login_required
def recieved():

    user_id = session["user_id"]
    print(user_id)
    emails = db.execute("SELECT email FROM userinfo WHERE id = ?", user_id)
    email = emails[0]["email"]
    info = db.execute("SELECT * FROM requestmeinfo WHERE user_id = ? AND status = 'COMPLETED'", user_id)
    reply = db.execute("SELECT * FROM replyinfo") 
    print(reply)
    
    return render_template("recieved.html", info = info, reply=reply)

@app.route("/recieved/<no>", methods=["GET", "POST"])
def get_recieved(no):
    no = no
    info = db.execute("SELECT * FROM requestmeinfo WHERE no = ?",no)
    replyinfo = db.execute("SELECT * FROM replyinfo WHERE project_no = ?",no)
    notshow = True
    recieved_page = True

    return render_template("projectdetail.html", info = info, notshow = notshow, replyinfo=replyinfo, recieved_page=recieved_page)


# -------------------------------------------------Contact-------------------------------------------------
@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        user_id = session["user_id"]
        Subject = request.form.get("subject")
        detail = request.form.get("message")
        
        if not Subject or not detail: 
            flash('Please fill subject and detail', 'warning') 
            return render_template("contact.html")

        db.execute("INSERT INTO contactme(user_id, Subject, detail) VALUES (?, ?, ?)",user_id, Subject, detail)
        flash('You message is sent', 'success')
        return render_template("contact.html")

    else:
        return render_template("contact.html")
        