from flask import Flask, render_template, request
import mySQL
from secret import CLIENT_ID, CLIENT_SECRET
from routes.authentication import *
import SMTP

app = Flask(__name__)
app.secret_key = "SECRET_KEY"
app.config["GITHUB_CLIENT_ID"] = CLIENT_ID
app.config["GITHUB_CLIENT_SECRET"] = CLIENT_SECRET

database = mySQL.dataSQL("database.db")

def check_session(session):
    return "token" in session and "username" in session and "id" in session

@app.template_filter('nl2br')
def nl2br_filter(s):
    """Converts newlines to <br> tags."""
    return s.replace('\n', '<br>')
    

@app.route('/')
def index():
    return render_template("mainPage.html")

@app.route("/lobby")
def lobby():
    sessionExists = check_session(session)
    
    return render_template("lobby.html", session=session)

@app.route("/me", methods=['GET', 'POST'])
def mePage():
    if request.method == 'POST':
        action = request.form.get("action")  # Assuming you have a form field named 'message'
        if action == "addExp": 
            database.use_database(
                "INSERT INTO experiences (associated_user_id, company_name, company_logo_url, position_title, position_description, dates) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session["id"], 
                    request.form.get("company_name"),
                    request.form.get("company_logo"),
                    request.form.get("position_name"),
                    request.form.get("description"),
                    request.form.get("position_dates")
                    
                ),
            )

            pass
        elif action == "editExp":
            database.use_database(
                f"UPDATE experiences SET company_name = ?, company_logo_url = ?, position_title = ?, position_description = ?, dates = ? WHERE id = ?;", 
                (   
                    request.form.get("company_name"),
                    request.form.get("company_logo"),
                    request.form.get("position_name"),
                    request.form.get("description"),
                    request.form.get("position_dates"),
                    request.form.get("unique_id")
                ),
            )
        
        elif action == "delExp":
            database.use_database(
                "DELETE FROM experiences WHERE id = ?", 
                (   
                    request.form.get("unique_id")
                ),
            )

        if action == "addEdu": 
            database.use_database(
                "INSERT INTO educations (associated_user_id, tuition_name, tuition_logo_url, position_description, dates) VALUES (?, ?, ?, ?, ?)",
                (
                    session["id"], 
                    request.form.get("campus_name"),
                    request.form.get("campus_logo"),
                    request.form.get("description"),
                    request.form.get("dates")
                    
                ),
            )

        elif action == "editEdu":
            database.use_database(
                f"UPDATE educations SET tuition_name = ?, tuition_logo_url = ?, position_description = ?, dates = ? WHERE id = ?;", 
                (   
                    request.form.get("campus_name"),
                    request.form.get("campus_logo"),
                    request.form.get("description"),
                    request.form.get("dates"),
                    request.form.get("unique_id")
                ),
            )
        
        elif action == "delEdu":
            database.use_database(
                "DELETE FROM educations WHERE id = ?", 
                (   
                    request.form.get("unique_id")
                ),
            )
        
        elif action == "upDescription":
            database.use_database(
                "UPDATE users SET description = ? WHERE id = ?", 
                (   
                    request.form.get("description"),
                    session["id"]
                ),
            )

        
        return redirect(url_for('mePage'))

            
    experiences = database.get_experiences(session["id"])
    educations = database.get_educations(session["id"])
    user = database.get_user(session["id"])

        
    return render_template("mePage.html", session=session, experiences=experiences, user=user, educations=educations)

@app.route("/user")
def userPage():
    id = request.args.get("id")
    experiences = database.get_experiences(id)
    educations = database.get_educations(id)
    user = database.get_user(id)

    return render_template("userPage.html", experiences=experiences, user=user, educations=educations)


@app.route("/jobs")
def jobPostings():
    return render_template("jobPosting.html")

@app.route("/business") #this is for accessing a single business site 
def businessTemplate():
    return render_template("businessTemplate.html")

@app.route("/verify", methods=['GET', 'POST'])
def verify():
    user = database.get_user(session["id"])

    if request.method == 'POST':
        if email := request.form.get("email"):

            if user.is_verified: #if email already verified...then no need to change it.
                return redirect("lobby")


            database.use_database(
                f"UPDATE users SET email = ? WHERE id = ?;", 
                (   
                    email,
                    session["id"]
                ),
            )
        
            SMTP.send_email(email, SMTP.generateCode(session["id"],email))

            return redirect("verify")
            
        elif code := request.form.get("code"):
            #email already given
            id = SMTP.generateCode( str(session["id"]) , user.email)
            if id == code:
                database.use_database(
                    f"UPDATE users SET is_verified = ? WHERE id = ?;", 
                    (   
                        1,
                        session["id"]
                    ),
                )

                return redirect("lobby")


    return render_template("verify.html")

if __name__ == "__main__":

    app.register_blueprint(authentication)
    
    app.run()