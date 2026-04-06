print("APP STARTED")
from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import os

from models import init_db
from pose_engine import extract_angles_from_video
from exercise_engine import *
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file

app = Flask(__name__)
app.secret_key = "secretkey"

DATABASE = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# ================= DB =================

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")

@app.route('/register_page')
def register_page():
    return render_template("register.html")

# -------- REGISTER --------
@app.route('/register', methods=['POST'])
def register():
    db = get_db()
    db.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (request.form['username'], request.form['email'], request.form['password'])
    )
    db.commit()
    return redirect('/login_page')

# -------- LOGIN --------
@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (request.form['username'], request.form['password'])
    ).fetchone()

    if user:
        session['user_id'] = user['id']
        return redirect('/dashboard')
    return "Invalid login"

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("dashboard.html")

# -------- UPLOAD --------
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/')

    exercise = request.form['exercise']
    file = request.files['video']

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    elbow, knee, hip = extract_angles_from_video(filepath)

    # Exercise logic
    if exercise == "pushup":
        reps = count_pushups(elbow)
    elif exercise == "squat":
        reps = count_squats(knee)
    elif exercise == "situp":
        reps = count_situps(hip)
    elif exercise == "plank":
        reps = count_plank(elbow)
    elif exercise == "jump":
        reps = int(max(hip))
    elif exercise == "running":
        reps = len(hip)
    else:
        reps = 0

    if exercise == "pushup":
        score, feedback = generate_score(reps, elbow, exercise)
    elif exercise == "squat":
        score, feedback = generate_score(reps, knee, exercise)
    else:
        score, feedback = generate_score(reps, None, exercise)

    db = get_db()
    db.execute("""
        INSERT INTO results (user_id, exercise_type, repetitions, score, feedback)
        VALUES (?,?,?,?,?)
    """, (session['user_id'], exercise, reps, score, feedback))

    db.commit()

    return render_template("result.html", reps=reps, score=score, feedback=feedback)

from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import os

from models import init_db
from pose_engine import extract_angles_from_video
from exercise_engine import *

app = Flask(__name__)
app.secret_key = "secretkey"

DATABASE = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# ================= DB =================

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")

@app.route('/register_page')
def register_page():
    return render_template("register.html")

# -------- REGISTER --------
@app.route('/register', methods=['POST'])
def register():
    db = get_db()
    db.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (request.form['username'], request.form['email'], request.form['password'])
    )
    db.commit()
    return redirect('/login_page')

# -------- LOGIN --------
@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (request.form['username'], request.form['password'])
    ).fetchone()

    if user:
        session['user_id'] = user['id']
        return redirect('/dashboard')
    return "Invalid login"

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("dashboard.html")
    # -------- ADMIN DASHBOARD --------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin_login')

    db = get_db()

    users = db.execute("SELECT * FROM users").fetchall()
    results = db.execute("SELECT * FROM results").fetchall()

    return render_template(
        "admin_dashboard.html",
        users=users,
        results=results
    )

# -------- UPLOAD --------
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/')

    exercise = request.form['exercise']
    file = request.files['video']

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    elbow, knee, hip = extract_angles_from_video(filepath)

    # Exercise logic
    if exercise == "pushup":
        reps = count_pushups(elbow)
    elif exercise == "squat":
        reps = count_squats(knee)
    elif exercise == "situp":
        reps = count_situps(hip)
    elif exercise == "plank":
        reps = count_plank(elbow)
    elif exercise == "jump":
        reps = int(max(hip))
    elif exercise == "running":
        reps = len(hip)
    else:
        reps = 0

    score, feedback = generate_score(reps)

    db = get_db()
    db.execute("""
        INSERT INTO results (user_id, exercise_type, repetitions, score, feedback)
        VALUES (?,?,?,?,?)
    """, (session['user_id'], exercise, reps, score, feedback))

    db.commit()

    return render_template("result.html", reps=reps, score=score, feedback=feedback)
@app.route('/leaderboard')
def leaderboard():
    db = get_db()

    data = db.execute("""
        SELECT users.username, AVG(results.score) as avg_score
        FROM results
        JOIN users ON results.user_id = users.id
        GROUP BY users.username
        ORDER BY avg_score DESC
    """).fetchall()

    return render_template("leaderboard.html", data=data)
@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()

    data = db.execute("""
        SELECT exercise_type, score
        FROM results
        WHERE user_id=?
    """, (session['user_id'],)).fetchall()

    exercises = [row['exercise_type'] for row in data]
    scores = [row['score'] for row in data]

    return render_template("progress.html",
                           exercises=exercises,
                           scores=scores)
@app.route('/download_report')
def download_report():

    if 'user_id' not in session:
        return redirect('/')

    db = get_db()

    data = db.execute("""
        SELECT exercise_type, repetitions, score, feedback
        FROM results
        WHERE user_id=?
        ORDER BY id DESC LIMIT 1
    """, (session['user_id'],)).fetchone()

    file_path = "report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Athlete Performance Report", styles['Title']))
    content.append(Paragraph(f"Exercise: {data['exercise_type']}", styles['Normal']))
    content.append(Paragraph(f"Repetitions: {data['repetitions']}", styles['Normal']))
    content.append(Paragraph(f"Score: {data['score']}", styles['Normal']))
    content.append(Paragraph(f"Feedback: {data['feedback']}", styles['Normal']))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # simple admin check
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/admin_dashboard')
        else:
            return "Invalid Admin Login"

    return render_template("admin_login.html")
@app.route('/delete_user/<int:id>')
def delete_user(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    return redirect('/admin_dashboard')


# -------- MAIN --------
if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)