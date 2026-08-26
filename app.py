import os
import json
import uuid
import random
import hashlib
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'linuxquest-secret-key-cyber-2026')

# 20 Levels XP Thresholds
LEVEL_THRESHOLDS = [
    0, 500, 1200, 2200, 3500, 5000, 7000, 9500, 12500, 16000,
    20000, 24500, 29500, 35000, 41000, 47500, 54500, 62000, 70000, 79000
]

def calculate_level(xp):
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return min(level, 20)

def award_xp(db, user_id, xp_amount, source, description):
    db.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (xp_amount, user_id))
    user = db.execute("SELECT xp FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        new_level = calculate_level(user['xp'])
        db.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))

    db.execute("""
        INSERT INTO xp_transactions (user_id, amount, source, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, xp_amount, source, description))
    db.commit()

def check_and_award_achievements(db, user_id):
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return []

    quests_count = db.execute("SELECT COUNT(*) as c FROM user_quest_attempts WHERE user_id = ?", (user_id,)).fetchone()['c']
    unlocked_keys = []
    achievements = db.execute("SELECT * FROM achievements;").fetchall()

    for ach in achievements:
        already_has = db.execute("SELECT id FROM user_achievements WHERE user_id = ? AND achievement_id = ?", (user_id, ach['id'])).fetchone()
        if already_has:
            continue

        unlocked = False
        if ach['required_metric'] == 'total_xp' and user['xp'] >= ach['required_value']:
            unlocked = True
        elif ach['required_metric'] == 'streak_days' and user['streak'] >= ach['required_value']:
            unlocked = True
        elif ach['required_metric'] == 'user_level' and user['level'] >= ach['required_value']:
            unlocked = True
        elif ach['required_metric'] == 'quests_completed' and quests_count >= ach['required_value']:
            unlocked = True
        elif ach['required_metric'] == 'commands_executed' and user['xp'] > 0:
            unlocked = True

        if unlocked:
            db.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)", (user_id, ach['id']))
            db.commit()
            unlocked_keys.append(ach['title'])
            award_xp(db, user_id, ach['xp_reward'], "achievement", f"Unlocked Achievement: {ach['title']}")

    return unlocked_keys

@app.before_request
def load_logged_in_user():
    g.db = get_db()
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = g.db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

@app.teardown_request
def close_db(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def login_required(f):
    def wrapper(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_required(f):
    def wrapper(*args, **kwargs):
        if g.user is None or g.user['role'] != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- CORE PAGE ROUTES ---

@app.route('/')
def index():
    levels = g.db.execute("SELECT * FROM levels ORDER BY level_number ASC;").fetchall()
    return render_template('index.html', levels=levels)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            return render_template('register.html', error="All fields are required.")
        if len(username) < 3:
            return render_template('register.html',
                                   error="Username must be at least 3 characters.")

        if len(password) < 6:
            return render_template('register.html',
                                   error="Password must be at least 6 characters.")

        if "@" not in email or "." not in email:
            return render_template('register.html',
                                   error="Please enter a valid email address.")
        hashed_pw = generate_password_hash(password)
        try:
            cursor = g.db.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, level, xp, streak, avatar)
                VALUES (?, ?, ?, 'user', 1, 0, 1, 'terminal_hero.png')
            """, (username, email, hashed_pw))
            g.db.commit()

            new_id = cursor.lastrowid
            session['user_id'] = new_id
            award_xp(g.db, new_id, 50, "welcome", "Welcome bonus for registering on LinuxQuest!")
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('register.html', error="Username or Email already exists.")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = g.db.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']

            today = date.today().strftime("%Y-%m-%d")
            last_login = user['last_login_date']
            new_streak = user['streak']

            if last_login:
                last_dt = datetime.strptime(last_login, "%Y-%m-%d").date()
                if last_dt == date.today() - timedelta(days=1):
                    new_streak += 1
                elif last_dt < date.today() - timedelta(days=1):
                    new_streak = 1
            else:
                new_streak = 1

            longest = max(user['longest_streak'], new_streak)
            g.db.execute("UPDATE users SET last_login_date = ?, streak = ?, longest_streak = ? WHERE id = ?", (today, new_streak, longest, user['id']))
            g.db.commit()

            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = g.user
    next_xp = LEVEL_THRESHOLDS[min(user['level'], 19)]

    completed_lessons = g.db.execute("SELECT COUNT(*) as c FROM user_learn_progress WHERE user_id = ?", (user['id'],)).fetchone()['c']
    completed_quests = g.db.execute("SELECT COUNT(*) as c FROM user_quest_attempts WHERE user_id = ?", (user['id'],)).fetchone()['c']
    total_lessons = g.db.execute("SELECT COUNT(*) as c FROM learn_lessons;").fetchone()['c']

    next_lesson = g.db.execute("""
        SELECT l.* FROM learn_lessons l
        LEFT JOIN user_learn_progress p ON l.id = p.learn_lesson_id AND p.user_id = ?
        WHERE p.id IS NULL
        ORDER BY l.lesson_number ASC
        LIMIT 1;
    """, (user['id'],)).fetchone()

    activities = g.db.execute("SELECT * FROM xp_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 6;", (user['id'],)).fetchall()
    achievements = g.db.execute("""
        SELECT a.*, ua.unlocked_at FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
        ORDER BY ua.unlocked_at DESC, a.id ASC LIMIT 6;
    """, (user['id'],)).fetchall()

    return render_template('dashboard.html',
                           user=user,
                           next_xp=next_xp,
                           completed_lessons=completed_lessons,
                           total_lessons=total_lessons,
                           completed_quests=completed_quests,
                           next_lesson=next_lesson,
                           activities=activities,
                           achievements=achievements)

