import sqlite3
import json
import os
from werkzeug.security import generate_password_hash
from database import get_db, init_db
from datetime import date, timedelta

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    print("Seeding database with 20 Levels, 10 Learn Lessons, 10 Quiz Levels (5 questions each), Friends, and Written Command Quests...")

    # Clear existing data
    cursor.execute("DELETE FROM user_learn_progress;")
    cursor.execute("DELETE FROM learn_lessons;")
    cursor.execute("DELETE FROM quiz_questions;")
    cursor.execute("DELETE FROM quiz_levels;")
    cursor.execute("DELETE FROM friends;")
    cursor.execute("DELETE FROM certificates;")
    cursor.execute("DELETE FROM daily_challenge_completions;")
    cursor.execute("DELETE FROM daily_challenges;")
    cursor.execute("DELETE FROM user_achievements;")
    cursor.execute("DELETE FROM user_quiz_attempts;")
    cursor.execute("DELETE FROM user_quest_attempts;")
    cursor.execute("DELETE FROM user_lesson_progress;")
    cursor.execute("DELETE FROM xp_transactions;")
    cursor.execute("DELETE FROM achievements;")
    cursor.execute("DELETE FROM quizzes;")
    cursor.execute("DELETE FROM quests;")
    cursor.execute("DELETE FROM lessons;")
    cursor.execute("DELETE FROM levels;")
    cursor.execute("DELETE FROM users;")

    # 1. Create Default Users
    admin_pw = generate_password_hash("admin123")
    hero_pw = generate_password_hash("hero123")

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, level, xp, streak, longest_streak, avatar, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("admin", "admin@linuxquest.org", admin_pw, "admin", 20, 35000, 30, 30, "root_avatar.png", "System Administrator & LinuxQuest Admin"))

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, level, xp, streak, longest_streak, avatar, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("hero", "hero@linuxquest.org", hero_pw, "user", 5, 3600, 7, 12, "terminal_hero.png", "Aspiring SysAdmin on a Linux Quest"))

    # Demo leaderboard users
    demo_users = [
        ("linus_t", "linus@kernel.org", generate_password_hash("demo123"), "user", 20, 48000, 95, 95, "avatar_linus.png", "Creator of the Kernel"),
        ("tux_hero", "tux@penguin.org", generate_password_hash("demo123"), "user", 16, 28500, 45, 50, "avatar_tux.png", "Penguin Commander"),
        ("cyber_grep", "grep@sec.io", generate_password_hash("demo123"), "user", 12, 18400, 28, 30, "avatar_cyber.png", "Text Filter Specialist"),
        ("bash_wizard", "bash@shell.com", generate_password_hash("demo123"), "user", 9, 12100, 14, 20, "avatar_wizard.png", "Master of Shell Scripts"),
        ("root_commander", "root@sys.net", generate_password_hash("demo123"), "user", 7, 8500, 10, 15, "avatar_root.png", "Permission Defender")
    ]

    for u in demo_users:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, level, xp, streak, longest_streak, avatar, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, u)

    # 2. Seed Friends Connections
    cursor.execute("SELECT id, username FROM users;")
    u_map = {r['username']: r['id'] for r in cursor.fetchall()}
    
    friends_pairs = [
        (u_map['hero'], u_map['admin']),
        (u_map['hero'], u_map['linus_t']),
        (u_map['hero'], u_map['tux_hero']),
        (u_map['admin'], u_map['cyber_grep'])
    ]
    for p in friends_pairs:
        cursor.execute("INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'accepted')", p)

    # 3. Seed 20 Levels
    levels = [
        (1, "Level 1 — Linux Basics & Navigation", "Discover Linux history, standard filesystem structure, and essential navigation commands: pwd, ls, cd, mkdir, touch.", "fa-terminal", 0),
        (2, "Level 2 — Files, Paths & Permissions", "Master absolute vs relative paths, hidden files, chmod permissions (rwx, octal notation), and chown ownership.", "fa-folder-open", 500),
        (3, "Level 3 — Text Manipulation & Pipes", "Learn text inspection commands (cat, less, head, tail), search patterns with grep, text sorting, piping (|), and redirection.", "fa-file-code", 1200),
        (4, "Level 4 — Process & System Inspection", "Monitor system tasks with ps, top, htop, kill processes by PID, check storage usage with df/du, and inspect memory.", "fa-microchip", 2200),
        (5, "Level 5 — User & Permission Management", "Manage users and groups with useradd, usermod, passwd, /etc/passwd inspection, and administrative elevation with sudo.", "fa-user-shield", 3500),
        (6, "Level 6 — Networking & Connectivity", "Master networking tools: ping, curl, wget, ssh remote access, inspecting IP addresses with ip addr, and checking open ports.", "fa-network-wired", 5000),
        (7, "Level 7 — Shell Scripting Foundations", "Automate tasks using Bash scripts: variables, positional arguments, conditional if/else logic, exit codes, and functions.", "fa-code", 7000),
        (8, "Level 8 — Automation & Cron Jobs", "Construct robust bash loops (for, while), parse command output, build automated backups, handle script error trapping, and cron jobs.", "fa-robot", 9500),
        (9, "Level 9 — Package & Service Management", "Control background services with systemd/systemctl, inspect journalctl logs, install packages with apt/yum, and environment vars.", "fa-cogs", 12500),
        (10, "Level 10 — System Administrator Boss Level", "Troubleshoot real-world server crashes, restore broken permissions, analyze security breach logs, and secure the environment.", "fa-crown", 16000),
        (11, "Level 11 — Linux Storage & Partitions", "Block devices, fdisk partitioning, mkfs file systems, LVM volume groups, and persistent /etc/fstab mounting.", "fa-database", 20000),
        (12, "Level 12 — Stream Editing (sed & awk)", "Master stream editing with sed pattern substitution and data extraction with awk scripts.", "fa-magic", 24500),
        (13, "Level 13 — Kernel Tuning & Sysctl", "Inspect Linux kernel parameters with sysctl, load kernel modules with lsmod/modprobe, and tune OS performance.", "fa-sliders-h", 29500),
        (14, "Level 14 — SSH Hardening & Key Auth", "Configure secure SSH key-based authentication with ssh-keygen and harden /etc/ssh/sshd_config.", "fa-key", 35000),
        (15, "Level 15 — Advanced Firewall & Traffic Control", "Construct complex packet filtering rules with iptables and nftables, and configure UFW rate limiting.", "fa-fire-alt", 41000),
        (16, "Level 16 — Containerization & Isolation", "Understand Linux cgroups, namespaces, chroot jail environments, and container CLI tools.", "fa-box-open", 47500),
        (17, "Level 17 — Security Auditing & Intrusion Detection", "Analyze security audit logs with auditd, configure automated intrusion prevention with fail2ban.", "fa-user-secret", 54500),
        (18, "Level 18 — Backup, Archiving & Recovery", "Master tar archives, gzip compression, automated remote folder syncing with rsync, and block cloning with dd.", "fa-archive", 62000),
        (19, "Level 19 — System Bootloader & Rescue", "Diagnose GRUB bootloader errors, kernel panic recovery, chroot rescue environments.", "fa-life-ring", 70000),
        (20, "Level 20 — Ultimate Linux Architect Certification", "Pass the comprehensive master exam covering end-to-end Linux architecture and unlock your official Certificate!", "fa-certificate", 79000)
    ]

    for lvl in levels:
        cursor.execute("""
            INSERT INTO levels (level_number, title, description, icon, required_xp)
            VALUES (?, ?, ?, ?, ?)
        """, lvl)

    cursor.execute("SELECT id, level_number FROM levels;")
    level_map = {row['level_number']: row['id'] for row in cursor.fetchall()}

    # 4. Seed 10 Learn Lessons (Up to 10 Lessons under /learn)
    learn_lessons = [
        (1, "Lesson 1: Introduction to Linux & Kernel Architecture", "intro-linux-kernel",
         "Learn the core architecture of Linux, standard Unix hierarchy, and command prompt structure.",
         "# Lesson 1: Introduction to Linux & Kernel Architecture\n\nLinux is an open-source Unix-like kernel created by Linus Torvalds in 1991.\n\nKey Concepts:\n- Kernel vs User Space\n- Everything is a file in Linux!\n- Terminal Prompt syntax: user@host:path$",
         json.dumps([{"cmd": "whoami", "desc": "Check current user"}, {"cmd": "uname -a", "desc": "Check kernel version"}]), 10, 75),

        (2, "Lesson 2: Directory Navigation (pwd, ls, cd)", "directory-navigation",
         "Master Print Working Directory, listing directory contents, and navigating paths.",
         "# Lesson 2: Directory Navigation\n\nNavigation is the most fundamental CLI skill.\n\nCommands:\n- `pwd`: Print current path\n- `ls -la`: List all files with permissions\n- `cd /var/log`: Move to folder",
         json.dumps([{"cmd": "pwd", "desc": "Print working dir"}, {"cmd": "ls -lh", "desc": "Human-readable file listing"}]), 12, 75),

        (3, "Lesson 3: File Creation & Deletion (touch, mkdir, rm)", "file-creation-deletion",
         "Learn to create files with touch, directories with mkdir, and safely remove files with rm.",
         "# Lesson 3: File Creation & Deletion\n\nCreate files with `touch filename.txt` and folders with `mkdir folder`.\nDelete files with `rm filename` and folders with `rm -r folder`.",
         json.dumps([{"cmd": "mkdir -p docs/notes", "desc": "Create nested folders"}, {"cmd": "touch docs/notes/todo.txt", "desc": "Create blank file"}]), 15, 80),

        (4, "Lesson 4: File Permissions & Octal chmod Notation", "permissions-chmod",
         "Understand rwx permission bits, owner/group/others, and octal numeric modes (755, 600).",
         "# Lesson 4: File Permissions & chmod\n\nPermissions define Read (4), Write (2), and Execute (1) access.\nExample: `chmod 755 script.sh` grants rwx to owner and r-x to group/others.",
         json.dumps([{"cmd": "chmod +x deploy.sh", "desc": "Make script executable"}, {"cmd": "chmod 600 id_rsa", "desc": "Set private file mode"}]), 18, 90),

        (5, "Lesson 5: Text Inspection & Grep Pattern Filtering", "text-cat-grep",
         "Inspect text files with cat, head, tail, and filter logs with grep.",
         "# Lesson 5: Text Inspection & grep\n\nRead files using `cat`, `head -n 20`, or `tail -f /var/log/syslog`.\nSearch text patterns using `grep -i 'error' server.log`.",
         json.dumps([{"cmd": "grep -i 'failed' /var/log/auth.log", "desc": "Search failed logins"}, {"cmd": "head -n 10 /etc/passwd", "desc": "View top 10 user lines"}]), 15, 85),

        (6, "Lesson 6: Process Monitoring & Signals (ps, top, kill)", "process-ps-top-kill",
         "Inspect running tasks with ps aux and top, and terminate rogue PIDs with kill -9.",
         "# Lesson 6: Process Monitoring\n\nEvery executing program has a Process ID (PID).\nUse `ps aux` to find PIDs and `kill -9 <PID>` to stop runaway processes.",
         json.dumps([{"cmd": "ps aux | grep python", "desc": "Find Python process PID"}, {"cmd": "kill -9 4096", "desc": "Force kill PID 4096"}]), 15, 90),

        (7, "Lesson 7: User Management & Sudo Privileges", "user-management-sudo",
         "Manage system users with useradd, usermod, passwd, and elevate commands with sudo.",
         "# Lesson 7: User Management & sudo\n\nRoot is superuser ID 0. Admin commands require `sudo` elevation.\nAdd users: `sudo useradd -m alice`.",
         json.dumps([{"cmd": "sudo useradd -m developer", "desc": "Create user with home folder"}, {"cmd": "sudo passwd developer", "desc": "Set user password"}]), 18, 100),

        (8, "Lesson 8: Networking Diagnostics (ping, ip, curl)", "networking-ip-curl",
         "Inspect local network interfaces with ip addr, test connectivity with ping, and test HTTP APIs with curl.",
         "# Lesson 8: Networking Diagnostics\n\nCheck IP settings with `ip addr` and test web endpoints with `curl -I https://api.linuxquest.org`.",
         json.dumps([{"cmd": "ip addr show", "desc": "Display local IP interfaces"}, {"cmd": "curl -I https://google.com", "desc": "Fetch HTTP response headers"}]), 20, 100),

        (9, "Lesson 9: Bash Scripting & Automation Loops", "bash-scripting-loops",
         "Write automated shell scripts with shebang #!/bin/bash, variables, arguments, and loops.",
         "# Lesson 9: Bash Scripting & Loops\n\nAutomate tasks using scripts:\n```bash\n#!/bin/bash\nfor FILE in *.txt; do\n  echo \"Processing $FILE\"\ndone\n```",
         json.dumps([{"cmd": "./backup.sh production", "desc": "Run script with argument"}, {"cmd": "crontab -l", "desc": "View cron schedule"}]), 22, 110),

        (10, "Lesson 10: System Administrator Hardening & Troubleshooting", "sysadmin-hardening",
         "Diagnose disk space exhaustion with df/du, inspect open ports with ss, and enable firewall protection with ufw.",
         "# Lesson 10: System Administrator Hardening\n\nAudit server health:\n1. Disk space: `df -h`\n2. Open sockets: `ss -tulpn`\n3. Enable firewall: `sudo ufw enable`",
         json.dumps([{"cmd": "df -h", "desc": "Check disk space"}, {"cmd": "sudo ufw status", "desc": "Inspect firewall rules"}]), 25, 125)
    ]

    for ll in learn_lessons:
        cursor.execute("""
            INSERT INTO learn_lessons (lesson_number, title, slug, summary, content_md, command_examples_json, estimated_minutes, xp_reward)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ll)

    # 5. Seed 20 Written Command Test Quests
    quests = [
        (level_map[1], "Written Command Test 1 — Confirm Location", "quest-test-1",
         "Type the exact command to display your current working directory.",
         "Execute `pwd` in the written command input box below.",
         json.dumps({"files": {}}), json.dumps({"required_commands": ["pwd"]}), "vfs_state", "Type 'pwd' and submit.", 50, "Easy", 1),

        (level_map[1], "Written Command Test 2 — List Files", "quest-test-2",
         "Type the command to list all directory contents including hidden dotfiles.",
         "Execute `ls -a` or `ls -la`.",
         json.dumps({"files": {".secret": "hidden"}}), json.dumps({"required_commands": ["ls -a", "ls -la"]}), "vfs_state", "Type 'ls -a'.", 60, "Easy", 2),

        (level_map[2], "Written Command Test 3 — Create Workspace Directory", "quest-test-3",
         "Type the command to create a directory named `workspace`.",
         "Execute `mkdir workspace`.",
         json.dumps({"files": {}}), json.dumps({"required_file": "/home/hero/workspace"}), "vfs_state", "Type 'mkdir workspace'.", 75, "Easy", 1),

        (level_map[2], "Written Command Test 4 — Grant Executable Permission", "quest-test-4",
         "Type the command to make script `run.sh` executable by adding the execution bit.",
         "Execute `chmod +x run.sh` or `chmod 755 run.sh`.",
         json.dumps({"files": {"run.sh": {"content": "#!/bin/bash\necho Hi", "perm": "644"}}}), json.dumps({"required_perm": {"/home/hero/run.sh": "executable"}}), "vfs_state", "Type 'chmod +x run.sh'.", 90, "Medium", 2),

        (level_map[3], "Written Command Test 5 — Filter Error Log Entries", "quest-test-5",
         "Type the command to search for the pattern 'ERROR' in file `app.log`.",
         "Execute `grep 'ERROR' app.log`.",
         json.dumps({"files": {"app.log": "INFO: ok\nERROR: database down"}}), json.dumps({"required_commands": ["grep"]}), "vfs_state", "Type 'grep ERROR app.log'.", 100, "Medium", 1)
    ]

    for q in quests:
        cursor.execute("""
            INSERT INTO quests (level_id, title, slug, description, objective, initial_vfs_json, expected_state_json, verification_type, hint, xp_reward, difficulty, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    # 6. Seed 10 Quiz Levels with 5 Questions each (50 total questions)
    for ql_num in range(1, 11):
        cursor.execute("""
            INSERT INTO quiz_levels (quiz_level_number, title, description, xp_reward)
            VALUES (?, ?, ?, ?)
        """, (ql_num, f"Quiz Level {ql_num} — Linux Mastery Test", f"Level {ql_num} contains 5 random daily-shuffled Linux evaluation questions.", 100))

        cursor.execute("SELECT id FROM quiz_levels WHERE quiz_level_number = ?;", (ql_num,))
        ql_id = cursor.fetchone()['id']

        # 5 Questions per level
        questions = [
            (ql_id, f"Level {ql_num} Q1: Which command displays current working directory?", json.dumps(["ls", "pwd", "cd", "where"]), 1, "'pwd' stands for Print Working Directory."),
            (ql_id, f"Level {ql_num} Q2: Which flag for 'ls' shows hidden files?", json.dumps(["-h", "-a", "-l", "-r"]), 1, "'-a' shows all files including hidden dotfiles."),
            (ql_id, f"Level {ql_num} Q3: What octal value represents Read (4) + Execute (1)?", json.dumps(["5", "6", "7", "3"]), 0, "4 + 1 = 5."),
            (ql_id, f"Level {ql_num} Q4: Which command sends a termination signal to a PID?", json.dumps(["stop", "top", "kill", "ps"]), 2, "'kill' sends signals to PIDs."),
            (ql_id, f"Level {ql_num} Q5: What file contains user account definitions in Linux?", json.dumps(["/etc/passwd", "/var/log", "/etc/hosts", "/home/users"]), 0, "/etc/passwd stores user account details.")
        ]

        for question in questions:
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_level_id, question_text, options_json, correct_answer_index, explanation)
                VALUES (?, ?, ?, ?, ?)
            """, question)

    # 7. Seed Achievements
    achievements = [
        ("first_command", "First Command", "Executed your first Linux command.", "fa-terminal", "terminal", "commands_executed", 1, 50),
        ("level_10_reached", "SysAdmin Candidate", "Reached Level 10.", "fa-shield-alt", "level", "user_level", 10, 500),
        ("level_20_reached", "Certified Linux Architect", "Completed Level 20 & unlocked official certificate!", "fa-certificate", "level", "user_level", 20, 2000)
    ]

    for ach in achievements:
        cursor.execute("""
            INSERT INTO achievements (key, title, description, icon, category, required_metric, required_value, xp_reward)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ach)

    # 8. Seed Daily Challenge
    today = date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT id FROM quests ORDER BY id ASC LIMIT 1;")
    q_row = cursor.fetchone()
    q_id = q_row['id'] if q_row else 1

    cursor.execute("""
        INSERT INTO daily_challenges (date_str, title, description, quest_id, bonus_xp)
        VALUES (?, ?, ?, ?, ?)
    """, (today, "Daily System & Log Audit", "Clean up cache files and inspect log entries to earn bonus XP today!", q_id, 150))

    conn.commit()
    conn.close()
    print("Database seeded with 20 Levels, 10 Learn Lessons, 10 Quiz Levels (5 questions each), Friends, and Written Command Quests!")

if __name__ == '__main__':
    seed_database()
