import sqlite3
import os
import json
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), 'linuxquest.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        level INTEGER NOT NULL DEFAULT 1,
        xp INTEGER NOT NULL DEFAULT 0,
        streak INTEGER NOT NULL DEFAULT 0,
        longest_streak INTEGER NOT NULL DEFAULT 0,
        last_login_date TEXT,
        avatar TEXT DEFAULT 'terminal_hero.png',
        bio TEXT DEFAULT 'Linux Enthusiast on a Quest!',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Levels Table (1 to 20)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level_number INTEGER UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        required_xp INTEGER NOT NULL
    );
    ''')

    # Learn Lessons Table (Up to 10 Core Topics)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learn_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_number INTEGER UNIQUE NOT NULL,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        summary TEXT NOT NULL,
        content_md TEXT NOT NULL,
        command_examples_json TEXT NOT NULL,
        estimated_minutes INTEGER DEFAULT 15,
        xp_reward INTEGER DEFAULT 75
    );
    ''')

    # Lessons Table (Linked to Levels)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        estimated_minutes INTEGER DEFAULT 10,
        difficulty TEXT DEFAULT 'Beginner',
        objectives_json TEXT NOT NULL,
        content_md TEXT NOT NULL,
        code_examples_json TEXT NOT NULL,
        xp_reward INTEGER DEFAULT 50,
        order_index INTEGER DEFAULT 1,
        FOREIGN KEY (level_id) REFERENCES levels (id) ON DELETE CASCADE
    );
    ''')

    # Quests Table (Written Command Tests)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        objective TEXT NOT NULL,
        initial_vfs_json TEXT NOT NULL,
        expected_state_json TEXT NOT NULL,
        verification_type TEXT DEFAULT 'vfs_state',
        hint TEXT NOT NULL,
        xp_reward INTEGER DEFAULT 100,
        difficulty TEXT DEFAULT 'Easy',
        order_index INTEGER DEFAULT 1,
        FOREIGN KEY (level_id) REFERENCES levels (id) ON DELETE CASCADE
    );
    ''')

    # Quiz Levels Table (10 Levels)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_level_number INTEGER UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        xp_reward INTEGER DEFAULT 100
    );
    ''')

    # Quiz Questions Table (5 Questions per Quiz Level = 50 total)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_level_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        options_json TEXT NOT NULL,
        correct_answer_index INTEGER NOT NULL,
        explanation TEXT NOT NULL,
        FOREIGN KEY (quiz_level_id) REFERENCES quiz_levels (id) ON DELETE CASCADE
    );
    ''')

    # Quizzes Table (Legacy compatibility)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        questions_json TEXT NOT NULL,
        xp_reward INTEGER DEFAULT 75
    );
    ''')

    # Friends Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        friend_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'accepted',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, friend_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (friend_id) REFERENCES users (id) ON DELETE CASCADE
    );
    ''')

    # Certificates Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        cert_code TEXT UNIQUE NOT NULL,
        title TEXT DEFAULT 'LinuxQuest Certified Linux Architect',
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        verification_hash TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    ''')

    # User Progress Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_learn_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        learn_lesson_id INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, learn_lesson_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (learn_lesson_id) REFERENCES learn_lessons (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_lesson_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lesson_id INTEGER NOT NULL,
        status TEXT DEFAULT 'completed',
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, lesson_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_quest_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quest_id INTEGER NOT NULL,
        status TEXT DEFAULT 'completed',
        attempts_count INTEGER DEFAULT 1,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, quest_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (quest_id) REFERENCES quests (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        passed INTEGER DEFAULT 1,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, achievement_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        required_metric TEXT NOT NULL,
        required_value INTEGER NOT NULL,
        xp_reward INTEGER DEFAULT 100
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS xp_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        source TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_str TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        quest_id INTEGER NOT NULL,
        bonus_xp INTEGER DEFAULT 150,
        FOREIGN KEY (quest_id) REFERENCES quests (id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_challenge_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        daily_challenge_id INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, daily_challenge_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (daily_challenge_id) REFERENCES daily_challenges (id) ON DELETE CASCADE
    );
    ''')

    conn.commit()
    conn.close()
    print("Database schema initialized with Friends, Learn Lessons, and 10 Quiz Levels.")

if __name__ == '__main__':
    init_db()
