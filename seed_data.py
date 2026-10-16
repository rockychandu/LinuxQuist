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
         json.dumps({"files": {"app.log": "INFO: ok\nERROR: database down"}}), json.dumps({"required_commands": ["grep"]}), "vfs_state", "Type 'grep ERROR app.log'.", 100, "Medium", 1),

        (level_map[4], "Written Command Test 6 — Inspect System Processes", "quest-test-6",
         "Type the command to list running processes.",
         "Execute `ps` or `ps aux`.",
         json.dumps({"files": {}}), json.dumps({"required_commands": ["ps"]}), "vfs_state", "Type 'ps' or 'ps aux'.", 110, "Medium", 1),

        (level_map[5], "Written Command Test 7 — Superuser Command Execution", "quest-test-7",
         "Type a command using elevated privileges with sudo.",
         "Execute `sudo whoami`.",
         json.dumps({"files": {}}), json.dumps({"required_commands": ["sudo"]}), "vfs_state", "Type 'sudo whoami'.", 120, "Medium", 1),

        (level_map[6], "Written Command Test 8 — Check Network Interface", "quest-test-8",
         "Type the command to display network IP addresses.",
         "Execute `ip addr` or `ping 127.0.0.1`.",
         json.dumps({"files": {}}), json.dumps({"required_commands": ["ip", "ping"]}), "vfs_state", "Type 'ip addr' or 'ping 127.0.0.1'.", 130, "Hard", 1),

        (level_map[7], "Written Command Test 9 — Write Output Redirection", "quest-test-9",
         "Type the command to echo text into a file named `hello.txt`.",
         "Execute `echo 'Hello World' > hello.txt`.",
         json.dumps({"files": {}}), json.dumps({"required_file": "/home/hero/hello.txt"}), "vfs_state", "Type 'echo Hello > hello.txt'.", 140, "Hard", 1),

        (level_map[8], "Written Command Test 10 — Inspect Password File", "quest-test-10",
         "Type the command to display system user account definitions.",
         "Execute `cat /etc/passwd`.",
         json.dumps({"files": {}}), json.dumps({"required_commands": ["cat"]}), "vfs_state", "Type 'cat /etc/passwd'.", 150, "Hard", 1)
    ]

    for q in quests:
        cursor.execute("""
            INSERT INTO quests (level_id, title, slug, description, objective, initial_vfs_json, expected_state_json, verification_type, hint, xp_reward, difficulty, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    # 6. Seed 20 Unique Quiz Levels with 5 Questions each (100 total distinct questions)
    quiz_dataset = {
        1: {
            "title": "Level 1 Quiz — Linux Basics & Navigation",
            "desc": "Test your knowledge on Linux filesystem basics, navigation commands, and directory manipulation.",
            "questions": [
                ("Which command displays the absolute path of your current working directory?", ["ls", "pwd", "cd", "dir"], 1, "'pwd' stands for Print Working Directory."),
                ("Which 'ls' option lists all contents including hidden files starting with a dot (.)?", ["-l", "-a", "-h", "-r"], 1, "'-a' shows all files including hidden dotfiles."),
                ("What is the shorthand symbol for a user's home directory in Linux?", ["/", "~", ".", ".."], 1, "'~' represents the user home directory /home/username."),
                ("Which command creates a new empty file or updates an existing file's timestamp?", ["mkdir", "touch", "create", "new"], 1, "'touch' creates blank files or touches timestamps."),
                ("How do you move up one level to the parent directory in Linux?", ["cd .", "cd ..", "cd /", "cd ~"], 1, "'cd ..' changes directory to the parent folder.")
            ]
        },
        2: {
            "title": "Level 2 Quiz — Files, Paths & Permissions",
            "desc": "Evaluate absolute vs relative paths, octal chmod permissions, and file ownership.",
            "questions": [
                ("In octal permission notation, what mode grants 'rwxr-xr-x' access?", ["644", "755", "777", "700"], 1, "Owner=7 (rwx), Group=5 (r-x), Others=5 (r-x) -> 755."),
                ("Which numeric value corresponds to Read (4) + Write (2) access in Linux 'chmod'?", ["5", "6", "7", "4"], 1, "Read (4) + Write (2) = 6."),
                ("Which command changes file owner and group in Linux?", ["chmod", "chown", "chgrp", "useradd"], 1, "'chown' changes user and group ownership of files."),
                ("What type of path starts directly from the root '/' directory?", ["Relative path", "Absolute path", "Symbolic path", "Virtual path"], 1, "Absolute paths always begin with root '/'."),
                ("Which flag makes 'mkdir' create nested parent directories automatically?", ["-r", "-p", "-f", "-a"], 1, "'-p' creates parent directories as needed.")
            ]
        },
        3: {
            "title": "Level 3 Quiz — Text Manipulation & Pipes",
            "desc": "Inspect pattern matching with grep, output redirection, and shell piping.",
            "questions": [
                ("Which command searches files for lines matching a specified pattern?", ["find", "grep", "cat", "awk"], 1, "'grep' filters and prints matching text lines."),
                ("Which operator redirects command output to a file, overwriting existing content?", [">", ">>", "<", "|"], 0, "'>' redirects output and overwrites the file."),
                ("Which operator appends command output to the end of a file without overwriting?", [">", ">>", "|", "&"], 1, "'>>' appends output to the end of the file."),
                ("Which pipe symbol '|' sends output of one command as input to another?", ["&", "|", ">", "<"], 1, "'|' connects stdout of left command to stdin of right command."),
                ("Which command displays the first 10 lines of a file by default?", ["tail", "head", "cat", "less"], 1, "'head' displays the top 10 lines of a file.")
            ]
        },
        4: {
            "title": "Level 4 Quiz — Process & System Inspection",
            "desc": "Monitor running tasks, process IDs, memory usage, and storage stats.",
            "questions": [
                ("Which command displays an interactive real-time view of running processes?", ["ps", "top", "df", "kill"], 1, "'top' or 'htop' provides interactive live process metrics."),
                ("Which signal number corresponds to SIGKILL (forceful termination)?", ["15", "9", "1", "2"], 1, "Signal 9 is SIGKILL, which forcefully terminates a process."),
                ("Which command checks disk space usage across all mounted file systems?", ["du -sh", "df -h", "free -m", "lsblk"], 1, "'df -h' reports file system disk space in human-readable format."),
                ("Which command displays total, used, and available RAM memory in megabytes?", ["free -m", "vmstat", "top", "df"], 0, "'free -m' displays RAM usage in MB."),
                ("Which command estimates disk space consumed by files within a directory?", ["df -h", "du -sh", "fdisk", "stat"], 1, "'du -sh' summarizes directory disk space usage.")
            ]
        },
        5: {
            "title": "Level 5 Quiz — User & Permission Management",
            "desc": "Inspect user credentials, password hashes, and sudo administrative privileges.",
            "questions": [
                ("Which file stores system user account credentials, user IDs, and default shell?", ["/etc/shadow", "/etc/passwd", "/etc/group", "/etc/hosts"], 1, "/etc/passwd stores user account details."),
                ("Which file holds encrypted user password hashes accessible only by root?", ["/etc/passwd", "/etc/shadow", "/etc/sudoers", "/var/log/auth.log"], 1, "/etc/shadow contains secure password hashes."),
                ("Which command creates a new system user account in Linux?", ["usermod", "useradd", "groupadd", "chmod"], 1, "'useradd' adds new user accounts."),
                ("Which command allows a permitted user to execute commands as superuser?", ["su", "sudo", "admin", "runas"], 1, "'sudo' grants administrative privilege execution."),
                ("Which file configures administrative privileges for users and groups?", ["/etc/passwd", "/etc/sudoers", "/etc/environment", "/etc/fstab"], 1, "/etc/sudoers controls sudo access rules.")
            ]
        },
        6: {
            "title": "Level 6 Quiz — Networking & Connectivity",
            "desc": "Master IP network configuration, HTTP testing, SSH remote access, and socket inspection.",
            "questions": [
                ("Which command tests network latency and reachability via ICMP echo requests?", ["curl", "ping", "wget", "ssh"], 1, "'ping' sends ICMP echo requests to test network connectivity."),
                ("Which modern command inspects and configures network IP interfaces?", ["ip addr", "netstat", "route", "ifstat"], 0, "'ip addr' (iproute2) replaces legacy ifconfig."),
                ("Which CLI tool downloads files directly from web URLs via HTTP/HTTPS/FTP?", ["ssh", "wget", "ping", "dig"], 1, "'wget' downloads files over web protocols."),
                ("Which command establishes an encrypted secure terminal connection to a remote host?", ["telnet", "ssh", "ftp", "scp"], 1, "'ssh' provides secure encrypted remote shell access."),
                ("Which modern command displays active socket connections and listening ports?", ["ss", "lsof", "ip link", "arp"], 0, "'ss' displays socket statistics and listening ports.")
            ]
        },
        7: {
            "title": "Level 7 Quiz — Shell Scripting Foundations",
            "desc": "Evaluate shebang syntax, shell variables, arguments, and exit status codes.",
            "questions": [
                ("What line at the beginning of a script specifies the Bash interpreter path?", ["#!/bin/bash", "#bash", "//bin/bash", "!/usr/bin"], 0, "'#!/bin/bash' is the shebang line specifying the shell binary."),
                ("How do you reference the value of a variable named PORT in Bash?", ["var(PORT)", "$PORT", "&PORT", "%PORT%"], 1, "Prefixing '$' dereferences a Bash variable: $PORT."),
                ("Which special variable holds the exit status code of the last executed command?", ["$1", "$#", "$?", "$$"], 2, "'$?' contains the exit code (0 = success)."),
                ("Which variable contains the first command-line argument passed to a script?", ["$0", "$1", "$@", "$*"], 1, "'$1' holds the first script parameter ($0 is script name)."),
                ("What keyword marks the closing block of an 'if' condition in Bash?", ["endif", "fi", "done", "esac"], 1, "'fi' closes an 'if' conditional statement.")
            ]
        },
        8: {
            "title": "Level 8 Quiz — Automation & Cron Jobs",
            "desc": "Test your knowledge on cron scheduling expressions, tar archives, and loops.",
            "questions": [
                ("Which command edits the cron job table schedule for the current user?", ["crontab -l", "crontab -e", "cron -r", "systemctl cron"], 1, "'crontab -e' opens the cron table editor."),
                ("What do the 5 time fields in a crontab schedule represent in order?", ["Min Hour Day Month DayOfWeek", "Hour Min Day Month Year", "Sec Min Hour Day Month", "Day Month Hour Min Sec"], 0, "Cron order: Minute (0-59), Hour (0-23), Day of Month (1-31), Month (1-12), Day of Week (0-7)."),
                ("Which command creates a compressed gzipped tar archive 'backup.tar.gz'?", ["tar -xvf backup.tar.gz", "tar -czvf backup.tar.gz /folder", "zip backup.zip", "gzip -d backup"], 1, "'tar -czvf' creates gzip compressed archive."),
                ("Which keyword marks the end of a 'for' or 'while' loop in Bash?", ["fi", "done", "end", "esac"], 1, "'done' terminates 'for' and 'while' loop blocks."),
                ("What schedule does the cron expression '*/5 * * * *' specify?", ["Every 5 hours", "Every 5 minutes", "At 5am daily", "At minute 5 every hour"], 1, "'*/5 * * * *' executes every 5 minutes.")
            ]
        },
        9: {
            "title": "Level 9 Quiz — Package & Service Management",
            "desc": "Control systemd services, inspect journalctl logs, and manage environment variables.",
            "questions": [
                ("Which command checks the status of a systemd background service like nginx?", ["service nginx start", "systemctl status nginx", "init status nginx", "ps status nginx"], 1, "'systemctl status <service>' checks systemd service status."),
                ("Which tool queries systemd log journals and service output?", ["cat /var/log", "journalctl", "syslogd", "logrotate"], 1, "'journalctl' queries systemd logs."),
                ("Which package manager command installs software packages on Debian/Ubuntu?", ["yum install", "apt install", "dnf install", "pacman -S"], 1, "'apt install' manages Debian/Ubuntu packages."),
                ("Which command exports an environment variable for current and child processes?", ["set VAR=1", "export VAR=1", "define VAR=1", "env VAR=1"], 1, "'export VAR=val' sets process environment variables."),
                ("Which command reloads systemd manager configurations after editing service units?", ["systemctl daemon-reload", "systemctl restart", "service reload", "init 6"], 0, "'systemctl daemon-reload' parses updated unit files.")
            ]
        },
        10: {
            "title": "Level 10 Quiz — System Administrator Boss Level",
            "desc": "Troubleshoot real-world server incidents, permissions, log tailing, and socket tools.",
            "questions": [
                ("Which command monitors server logs in real-time as new lines are written?", ["head -n 50", "tail -f /var/log/syslog", "cat /var/log/syslog", "grep log"], 1, "'tail -f' continuously streams new log lines."),
                ("How do you forcibly send SIGKILL to process ID 2048?", ["kill -15 2048", "kill -9 2048", "stop 2048", "term 2048"], 1, "'kill -9 2048' forcefully kills PID 2048."),
                ("Which permission setting ensures a file is readable & writable ONLY by its owner?", ["755", "600", "644", "700"], 1, "'600' grants rw------- (owner read/write only)."),
                ("Which utility displays open files and processes holding network sockets?", ["lsof", "df", "free", "fdisk"], 0, "'lsof' lists open files and network sockets."),
                ("Which directory contains system-wide configuration files in Linux?", ["/var", "/etc", "/usr", "/opt"], 1, "/etc stores system configuration files.")
            ]
        },
        11: {
            "title": "Level 11 Quiz — Storage & Partitions",
            "desc": "Partitioning, formatting filesystems, fstab mounting, and LVM volumes.",
            "questions": [
                ("Which command lists disk partitions and block storage details?", ["df -h", "fdisk -l", "mount", "du"], 1, "'fdisk -l' lists disk partitions and layout."),
                ("Which tool formats a partition with the ext4 filesystem?", ["fdisk", "mkfs.ext4", "mount", "fsck"], 1, "'mkfs.ext4' formats partitions with ext4."),
                ("Which file configures persistent partition mounts automatically attached at boot?", ["/etc/hosts", "/etc/fstab", "/etc/mnt", "/etc/exports"], 1, "/etc/fstab stores persistent mount table entries."),
                ("In Logical Volume Management (LVM), what is initialized first from raw disk partitions?", ["Volume Group", "Physical Volume (PV)", "Logical Volume (LV)", "File System"], 1, "Physical Volumes (PV) are created first via pvcreate."),
                ("Which command checks and repairs Linux file system errors?", ["fdisk", "fsck", "mkfs", "umount"], 1, "'fsck' checks and repairs filesystem consistency.")
            ]
        },
        12: {
            "title": "Level 12 Quiz — Stream Editing (sed & awk)",
            "desc": "Master pattern substitution with sed and text parsing scripts with awk.",
            "questions": [
                ("Which 'sed' command replaces all occurrences of 'foo' with 'bar' in a file?", ["sed 's/foo/bar/g' file", "sed 'replace foo bar'", "sed 'c/foo/bar'", "grep 'foo' | bar"], 0, "'s/foo/bar/g' replaces all matching instances."),
                ("Which 'awk' command prints the first field of every line from space-delimited text?", ["awk '{print $1}' file", "awk '{print line[0]}'", "sed '{print 1}'", "cut -f0"], 0, "'$1' represents the first column in awk."),
                ("Which flag specifies a custom field delimiter in 'awk' (e.g., colon ':' for /etc/passwd)?", ["-d", "-F", "-t", "-s"], 1, "'-F:' sets the input field separator in awk."),
                ("In 'awk', what special variable represents the total number of fields in current line?", ["NR", "NF", "FS", "OFS"], 1, "'NF' holds the number of fields in the record."),
                ("In 'awk', what special variable represents the current record line number?", ["NF", "NR", "RS", "VAR"], 1, "'NR' represents the current line number.")
            ]
        },
        13: {
            "title": "Level 13 Quiz — Kernel Tuning & Sysctl",
            "desc": "Explore /proc virtual filesystem, sysctl runtime tuning, and kernel modules.",
            "questions": [
                ("Which virtual filesystem provides a direct interface to live kernel data?", ["/etc", "/proc", "/opt", "/mnt"], 1, "/proc is a virtual pseudo-filesystem exposed by the kernel."),
                ("Which command configures kernel runtime parameters dynamically without rebooting?", ["sysctl", "systemctl", "modprobe", "lsmod"], 0, "'sysctl' inspects and modifies kernel parameters."),
                ("Which command lists currently loaded Linux kernel modules?", ["insmod", "lsmod", "rmmod", "modinfo"], 1, "'lsmod' displays loaded kernel modules."),
                ("Which tool loads or unloads kernel modules with automatic dependency handling?", ["insmod", "modprobe", "depmod", "lsmod"], 1, "'modprobe' intelligently handles kernel module dependencies."),
                ("Which /proc path controls virtual memory swappiness ratio?", ["/proc/sys/vm/swappiness", "/proc/meminfo", "/proc/cpuinfo", "/proc/net"], 0, "/proc/sys/vm/swappiness tunes swap aggressiveness.")
            ]
        },
        14: {
            "title": "Level 14 Quiz — SSH Hardening & Key Auth",
            "desc": "Generate SSH keys, set permissions, and harden sshd_config.",
            "questions": [
                ("Which utility generates public and private SSH key pairs?", ["ssh-add", "ssh-keygen", "ssh-copy-id", "openssl"], 1, "'ssh-keygen' generates public/private key pairs."),
                ("Which file in ~/.ssh/ holds public keys authorized to log into the account?", ["id_rsa", "authorized_keys", "known_hosts", "config"], 1, "'authorized_keys' holds allowed user public keys."),
                ("What is the mandatory secure file permission for private key files (id_rsa)?", ["755", "600", "644", "777"], 1, "'600' (rw-------) restricts private key read access."),
                ("Which directive in /etc/ssh/sshd_config disables root SSH access?", ["RootLogin off", "PermitRootLogin no", "DisableRoot yes", "UserRoot block"], 1, "'PermitRootLogin no' prevents direct root SSH login."),
                ("Which tool copies your public key to a remote server's authorized_keys file?", ["scp", "ssh-copy-id", "rsync", "sftp"], 1, "'ssh-copy-id' installs public keys on remote systems.")
            ]
        },
        15: {
            "title": "Level 15 Quiz — Advanced Firewall & Traffic Control",
            "desc": "Inspect UFW rules, iptables packet filtering, and nftables framework.",
            "questions": [
                ("Which CLI tool provides a simplified firewall manager on Ubuntu/Debian?", ["nftables", "ufw", "firewalld", "fail2ban"], 1, "'ufw' (Uncomplicated Firewall) simplifies netfilter control."),
                ("Which command enables the UFW firewall service?", ["sudo ufw start", "sudo ufw enable", "sudo ufw run", "sudo service ufw up"], 1, "'ufw enable' activates firewall rules."),
                ("Which table in 'iptables' handles Network Address Translation and port forwarding?", ["filter", "nat", "mangle", "raw"], 1, "'nat' table manages PREROUTING/POSTROUTING translation."),
                ("Which iptables command appends a rule accepting incoming TCP port 22 traffic?", ["iptables -A INPUT -p tcp --dport 22 -j ACCEPT", "iptables allow 22", "iptables open 22", "ufw add 22"], 0, "'-A INPUT -p tcp --dport 22 -j ACCEPT' appends port 22 rule."),
                ("What modern netfilter framework is designed to succeed legacy iptables?", ["ufw", "nftables", "ebtables", "arptables"], 1, "'nftables' replaces iptables for high-performance packet filtering.")
            ]
        },
        16: {
            "title": "Level 16 Quiz — Containerization & Isolation",
            "desc": "Evaluate Linux cgroups, namespaces, chroot jails, and security isolation.",
            "questions": [
                ("Which Linux kernel feature limits and controls CPU/RAM resources per process group?", ["Namespaces", "cgroups (Control Groups)", "chroot", "SELinux"], 1, "cgroups allocate and limit system resources."),
                ("Which kernel feature isolates process IDs, network interfaces, and mount points?", ["cgroups", "Namespaces", "AppArmor", "auditd"], 1, "Linux namespaces isolate system views per container."),
                ("Which command changes the root directory for current and child processes?", ["cd /root", "chroot", "pivot_root", "mkdir"], 1, "'chroot' alters the apparent root directory."),
                ("Which namespace type provides process ID isolation so a container sees itself as PID 1?", ["MNT namespace", "PID namespace", "NET namespace", "IPC namespace"], 1, "PID namespace provides isolated process trees."),
                ("What Linux security mechanism restricts available system calls to container runtimes?", ["seccomp", "syslog", "cron", "journald"], 0, "seccomp filters unauthorized system calls.")
            ]
        },
        17: {
            "title": "Level 17 Quiz — Security Auditing & Intrusion Detection",
            "desc": "Analyze security audit logs, fail2ban intrusion prevention, and user sessions.",
            "questions": [
                ("Which daemon scans log files and dynamically bans IP addresses exhibiting brute-force attacks?", ["auditd", "fail2ban", "clamav", "snort"], 1, "'fail2ban' blocks malicious IPs based on log activity."),
                ("Which mandatory access control framework uses security labels on RHEL/CentOS systems?", ["AppArmor", "SELinux", "UFW", "PAM"], 1, "SELinux enforces mandatory access control labels."),
                ("Which log file records authentication events and SSH login attempts on Debian/Ubuntu?", ["/var/log/syslog", "/var/log/auth.log", "/var/log/messages", "/var/log/dmesg"], 1, "/var/log/auth.log records authentication attempts."),
                ("Which command displays recent user login sessions and connection history?", ["whoami", "last", "history", "w"], 1, "'last' prints system login records."),
                ("Which command inspects kernel ring buffer boot messages?", ["dmesg", "journalctl -k", "cat /var/log/boot", "syslog"], 0, "'dmesg' prints kernel ring buffer messages.")
            ]
        },
        18: {
            "title": "Level 18 Quiz — Backup, Archiving & Recovery",
            "desc": "Master rsync remote synchronization, block cloning with dd, and checksums.",
            "questions": [
                ("Which tool synchronizes files locally or remotely using efficient delta transfers?", ["cp -r", "rsync", "scp", "ftp"], 1, "'rsync' efficiently synchronizes folders."),
                ("Which flag for 'rsync' enables archive mode (preserves permissions, links, times)?", ["-v", "-a", "-z", "-r"], 1, "'-a' (archive) preserves file attributes and recurses."),
                ("Which low-level utility copies raw data byte-for-byte to clone drives or create ISOs?", ["cp", "dd", "cat", "clone"], 1, "'dd' performs block-level data duplication."),
                ("Which command computes SHA-256 cryptographic checksums for data verification?", ["md5sum", "sha256sum", "cksum", "hash"], 1, "'sha256sum' generates SHA-256 digests."),
                ("Which compression utility generates compressed archives with '.bz2' extension?", ["gzip", "bzip2", "xz", "zip"], 1, "'bzip2' creates bz2 compressed files.")
            ]
        },
        19: {
            "title": "Level 19 Quiz — System Bootloader & Rescue",
            "desc": "GRUB2 configuration, initramfs image loading, and emergency recovery targets.",
            "questions": [
                ("What is the primary bootloader used by modern Linux distributions?", ["LILO", "GRUB2", "Syslinux", "Systemd-boot"], 1, "GRUB2 is the default bootloader for Linux."),
                ("Which file in Ubuntu/Debian is edited to configure GRUB defaults before running update-grub?", ["/etc/grub.conf", "/etc/default/grub", "/boot/grub/grub.cfg", "/etc/boot"], 1, "/etc/default/grub contains main GRUB settings."),
                ("Which command generates the final /boot/grub/grub.cfg file?", ["grub-install", "grub-mkconfig -o /boot/grub/grub.cfg", "grub-setup", "update-boot"], 1, "'grub-mkconfig' builds grub.cfg configuration."),
                ("What initial RAM filesystem is loaded into memory by GRUB to mount root?", ["vmlinuz", "initramfs", "swap", "GRUB"], 1, "initramfs provides early boot drivers to mount root."),
                ("Which systemd target provides a single-user emergency maintenance shell?", ["multi-user.target", "emergency.target", "graphical.target", "reboot.target"], 1, "emergency.target loads minimal rescue shell.")
            ]
        },
        20: {
            "title": "Level 20 Quiz — Master Architect Certification",
            "desc": "Comprehensive master evaluation across system architecture, security, and administration.",
            "questions": [
                ("Which command finds all '.log' files in /var/log larger than 50MB and removes them?", ["find /var/log -name '*.log' -size +50M -exec rm -f {} +", "rm -rf /var/log/*.log", "grep 50M | rm", "clean log"], 0, "'find' with '-exec rm' safely purges matching files."),
                ("In Linux networking, which file maps hostnames to IP addresses locally before DNS?", ["/etc/resolv.conf", "/etc/hosts", "/etc/networks", "/etc/nsswitch.conf"], 1, "/etc/hosts contains local static IP-to-hostname mappings."),
                ("Which file configures DNS nameservers used for domain name resolution?", ["/etc/hosts", "/etc/resolv.conf", "/etc/named.conf", "/etc/bind"], 1, "/etc/resolv.conf specifies upstream DNS servers."),
                ("Which security auditing tool performs automated system hardening & compliance scans?", ["lynis", "top", "df", "fdisk"], 0, "'lynis' performs security audits and vulnerability scans."),
                ("Congratulations! What official title do you earn upon mastering LinuxQuest Level 20?", ["Certified Linux User", "Certified Linux Architect", "System Administrator Novice", "Terminal Specialist"], 1, "Level 20 unlocks official LinuxQuest Certified Linux Architect status!")
            ]
        }
    }

    for ql_num in range(1, 21):
        qdata = quiz_dataset[ql_num]
        cursor.execute("""
            INSERT INTO quiz_levels (quiz_level_number, title, description, xp_reward)
            VALUES (?, ?, ?, ?)
        """, (ql_num, qdata["title"], qdata["desc"], 100))

        cursor.execute("SELECT id FROM quiz_levels WHERE quiz_level_number = ?;", (ql_num,))
        ql_id = cursor.fetchone()['id']

        for question in qdata["questions"]:
            q_text, opts, correct_idx, expl = question
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_level_id, question_text, options_json, correct_answer_index, explanation)
                VALUES (?, ?, ?, ?, ?)
            """, (ql_id, q_text, json.dumps(opts), correct_idx, expl))

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