# --- LEARN SECTION (Up to 10 Lessons) ---
@app.route('/learn')
def learn_list():
    lessons = g.db.execute("SELECT * FROM learn_lessons ORDER BY lesson_number ASC;").fetchall()
    completed_ids = set()
    if g.user:
        rows = g.db.execute("SELECT learn_lesson_id FROM user_learn_progress WHERE user_id = ?", (g.user['id'],)).fetchall()
        completed_ids = {r['learn_lesson_id'] for r in rows}

    return render_template('learn.html', lessons=lessons, completed_ids=completed_ids)

@app.route('/learn/<slug>')
def learn_detail(slug):
    lesson = g.db.execute("SELECT * FROM learn_lessons WHERE slug = ?", (slug,)).fetchone()
    if not lesson:
        return redirect(url_for('learn_list'))

    is_completed = False
    if g.user:
        row = g.db.execute("SELECT id FROM user_learn_progress WHERE user_id = ? AND learn_lesson_id = ?", (g.user['id'], lesson['id'])).fetchone()
        is_completed = bool(row)

    examples = json.loads(lesson['command_examples_json'])
    return render_template('learn_detail.html', lesson=lesson, is_completed=is_completed, examples=examples)

# --- 20 LEVELS ROADMAP ---
@app.route('/levels')
def levels():
    levels_data = g.db.execute("SELECT * FROM levels ORDER BY level_number ASC;").fetchall()
    lessons_data = g.db.execute("SELECT * FROM learn_lessons ORDER BY lesson_number ASC;").fetchall()

    user_completed_lesson_ids = set()
    if g.user:
        rows = g.db.execute("SELECT learn_lesson_id FROM user_learn_progress WHERE user_id = ?", (g.user['id'],)).fetchall()
        user_completed_lesson_ids = {r['learn_lesson_id'] for r in rows}

    return render_template('levels.html', levels=levels_data, lessons=lessons_data, completed_ids=user_completed_lesson_ids)

# --- WRITTEN COMMAND TEST QUESTS ---
@app.route('/quests')
def quests_list():
    quests_data = g.db.execute("""
        SELECT q.*, l.title as level_title, l.level_number
        FROM quests q
        JOIN levels l ON q.level_id = l.id
        ORDER BY l.level_number ASC, q.order_index ASC;
    """).fetchall()

    completed_quest_ids = set()
    if g.user:
        rows = g.db.execute("SELECT quest_id FROM user_quest_attempts WHERE user_id = ?", (g.user['id'],)).fetchall()
        completed_quest_ids = {r['quest_id'] for r in rows}

    return render_template('quests.html', quests=quests_data, completed_ids=completed_quest_ids)

@app.route('/quest/<slug>')
def quest_detail(slug):
    quest = g.db.execute("SELECT * FROM quests WHERE slug = ?", (slug,)).fetchone()
    if not quest:
        return redirect(url_for('quests_list'))

    all_quests = g.db.execute("SELECT id, title, slug, difficulty, xp_reward FROM quests ORDER BY id ASC;").fetchall()
    return render_template('quest_detail.html', quest=quest, all_quests=all_quests)

# --- 10 QUIZ LEVELS (5 Questions each, Daily Shuffled) ---
@app.route('/quizzes')
def quizzes_list():
    quiz_levels = g.db.execute("SELECT * FROM quiz_levels ORDER BY quiz_level_number ASC;").fetchall()
    return render_template('quizzes.html', quiz_levels=quiz_levels)

@app.route('/quiz/<int:quiz_level_number>')
def quiz_play(quiz_level_number):
    ql = g.db.execute("SELECT * FROM quiz_levels WHERE quiz_level_number = ?", (quiz_level_number,)).fetchone()
    if not ql:
        return redirect(url_for('quizzes_list'))

    questions_rows = g.db.execute("SELECT * FROM quiz_questions WHERE quiz_level_id = ?", (ql['id'],)).fetchall()
    
    # Shuffle questions daily using date seed
    today_seed = int(datetime.now().strftime("%Y%m%d")) + quiz_level_number
    rng = random.Random(today_seed)
    questions = list(questions_rows)
    rng.shuffle(questions)

    parsed_questions = []
    for q in questions:
        parsed_questions.append({
            'id': q['id'],
            'question_text': q['question_text'],
            'options': json.loads(q['options_json']),
            'explanation': q['explanation']
        })

    return render_template('quiz_play.html', quiz_level=ql, questions=parsed_questions)

# --- PERFORMANCE ANALYTICS ---
@app.route('/performance')
@login_required
def performance():
    user = g.user
    quiz_attempts = g.db.execute("SELECT * FROM user_quiz_attempts WHERE user_id = ? ORDER BY completed_at DESC LIMIT 10", (user['id'],)).fetchall()
    quests_count = g.db.execute("SELECT COUNT(*) as c FROM user_quest_attempts WHERE user_id = ?", (user['id'],)).fetchone()['c']
    learn_count = g.db.execute("SELECT COUNT(*) as c FROM user_learn_progress WHERE user_id = ?", (user['id'],)).fetchone()['c']
    
    avg_quiz_score = 0
    if quiz_attempts:
        avg_quiz_score = int(sum(a['score'] for a in quiz_attempts) / len(quiz_attempts))

    return render_template('performance.html', user=user, avg_quiz_score=avg_quiz_score, quests_count=quests_count, learn_count=learn_count, quiz_attempts=quiz_attempts)

# --- FRIENDS SYSTEM ---
@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    message = None
    error = None

    if request.method == 'POST':
        friend_username = request.form.get('friend_username', '').strip()
        target = g.db.execute("SELECT id FROM users WHERE username = ?", (friend_username,)).fetchone()
        if target:
            if target['id'] == g.user['id']:
                error = "You cannot add yourself as a friend."
            else:
                try:
                    g.db.execute("INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'accepted')", (g.user['id'], target['id']))
                    g.db.execute("INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'accepted')", (target['id'], g.user['id']))
                    g.db.commit()
                    message = f"Added {friend_username} to your Friends list!"
                except Exception:
                    error = f"Already friends with {friend_username}."
        else:
            error = f"User '{friend_username}' not found."

    friends_list = g.db.execute("""
        SELECT u.id, u.username, u.avatar, u.level, u.xp, u.streak
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = ? AND f.status = 'accepted'
        ORDER BY u.xp DESC;
    """, (g.user['id'],)).fetchall()

    return render_template('friends.html', friends=friends_list, message=message, error=error)

# --- CERTIFICATE ROUTE (LEVEL 20 LOCK) ---
@app.route('/certificate')
@login_required
def certificate():
    user = g.user
    # STRICT UNLOCK: Requires Level 20 or Admin role!
    is_unlocked = user['level'] >= 20 or user['role'] == 'admin'

    if not is_unlocked:
        return render_template('certificate_locked.html', user=user)

    cert = g.db.execute("SELECT * FROM certificates WHERE user_id = ?", (user['id'],)).fetchone()
    if not cert:
        cert_code = f"LQ-CERT-{uuid.uuid4().hex[:8].upper()}"
        verify_hash = hashlib.sha256(f"{user['username']}-{cert_code}-linuxquest-2026".encode()).hexdigest()[:16].upper()
        
        g.db.execute("""
            INSERT INTO certificates (user_id, cert_code, verification_hash)
            VALUES (?, ?, ?)
        """, (user['id'], cert_code, verify_hash))
        g.db.commit()
        cert = g.db.execute("SELECT * FROM certificates WHERE user_id = ?", (user['id'],)).fetchone()

    return render_template('certificate.html', user=user, cert=cert)

@app.route('/verify-certificate/<cert_code>')
def verify_certificate(cert_code):
    cert = g.db.execute("SELECT c.*, u.username FROM certificates c JOIN users u ON c.user_id = u.id WHERE cert_code = ?", (cert_code,)).fetchone()
    return render_template('verify_certificate.html', cert=cert)

@app.route('/speedrun')
def speedrun():
    return render_template('speedrun.html')

@app.route('/script-builder')
def script_builder():
    return render_template('script_builder.html')

@app.route('/cheatsheet')
def cheatsheet():
    return render_template('cheatsheet.html')

@app.route('/achievements')
def achievements():
    achievements_data = g.db.execute("SELECT * FROM achievements ORDER BY id ASC;").fetchall()
    unlocked_map = {}
    if g.user:
        rows = g.db.execute("SELECT achievement_id, unlocked_at FROM user_achievements WHERE user_id = ?", (g.user['id'],)).fetchall()
        unlocked_map = {r['achievement_id']: r['unlocked_at'] for r in rows}

    return render_template('achievements.html', achievements=achievements_data, unlocked_map=unlocked_map)

@app.route('/leaderboard')
def leaderboard():
    filter_type = request.args.get('filter', 'global')
    users = g.db.execute("""
        SELECT id, username, avatar, level, xp, streak, role
        FROM users
        ORDER BY xp DESC, streak DESC
        LIMIT 50;
    """).fetchall()

    return render_template('leaderboard.html', users=users, active_filter=filter_type)

@app.route('/daily')
def daily_challenge():
    today = date.today().strftime("%Y-%m-%d")
    challenge = g.db.execute("SELECT dc.*, q.slug as quest_slug FROM daily_challenges dc JOIN quests q ON dc.quest_id = q.id WHERE date_str = ?", (today,)).fetchone()

    is_completed = False
    if g.user and challenge:
        row = g.db.execute("SELECT id FROM daily_challenge_completions WHERE user_id = ? AND daily_challenge_id = ?", (g.user['id'], challenge['id'])).fetchone()
        is_completed = bool(row)

    return render_template('daily.html', challenge=challenge, is_completed=is_completed)

@app.route('/profile')
@login_required
def profile():
    user = g.user
    achievements_count = g.db.execute("SELECT COUNT(*) as c FROM user_achievements WHERE user_id = ?", (user['id'],)).fetchone()['c']
    quests_count = g.db.execute("SELECT COUNT(*) as c FROM user_quest_attempts WHERE user_id = ?", (user['id'],)).fetchone()['c']
    learn_count = g.db.execute("SELECT COUNT(*) as c FROM user_learn_progress WHERE user_id = ?", (user['id'],)).fetchone()['c']

    activities = g.db.execute("SELECT * FROM xp_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user['id'],)).fetchall()
    user_achievements = g.db.execute("""
        SELECT a.*, ua.unlocked_at FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = ?
        ORDER BY ua.unlocked_at DESC;
    """, (user['id'],)).fetchall()

    return render_template('profile.html', user=user, achievements_count=achievements_count, quests_count=quests_count, lessons_count=learn_count, activities=activities, user_achievements=user_achievements)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    message = None
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'profile':
            bio = request.form.get('bio', '').strip()
            g.db.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, g.user['id']))
            g.db.commit()
            message = "Profile updated successfully!"
        elif action == 'password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            if check_password_hash(g.user['password_hash'], old_pw):
                hashed = generate_password_hash(new_pw)
                g.db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, g.user['id']))
                g.db.commit()
                message = "Password changed successfully!"
            else:
                error = "Incorrect current password."

    return render_template('settings.html', user=g.user, message=message, error=error)

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = g.db.execute("SELECT COUNT(*) as c FROM users;").fetchone()['c']
    total_lessons = g.db.execute("SELECT COUNT(*) as c FROM learn_lessons;").fetchone()['c']
    total_quests = g.db.execute("SELECT COUNT(*) as c FROM quests;").fetchone()['c']
    users_list = g.db.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 20;").fetchall()
    lessons_list = g.db.execute("SELECT * FROM learn_lessons ORDER BY lesson_number ASC;").fetchall()
    quests_list = g.db.execute("SELECT q.*, lvl.title as level_title FROM quests q JOIN levels lvl ON q.level_id = lvl.id ORDER BY q.id ASC;").fetchall()

    return render_template('admin.html', total_users=total_users, total_lessons=total_lessons, total_quests=total_quests, users=users_list, lessons=lessons_list, quests=quests_list)

# --- REST APIs ---

@app.route('/api/learn/<int:lesson_id>/complete', methods=['POST'])
@login_required
def api_complete_learn_lesson(lesson_id):
    lesson = g.db.execute("SELECT * FROM learn_lessons WHERE id = ?", (lesson_id,)).fetchone()
    if not lesson:
        return jsonify({'success': False, 'error': 'Lesson not found'}), 404

    existing = g.db.execute("SELECT id FROM user_learn_progress WHERE user_id = ? AND learn_lesson_id = ?", (g.user['id'], lesson_id)).fetchone()
    if not existing:
        g.db.execute("INSERT INTO user_learn_progress (user_id, learn_lesson_id) VALUES (?, ?)", (g.user['id'], lesson_id))
        g.db.commit()
        award_xp(g.db, g.user['id'], lesson['xp_reward'], "learn", f"Completed Learn Lesson: {lesson['title']}")
        new_badges = check_and_award_achievements(g.db, g.user['id'])
        return jsonify({'success': True, 'xp_earned': lesson['xp_reward'], 'new_badges': new_badges})

    return jsonify({'success': True, 'already_completed': True})

@app.route('/api/quiz-levels/<int:quiz_level_id>/submit', methods=['POST'])
@login_required
def api_submit_quiz_level(quiz_level_id):
    ql = g.db.execute("SELECT * FROM quiz_levels WHERE id = ?", (quiz_level_id,)).fetchone()
    if not ql:
        return jsonify({'success': False, 'error': 'Quiz level not found'}), 404

    answers = request.get_json() or {}
    questions = g.db.execute("SELECT * FROM quiz_questions WHERE quiz_level_id = ?", (quiz_level_id,)).fetchall()
    
    correct_count = sum(1 for q in questions if answers.get(str(q['id'])) == q['correct_answer_index'])
    total = len(questions)

    score = int((correct_count / total) * 100) if total > 0 else 0
    passed = 1 if score >= 70 else 0

    g.db.execute("INSERT INTO user_quiz_attempts (user_id, quiz_id, score, passed) VALUES (?, ?, ?, ?)", (g.user['id'], quiz_level_id, score, passed))
    g.db.commit()

    xp_earned = 0
    if passed:
        xp_earned = ql['xp_reward']
        award_xp(g.db, g.user['id'], xp_earned, "quiz", f"Passed Quiz Level {ql['quiz_level_number']} ({score}%)")

    new_badges = check_and_award_achievements(g.db, g.user['id'])
    return jsonify({'success': True, 'score': score, 'passed': bool(passed), 'xp_earned': xp_earned, 'new_badges': new_badges})

if __name__ == '__main__':
    print("[+] Starting LinuxQuest Web Server...")
    print("[+] URL: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
