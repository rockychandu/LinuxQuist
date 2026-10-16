/* ==========================================================================
   LINUXQUEST — ENHANCED VIRTUAL FILE SYSTEM & TERMINAL SIMULATOR ENGINE
   Features: POSIX VFS, Tab-completion, Nano inline editor, Bash script runner,
   Man pages integration, Process simulation, and Quest Verification.
   ========================================================================== */

class VirtualFileSystem {
  constructor(initialVFS = null) {
    this.root = {
      type: 'dir',
      name: '/',
      owner: 'root',
      perm: 'rwxr-xr-x',
      children: {
        'home': {
          type: 'dir',
          name: 'home',
          owner: 'root',
          perm: 'rwxr-xr-x',
          children: {
            'hero': {
              type: 'dir',
              name: 'hero',
              owner: 'hero',
              perm: 'rwxr-xr-x',
              children: {
                'notes.txt': { type: 'file', name: 'notes.txt', owner: 'hero', perm: 'rw-r--r--', content: 'Welcome to LinuxQuest!\nMaster commands, complete quests, earn XP!\nPractice scripting, permissions, and network commands.' },
                'welcome.sh': { type: 'file', name: 'welcome.sh', owner: 'hero', perm: 'rwxr-xr-x', content: '#!/bin/bash\necho "LinuxQuest VFS Environment Active"\necho "Kernel: 6.8.0-linuxquest-posix"\nuptime' }
              }
            }
          }
        },
        'var': {
          type: 'dir',
          name: 'var',
          owner: 'root',
          perm: 'rwxr-xr-x',
          children: {
            'log': {
              type: 'dir',
              name: 'log',
              owner: 'root',
              perm: 'rwxr-xr-x',
              children: {
                'syslog': { type: 'file', name: 'syslog', owner: 'root', perm: 'rw-r--r--', content: 'INFO: System booted successfully.\nINFO: Network interface eth0 up (192.168.1.100).\nCRITICAL: Database connection failed at 10:00:05.\nCRITICAL: Auth service offline.\nINFO: Worker threads initialized (PID: 1042).\nINFO: Backup daemon started (PID: 1337).' },
                'auth.log': { type: 'file', name: 'auth.log', owner: 'root', perm: 'rw-r-----', content: 'Aug 25 10:00:01 server sshd[1024]: Accepted password for hero from 192.168.1.100 port 52140 ssh2\nAug 25 10:05:12 server sudo: hero : TTY=pts/0 ; PWD=/home/hero ; USER=root ; COMMAND=/bin/systemctl restart nginx' }
              }
            }
          }
        },
        'etc': {
          type: 'dir',
          name: 'etc',
          owner: 'root',
          perm: 'rwxr-xr-x',
          children: {
            'passwd': { type: 'file', name: 'passwd', owner: 'root', perm: 'rw-r--r--', content: 'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nhero:x:1000:1000:Hero User:/home/hero:/bin/bash\nquestbot:x:1001:1001:Quest Bot:/home/questbot:/bin/bash' },
            'hostname': { type: 'file', name: 'hostname', owner: 'root', perm: 'rw-r--r--', content: 'linuxquest-srv01' },
            'hosts': { type: 'file', name: 'hosts', owner: 'root', perm: 'rw-r--r--', content: '127.0.0.1 localhost\n127.0.1.1 linuxquest-srv01\n192.168.1.1 gateway.local' },
            'resolv.conf': { type: 'file', name: 'resolv.conf', owner: 'root', perm: 'rw-r--r--', content: 'nameserver 1.1.1.1\nnameserver 8.8.8.8' }
          }
        },
        'bin': {
          type: 'dir',
          name: 'bin',
          owner: 'root',
          perm: 'rwxr-xr-x',
          children: {
            'bash': { type: 'file', name: 'bash', owner: 'root', perm: 'rwxr-xr-x', content: '[ELF Binary]' },
            'ls': { type: 'file', name: 'ls', owner: 'root', perm: 'rwxr-xr-x', content: '[ELF Binary]' },
            'grep': { type: 'file', name: 'grep', owner: 'root', perm: 'rwxr-xr-x', content: '[ELF Binary]' },
            'cat': { type: 'file', name: 'cat', owner: 'root', perm: 'rwxr-xr-x', content: '[ELF Binary]' }
          }
        }
      }
    };

    if (initialVFS) {
      this.loadCustomVFS(initialVFS);
    }
  }

  loadCustomVFS(vfsData) {
    if (vfsData.files) {
      for (const [path, data] of Object.entries(vfsData.files)) {
        const content = typeof data === 'string' ? data : (data.content || '');
        const perm = typeof data === 'object' && data.perm ? data.perm : 'rw-r--r--';
        this.createFile(path, content, perm);
      }
    }
    if (vfsData.directories) {
      for (const dirPath of Object.keys(vfsData.directories)) {
        this.createDirectory(dirPath);
      }
    }
  }

  normalizePath(pathStr, cwd = '/home/hero') {
    if (!pathStr) return cwd;
    let absolute = pathStr.startsWith('/') ? pathStr : `${cwd}/${pathStr}`;
    absolute = absolute.replace(/~/g, '/home/hero');
    
    const parts = absolute.split('/').filter(p => p.length > 0 && p !== '.');
    const stack = [];
    
    for (const part of parts) {
      if (part === '..') {
        if (stack.length > 0) stack.pop();
      } else {
        stack.push(part);
      }
    }
    return '/' + stack.join('/');
  }

  getNode(pathStr, cwd = '/home/hero') {
    const absPath = this.normalizePath(pathStr, cwd);
    if (absPath === '/') return this.root;
    
    const parts = absPath.split('/').filter(Boolean);
    let current = this.root;
    
    for (const part of parts) {
      if (!current.children || !current.children[part]) {
        return null;
      }
      current = current.children[part];
    }
    return current;
  }

  createFile(pathStr, content = '', perm = 'rw-r--r--', cwd = '/home/hero') {
    const absPath = this.normalizePath(pathStr, cwd);
    const lastSlash = absPath.lastIndexOf('/');
    const dirPath = absPath.substring(0, lastSlash) || '/';
    const fileName = absPath.substring(lastSlash + 1);

    const parentNode = this.getNode(dirPath);
    if (!parentNode || parentNode.type !== 'dir') {
      this.createDirectory(dirPath);
    }
    
    const targetDir = this.getNode(dirPath);
    if (!targetDir || targetDir.type !== 'dir') return false;

    if (!targetDir.children) targetDir.children = {};
    targetDir.children[fileName] = {
      type: 'file',
      name: fileName,
      owner: 'hero',
      perm: perm,
      content: content
    };
    return true;
  }

  createDirectory(pathStr, cwd = '/home/hero') {
    const absPath = this.normalizePath(pathStr, cwd);
    const parts = absPath.split('/').filter(Boolean);
    let current = this.root;

    for (const part of parts) {
      if (!current.children) current.children = {};
      if (!current.children[part]) {
        current.children[part] = {
          type: 'dir',
          name: part,
          owner: 'hero',
          perm: 'rwxr-xr-x',
          children: {}
        };
      }
      current = current.children[part];
    }
    return true;
  }

  removePath(pathStr, cwd = '/home/hero') {
    const absPath = this.normalizePath(pathStr, cwd);
    const lastSlash = absPath.lastIndexOf('/');
    const dirPath = absPath.substring(0, lastSlash) || '/';
    const targetName = absPath.substring(lastSlash + 1);

    const parentNode = this.getNode(dirPath);
    if (!parentNode || !parentNode.children || !parentNode.children[targetName]) return false;

    delete parentNode.children[targetName];
    return true;
  }

  exportState() {
    const files = {};
    const traverse = (node, currentPath) => {
      if (node.type === 'file') {
        files[currentPath] = { content: node.content, perm: node.perm, owner: node.owner };
      } else if (node.type === 'dir' && node.children) {
        for (const [name, child] of Object.entries(node.children)) {
          const path = currentPath === '/' ? `/${name}` : `${currentPath}/${name}`;
          traverse(child, path);
        }
      }
    };
    traverse(this.root, '/');
    return { files };
  }

  renderTreeHTML(node = this.root, currentPath = '') {
    if (node.type === 'file') {
      const isExec = node.perm && node.perm.includes('x');
      const icon = isExec ? 'fa-cog text-green' : 'fa-file-alt text-cyan';
      return `<div class="tree-item file"><i class="fas ${icon}"></i> ${node.name} <span style="font-size:0.7rem; color:var(--text-muted);">${node.perm}</span></div>`;
    }
    
    let html = `<div class="tree-item dir"><i class="fas fa-folder text-gold"></i> <strong>${node.name || '/'}</strong></div>`;
    if (node.children) {
      html += `<div class="tree-children" style="padding-left: 1rem; border-left: 1px dashed rgba(0,243,255,0.2);">`;
      for (const childName of Object.keys(node.children).sort()) {
        html += this.renderTreeHTML(node.children[childName]);
      }
      html += `</div>`;
    }
    return html;
  }

  searchFiles(namePattern, startPath = '/') {
    const results = [];
    const traverse = (node, currentPath) => {
      if (node.type === 'file') {
        if (!namePattern || node.name.includes(namePattern) || namePattern === '*') {
          results.push(currentPath);
        }
      } else if (node.type === 'dir' && node.children) {
        for (const [name, child] of Object.entries(node.children)) {
          const path = currentPath === '/' ? `/${name}` : `${currentPath}/${name}`;
          traverse(child, path);
        }
      }
    };
    const startNode = this.getNode(startPath);
    if (startNode) traverse(startNode, startPath);
    return results;
  }
}

class TerminalSimulator {
  constructor(containerId, questData = null) {
    this.container = document.getElementById(containerId);
    let initialVFS = null;
    if (questData && questData.initial_vfs_json) {
      if (typeof questData.initial_vfs_json === 'string') {
        try {
          initialVFS = JSON.parse(questData.initial_vfs_json);
        } catch (e) {
          console.error("Error parsing initial_vfs_json:", e);
          initialVFS = null;
        }
      } else {
        initialVFS = questData.initial_vfs_json;
      }
    }
    this.vfs = new VirtualFileSystem(initialVFS);
    this.cwd = '/home/hero';
    this.user = 'hero';
    this.history = [];
    this.historyIdx = -1;
    this.quest = questData;
    this.questCompleted = false;
    this.processes = [
      { pid: 1, user: 'root', cpu: '0.0', mem: '0.2', cmd: '/sbin/init' },
      { pid: 104, user: 'root', cpu: '0.1', mem: '0.5', cmd: '/lib/systemd/systemd-journald' },
      { pid: 512, user: 'root', cpu: '0.0', mem: '0.4', cmd: '/usr/sbin/sshd -D' },
      { pid: 1042, user: 'hero', cpu: '0.2', mem: '1.4', cmd: 'python3 -m app.worker' },
      { pid: 1337, user: 'hero', cpu: '1.1', mem: '3.8', cmd: 'bash /home/hero/monitor.sh' },
      { pid: 2048, user: 'hero', cpu: '0.0', mem: '0.8', cmd: '-bash' }
    ];
    
    this.init();
  }

  init() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="terminal-window" style="box-shadow: 0 10px 30px rgba(0,0,0,0.6); border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; background: #070a12;">
        <div class="terminal-header" style="background: #0f1422; padding: 0.6rem 1rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-subtle);">
          <div class="terminal-dots" style="display:flex; gap:6px;">
            <span class="dot dot-red" style="width:12px; height:12px; border-radius:50%; background:#ff5f56; display:inline-block;"></span>
            <span class="dot dot-yellow" style="width:12px; height:12px; border-radius:50%; background:#ffbd2e; display:inline-block;"></span>
            <span class="dot dot-green" style="width:12px; height:12px; border-radius:50%; background:#27c93f; display:inline-block;"></span>
          </div>
          <div class="terminal-title" style="font-family: var(--font-code); font-size: 0.85rem; color: #8a99ad;">
            <i class="fas fa-terminal"></i> bash - linuxquest@hero: ${this.cwd}
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <span style="font-size:0.75rem; color:var(--text-muted); cursor:pointer;" onclick="window.terminalInstance && window.terminalInstance.clearTerminal()" title="Clear screen (Ctrl+L)"><i class="fas fa-eraser"></i></span>
            <i class="fas fa-volume-up sound-toggle-icon" onclick="window.soundEngine && window.soundEngine.toggleMute()" style="cursor:pointer; color:var(--neon-cyan);" title="Toggle Sound"></i>
          </div>
        </div>
        <div class="terminal-body" id="termBody" style="min-height: 380px; max-height: 480px; overflow-y: auto; padding: 1rem; font-family: var(--font-code); font-size: 0.9rem; line-height: 1.5; color: #d8e2ec;">
          <div class="terminal-line"><span style="color:#00ff9d; font-weight:bold;">Welcome to LinuxQuest POSIX Terminal Simulator v3.0</span></div>
          <div class="terminal-line"><span style="color:#8a99ad;">Type <strong style="color:#00f3ff;">help</strong> for command index, <strong style="color:#ffbe0b;">nano &lt;file&gt;</strong> to edit files, or press <kbd style="background:#1b2438; padding:2px 6px; border-radius:4px; font-size:0.8rem; color:#00f3ff;">Tab</kbd> for autocomplete.</span></div>
        </div>
        <div class="terminal-input-wrapper" style="padding: 0.75rem 1rem; background: #0b0f19; border-top: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 0.5rem;">
          <span class="terminal-prompt" id="termPrompt" style="color: var(--neon-green); font-family: var(--font-code); font-weight: bold; white-space: nowrap;">${this.user}@linuxquest:${this.cwd}$</span>
          <input type="text" class="terminal-input" id="termInput" autocomplete="off" spellcheck="false" placeholder="Type a Linux command..." style="flex:1; background:transparent; border:none; color:#fff; font-family:var(--font-code); font-size:0.95rem; outline:none;">
        </div>
      </div>

      <!-- INLINE NANO EDITOR MODAL -->
      <div id="nanoModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.85); z-index:9999; justify-content:center; align-items:center;">
        <div style="width: 80%; max-width: 820px; background:#080c16; border:2px solid var(--neon-cyan); border-radius:8px; overflow:hidden; box-shadow:0 0 30px rgba(0,243,255,0.3); font-family:var(--font-code);">
          <div style="background:var(--neon-cyan); color:#000; padding:0.4rem 1rem; font-weight:bold; display:flex; justify-content:space-between; align-items:center;">
            <span>GNU nano 7.2 &mdash; <span id="nanoFilename">file.txt</span></span>
            <span style="font-size:0.8rem;">[ Modified ]</span>
          </div>
          <textarea id="nanoTextArea" style="width:100%; height:340px; background:#070a12; color:#fff; font-family:var(--font-code); padding:1rem; border:none; outline:none; resize:none; font-size:0.95rem; line-height:1.5;"></textarea>
          <div style="background:#0f172a; padding:0.6rem 1rem; border-top:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:0.8rem; color:#8a99ad;">
              <span style="background:#1e293b; color:#00f3ff; padding:2px 6px; border-radius:3px;">^O</span> Save File &nbsp;&nbsp;
              <span style="background:#1e293b; color:#ff3366; padding:2px 6px; border-radius:3px;">^X</span> Exit
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button onclick="window.terminalInstance && window.terminalInstance.saveNanoFile()" class="btn btn-primary" style="padding:0.3rem 0.8rem; font-size:0.8rem;"><i class="fas fa-save"></i> Save</button>
              <button onclick="window.terminalInstance && window.terminalInstance.closeNano()" class="btn btn-outline" style="padding:0.3rem 0.8rem; font-size:0.8rem;"><i class="fas fa-times"></i> Close</button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.termBody = document.getElementById('termBody');
    this.termInput = document.getElementById('termInput');
    this.termPrompt = document.getElementById('termPrompt');

    this.termInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
    this.container.addEventListener('click', () => this.termInput.focus());

    this.updateVFSInspector();
  }

  updatePrompt() {
    const displayPath = this.cwd.startsWith('/home/hero') ? this.cwd.replace('/home/hero', '~') : this.cwd;
    this.termPrompt.innerText = `${this.user}@linuxquest:${displayPath}$`;
    const titleEl = this.container.querySelector('.terminal-title');
    if (titleEl) titleEl.innerHTML = `<i class="fas fa-terminal"></i> bash - linuxquest@${this.user}: ${displayPath}`;
  }

  updateVFSInspector() {
    const vfsEl = document.getElementById('vfsTreeContainer');
    if (vfsEl) {
      vfsEl.innerHTML = this.vfs.renderTreeHTML();
    }
  }

  clearTerminal() {
    this.termBody.innerHTML = '';
  }

  handleKeyDown(e) {
    if (window.soundEngine) window.soundEngine.playKeyClick();

    if (e.key === 'Tab') {
      e.preventDefault();
      this.handleTabCompletion();
      return;
    }

    if (e.ctrlKey && e.key === 'l') {
      e.preventDefault();
      this.clearTerminal();
      return;
    }

    if (e.key === 'Enter') {
      const cmd = this.termInput.value.trim();
      if (cmd.length > 0) {
        this.writeLine(`${this.termPrompt.innerText} ${cmd}`, 'prompt-line');
        this.history.push(cmd);
        this.historyIdx = this.history.length;
        this.executeCommand(cmd);
        this.termInput.value = '';
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (this.historyIdx > 0) {
        this.historyIdx--;
        this.termInput.value = this.history[this.historyIdx];
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (this.historyIdx < this.history.length - 1) {
        this.historyIdx++;
        this.termInput.value = this.history[this.historyIdx];
      } else {
        this.historyIdx = this.history.length;
        this.termInput.value = '';
      }
    }
  }

  handleTabCompletion() {
    const text = this.termInput.value;
    const tokens = text.split(/\s+/);
    const lastToken = tokens[tokens.length - 1] || '';

    const COMMAND_LIST = [
      'pwd', 'ls', 'cd', 'mkdir', 'touch', 'rm', 'cat', 'echo', 'grep',
      'chmod', 'chown', 'sudo', 'whoami', 'clear', 'help', 'head', 'tail',
      'wc', 'find', 'nano', 'vim', 'vi', 'ps', 'top', 'kill', 'curl',
      'wget', 'ping', 'uname', 'uptime', 'date', 'history', 'man', 'bash', 'tar'
    ];

    if (tokens.length <= 1) {
      const matches = COMMAND_LIST.filter(c => c.startsWith(lastToken));
      if (matches.length === 1) {
        this.termInput.value = matches[0] + ' ';
      } else if (matches.length > 1) {
        this.writeLine(matches.join('  '), 'text-cyan');
      }
      return;
    }

    // Path or file completion
    const dirNode = this.vfs.getNode(this.cwd);
    if (dirNode && dirNode.children) {
      const candidates = Object.keys(dirNode.children).filter(k => k.startsWith(lastToken));
      if (candidates.length === 1) {
        tokens[tokens.length - 1] = candidates[0];
        this.termInput.value = tokens.join(' ');
      } else if (candidates.length > 1) {
        this.writeLine(candidates.join('  '), 'text-green');
      }
    }
  }

  writeLine(text, className = '') {
    const line = document.createElement('div');
    line.className = `terminal-line ${className}`;
    line.innerHTML = text;
    this.termBody.appendChild(line);
    this.termBody.scrollTop = this.termBody.scrollHeight;
  }

  executeCommand(rawCmd) {
    if (window.soundEngine) window.soundEngine.playCommandChime();

    // Check for pipes
    if (rawCmd.includes('|')) {
      this.executePipedCommands(rawCmd);
      if (this.quest) this.verifyCurrentQuest();
      return;
    }

    const parts = rawCmd.split(/\s+/);
    const cmd = parts[0];
    const args = parts.slice(1);

    // Shell script execution e.g. ./script.sh or bash script.sh
    if (cmd === 'bash' || cmd === 'sh' || cmd.startsWith('./')) {
      this.cmdRunScript(cmd, args);
      if (this.quest) this.verifyCurrentQuest();
      return;
    }

    switch (cmd) {
      case 'pwd':
        this.writeLine(this.cwd);
        break;

      case 'ls':
        this.cmdLs(args);
        break;

      case 'cd':
        this.cmdCd(args[0]);
        break;

      case 'mkdir':
        this.cmdMkdir(args);
        break;

      case 'touch':
        if (args.length === 0) this.writeLine('touch: missing file operand', 'text-red');
        else {
          args.forEach(f => this.vfs.createFile(f, '', 'rw-r--r--', this.cwd));
          this.updateVFSInspector();
        }
        break;

      case 'rm':
        this.cmdRm(args);
        break;

      case 'cat':
        this.cmdCat(args[0]);
        break;

      case 'head':
        this.cmdHead(args);
        break;

      case 'tail':
        this.cmdTail(args);
        break;

      case 'wc':
        this.cmdWc(args);
        break;

      case 'echo':
        this.cmdEcho(args);
        break;

      case 'grep':
        this.cmdGrep(args);
        break;

      case 'sed':
        this.cmdSed(args);
        break;

      case 'awk':
        this.cmdAwk(args);
        break;

      case 'sort':
        this.cmdSort(args);
        break;

      case 'uniq':
        this.cmdUniq(args);
        break;

      case 'df':
        this.cmdDf(args);
        break;

      case 'free':
        this.cmdFree(args);
        break;

      case 'crontab':
        this.cmdCrontab(args);
        break;

      case 'chmod':
        this.cmdChmod(args);
        break;

      case 'chown':
        this.cmdChown(args);
        break;

      case 'find':
        this.cmdFind(args);
        break;

      case 'sudo':
        if (args.length > 0) this.executeCommand(args.join(' '));
        else this.writeLine('usage: sudo command');
        break;

      case 'whoami':
        this.writeLine(this.user);
        break;

      case 'id':
        this.writeLine(`uid=1000(${this.user}) gid=1000(${this.user}) groups=1000(${this.user}),27(sudo),100(users)`);
        break;

      case 'uname':
        if (args.includes('-a') || args.includes('-r')) {
          this.writeLine('Linux linuxquest-srv01 6.8.0-40-generic #40-Ubuntu SMP PREEMPT_DYNAMIC x86_64 GNU/Linux');
        } else {
          this.writeLine('Linux');
        }
        break;

      case 'uptime':
        this.writeLine(` 10:15:32 up 14 days,  3:22,  2 users,  load average: 0.12, 0.08, 0.05`);
        break;

      case 'date':
        this.writeLine(new Date().toUTCString());
        break;

      case 'ps':
        this.cmdPs(args);
        break;

      case 'top':
        this.cmdTop();
        break;

      case 'kill':
        this.cmdKill(args);
        break;

      case 'curl':
      case 'wget':
        this.cmdCurl(args);
        break;

      case 'ping':
        this.cmdPing(args);
        break;

      case 'nano':
      case 'vim':
      case 'vi':
        this.openNano(args[0]);
        break;

      case 'history':
        this.history.forEach((h, idx) => {
          this.writeLine(`  ${(idx + 1).toString().padStart(4, ' ')}  ${h}`);
        });
        break;

      case 'man':
        this.cmdMan(args[0]);
        break;

      case 'tar':
        this.cmdTar(args);
        break;

      case 'clear':
        this.clearTerminal();
        break;

      case 'help':
        this.writeLine(`
<span style="color:#00f3ff; font-weight:bold;">LINUXQUEST COMMAND REFERENCE:</span>
  <strong style="color:#00ff9d;">Navigation & Files:</strong>
    pwd, ls [-la], cd &lt;path&gt;, mkdir [-p] &lt;dir&gt;, touch &lt;file&gt;, rm [-rf] &lt;path&gt;, cat &lt;file&gt;
    head [-n N] &lt;file&gt;, tail [-n N] &lt;file&gt;, wc [-l|-w] &lt;file&gt;, find [path] [-name pattern]
  <strong style="color:#00ff9d;">Text & Permissions:</strong>
    echo "text" [&gt;|&gt;&gt; file], grep "pattern" &lt;file&gt;, chmod &lt;+x|755|644&gt; &lt;file&gt;, chown &lt;user&gt; &lt;file&gt;
  <strong style="color:#00ff9d;">Editors & Scripting:</strong>
    nano &lt;file&gt;, vim &lt;file&gt;, bash &lt;script.sh&gt;, ./&lt;script.sh&gt;
  <strong style="color:#00ff9d;">System & Process:</strong>
    whoami, id, uname [-a], uptime, date, ps [aux], top, kill &lt;pid&gt;, sudo &lt;cmd&gt;
  <strong style="color:#00ff9d;">Network & Utilities:</strong>
    curl &lt;url&gt;, ping &lt;host&gt;, man &lt;cmd&gt;, history, clear, tar [-czf|-xzf]
        `);
        break;

      default:
        this.writeLine(`bash: ${cmd}: command not found. Type 'help' for guidance.`, 'text-red');
    }

    if (this.quest) {
      this.verifyCurrentQuest();
    }
  }

  executePipedCommands(rawCmd) {
    const pipeParts = rawCmd.split('|').map(s => s.trim());
    let buffer = '';

    for (let i = 0; i < pipeParts.length; i++) {
      const part = pipeParts[i];
      const tokens = part.split(/\s+/);
      const c = tokens[0];
      const a = tokens.slice(1);

      if (i === 0) {
        if (c === 'cat') {
          const node = this.vfs.getNode(a[0], this.cwd);
          buffer = node && node.type === 'file' ? node.content : '';
        } else if (c === 'echo') {
          buffer = a.join(' ').replace(/^["']|["']$/g, '');
        } else if (c === 'ls') {
          const node = this.vfs.getNode(this.cwd);
          buffer = node && node.children ? Object.keys(node.children).join('\n') : '';
        }
      } else {
        if (c === 'grep') {
          const pat = a[0] ? a[0].replace(/^["']|["']$/g, '') : '';
          buffer = buffer.split('\n').filter(l => l.includes(pat)).join('\n');
        } else if (c === 'wc') {
          if (a.includes('-l')) buffer = buffer.split('\n').filter(Boolean).length.toString();
          else buffer = `${buffer.split('\n').length} ${buffer.split(/\s+/).length} ${buffer.length}`;
        } else if (c === 'head') {
          buffer = buffer.split('\n').slice(0, 5).join('\n');
        } else if (c === 'tail') {
          buffer = buffer.split('\n').slice(-5).join('\n');
        }
      }
    }

    if (buffer) {
      this.writeLine(buffer);
    }
  }

  cmdRunScript(cmd, args) {
    const scriptPath = cmd === 'bash' || cmd === 'sh' ? args[0] : cmd;
    if (!scriptPath) {
      this.writeLine('bash: missing script argument', 'text-red');
      return;
    }
    const cleanPath = scriptPath.replace(/^\.\//, '');
    const node = this.vfs.getNode(cleanPath, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`bash: ${scriptPath}: No such file or directory`, 'text-red');
      return;
    }

    if (cmd.startsWith('./') && (!node.perm || !node.perm.includes('x'))) {
      this.writeLine(`bash: ${scriptPath}: Permission denied. Run 'chmod +x ${scriptPath}' first.`, 'text-red');
      return;
    }

    this.writeLine(`[Running ${cleanPath}...]`, 'text-cyan');
    const lines = node.content.split('\n');
    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line || line.startsWith('#')) continue;
      this.executeCommand(line);
    }
    this.writeLine(`[Process completed with exit code 0]`, 'text-green');
  }

  cmdLs(args) {
    const showAll = args.includes('-a') || args.includes('-la') || args.includes('-al');
    const showLong = args.includes('-l') || args.includes('-la') || args.includes('-al');

    const targetArg = args.find(a => !a.startsWith('-')) || this.cwd;
    const node = this.vfs.getNode(targetArg, this.cwd);
    if (!node) {
      this.writeLine(`ls: cannot access '${targetArg}': No such file or directory`, 'text-red');
      return;
    }
    if (node.type === 'file') {
      this.writeLine(node.name);
      return;
    }

    const items = Object.values(node.children || {});
    if (showLong) {
      this.writeLine(`total ${items.length * 4}`);
      items.forEach(item => {
        if (!showAll && item.name.startsWith('.')) return;
        const color = item.type === 'dir' ? '#00f3ff' : (item.perm && item.perm.includes('x') ? '#00ff9d' : '#fff');
        this.writeLine(`${item.perm || 'rw-r--r--'} 1 ${item.owner || 'hero'} hero 4096 Oct 16 10:15 <span style="color:${color}; font-weight:bold;">${item.name}</span>`);
      });
    } else {
      const names = items
        .filter(item => showAll || !item.name.startsWith('.'))
        .map(item => `<span style="color:${item.type === 'dir' ? '#00f3ff' : (item.perm && item.perm.includes('x') ? '#00ff9d' : '#fff')}; font-weight:bold;">${item.name}</span>`);
      this.writeLine(names.join('   '));
    }
  }

  cmdCd(targetPath) {
    if (!targetPath || targetPath === '~') {
      this.cwd = '/home/hero';
      this.updatePrompt();
      return;
    }
    const targetNode = this.vfs.getNode(targetPath, this.cwd);
    if (!targetNode) {
      this.writeLine(`cd: ${targetPath}: No such file or directory`, 'text-red');
    } else if (targetNode.type !== 'dir') {
      this.writeLine(`cd: ${targetPath}: Not a directory`, 'text-red');
    } else {
      this.cwd = this.vfs.normalizePath(targetPath, this.cwd);
      this.updatePrompt();
    }
  }

  cmdMkdir(args) {
    const path = args.find(a => !a.startsWith('-'));
    if (!path) {
      this.writeLine('mkdir: missing operand', 'text-red');
      return;
    }
    const created = this.vfs.createDirectory(path, this.cwd);
    if (!created) {
      this.writeLine(`mkdir: cannot create directory '${path}'`, 'text-red');
      return;
    }
    this.updateVFSInspector();
    this.writeLine(`Created directory: ${path}`, 'text-green');
  }

  cmdRm(args) {
    const target = args.find(a => !a.startsWith('-'));
    if (!target) {
      this.writeLine('rm: missing operand', 'text-red');
      return;
    }
    const ok = this.vfs.removePath(target, this.cwd);
    if (ok) {
      this.updateVFSInspector();
    } else {
      this.writeLine(`rm: cannot remove '${target}': No such file or directory`, 'text-red');
    }
  }

  cmdCat(path) {
    if (!path) {
      this.writeLine('cat: missing file operand', 'text-red');
      return;
    }
    const node = this.vfs.getNode(path, this.cwd);
    if (!node) this.writeLine(`cat: ${path}: No such file or directory`, 'text-red');
    else if (node.type === 'dir') this.writeLine(`cat: ${path}: Is a directory`, 'text-red');
    else this.writeLine(node.content ? node.content.replace(/\n/g, '<br>') : '');
  }

  cmdHead(args) {
    const nIdx = args.indexOf('-n');
    let limit = 10;
    let filePath = args[0];
    if (nIdx !== -1 && args[nIdx + 1]) {
      limit = parseInt(args[nIdx + 1], 10) || 10;
      filePath = args.find((a, i) => i !== nIdx && i !== nIdx + 1 && !a.startsWith('-'));
    }
    if (!filePath) {
      this.writeLine('head: missing file operand');
      return;
    }
    const node = this.vfs.getNode(filePath, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`head: cannot open '${filePath}'`);
      return;
    }
    const lines = node.content.split('\n').slice(0, limit);
    this.writeLine(lines.join('<br>'));
  }

  cmdTail(args) {
    const nIdx = args.indexOf('-n');
    let limit = 10;
    let filePath = args[0];
    if (nIdx !== -1 && args[nIdx + 1]) {
      limit = parseInt(args[nIdx + 1], 10) || 10;
      filePath = args.find((a, i) => i !== nIdx && i !== nIdx + 1 && !a.startsWith('-'));
    }
    if (!filePath) {
      this.writeLine('tail: missing file operand');
      return;
    }
    const node = this.vfs.getNode(filePath, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`tail: cannot open '${filePath}'`);
      return;
    }
    const lines = node.content.split('\n').slice(-limit);
    this.writeLine(lines.join('<br>'));
  }

  cmdWc(args) {
    const filePath = args.find(a => !a.startsWith('-'));
    if (!filePath) {
      this.writeLine('wc: missing file operand');
      return;
    }
    const node = this.vfs.getNode(filePath, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`wc: ${filePath}: No such file or directory`);
      return;
    }
    const lines = node.content ? node.content.split('\n').length : 0;
    const words = node.content ? node.content.trim().split(/\s+/).filter(Boolean).length : 0;
    const bytes = node.content ? node.content.length : 0;

    if (args.includes('-l')) {
      this.writeLine(`${lines} ${filePath}`);
    } else if (args.includes('-w')) {
      this.writeLine(`${words} ${filePath}`);
    } else {
      this.writeLine(` ${lines}  ${words} ${bytes} ${filePath}`);
    }
  }

  cmdEcho(args) {
    const fullText = args.join(' ');
    if (fullText.includes('>')) {
      const redirectAppend = fullText.includes('>>');
      const parts = fullText.split(redirectAppend ? '>>' : '>');
      const text = parts[0].trim().replace(/^["']|["']$/g, '');
      const filePath = parts[1].trim();

      if (redirectAppend) {
        const existingNode = this.vfs.getNode(filePath, this.cwd);
        const existingContent = existingNode && existingNode.type === 'file' ? existingNode.content + '\n' : '';
        this.vfs.createFile(filePath, existingContent + text, 'rw-r--r--', this.cwd);
      } else {
        this.vfs.createFile(filePath, text, 'rw-r--r--', this.cwd);
      }
      this.updateVFSInspector();
    } else {
      this.writeLine(fullText.replace(/^["']|["']$/g, ''));
    }
  }

  cmdGrep(args) {
    let pattern = '';
    let filePath = '';
    for (const a of args) {
      if (!pattern) pattern = a.replace(/^["']|["']$/g, '');
      else if (!filePath) filePath = a;
    }
    if (!filePath) {
      this.writeLine('grep: missing file operand');
      return;
    }
    const node = this.vfs.getNode(filePath, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`grep: ${filePath}: No such file`);
      return;
    }
    const lines = node.content.split('\n');
    let matches = 0;
    lines.forEach(line => {
      if (line.includes(pattern)) {
        matches++;
        const highlighted = line.replace(new RegExp(pattern, 'g'), `<span style="color:#ff3366; font-weight:bold;">${pattern}</span>`);
        this.writeLine(highlighted);
      }
    });
    if (matches === 0) {
      // Grep outputs nothing on no match
    }
  }

  cmdSed(args) {
    const expr = args.find(a => !a.startsWith('-')) || '';
    const file = args.filter(a => !a.startsWith('-'))[1];
    if (!file) {
      this.writeLine('sed: missing input file');
      return;
    }
    const node = this.vfs.getNode(file, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`sed: cannot read ${file}: No such file`);
      return;
    }
    let content = node.content;
    const match = expr.match(/^s\/([^/]+)\/([^/]*)\/([g]?)$/);
    if (match) {
      const search = match[1];
      const replace = match[2];
      const flags = match[3];
      content = content.replace(new RegExp(search, flags.includes('g') ? 'g' : ''), replace);
    }
    this.writeLine(content.replace(/\n/g, '<br>'));
  }

  cmdAwk(args) {
    const expr = args.find(a => !a.startsWith('-')) || '';
    const file = args.filter(a => !a.startsWith('-'))[1];
    if (!file) {
      this.writeLine('awk: missing input file');
      return;
    }
    const node = this.vfs.getNode(file, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`awk: cannot open file ${file}`);
      return;
    }
    const lines = node.content.split('\n');
    const colMatch = expr.match(/\$([0-9]+)/);
    const colIdx = colMatch ? parseInt(colMatch[1], 10) : null;
    lines.forEach(l => {
      if (colIdx === 0) this.writeLine(l);
      else if (colIdx !== null) {
        const parts = l.trim().split(/\s+/);
        this.writeLine(parts[colIdx - 1] || '');
      } else {
        this.writeLine(l);
      }
    });
  }

  cmdSort(args) {
    const file = args.find(a => !a.startsWith('-'));
    if (!file) {
      this.writeLine('sort: missing file operand');
      return;
    }
    const node = this.vfs.getNode(file, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`sort: cannot read: ${file}: No such file or directory`);
      return;
    }
    let lines = node.content.split('\n').filter(Boolean);
    const reverse = args.includes('-r');
    const unique = args.includes('-u');
    if (unique) lines = Array.from(new Set(lines));
    lines.sort();
    if (reverse) lines.reverse();
    this.writeLine(lines.join('<br>'));
  }

  cmdUniq(args) {
    const file = args.find(a => !a.startsWith('-'));
    if (!file) {
      this.writeLine('uniq: missing file operand');
      return;
    }
    const node = this.vfs.getNode(file, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`uniq: ${file}: No such file or directory`);
      return;
    }
    const lines = node.content.split('\n');
    const showCount = args.includes('-c');
    const out = [];
    let prev = null;
    let count = 0;
    lines.forEach(l => {
      if (l === prev) count++;
      else {
        if (prev !== null) out.push(showCount ? `   ${count} ${prev}` : prev);
        prev = l;
        count = 1;
      }
    });
    if (prev !== null) out.push(showCount ? `   ${count} ${prev}` : prev);
    this.writeLine(out.join('<br>'));
  }

  cmdDf(args) {
    this.writeLine(`Filesystem     1K-blocks      Used Available Use% Mounted on<br>/dev/sda1      102838104  24128912  73452104  25% /<br>tmpfs            4096000         0   4096000   0% /dev/shm<br>/dev/sdb1      514190520 102400120 385621400  21% /var/backups`);
  }

  cmdFree(args) {
    this.writeLine(`               total        used        free      shared  buff/cache   available<br>Mem:         8192000     2412000     3980000       42000     1800000     5780000<br>Swap:        2048000           0     2048000`);
  }

  cmdCrontab(args) {
    if (args.includes('-l')) {
      const node = this.vfs.getNode('/etc/crontab');
      if (node && node.type === 'file') {
        this.writeLine(node.content.replace(/\n/g, '<br>'));
      } else {
        this.writeLine('no crontab for hero');
      }
    } else {
      this.writeLine('crontab: usage: crontab -l (view jobs)');
    }
  }

  cmdChmod(args) {
    if (args.length < 2) {
      this.writeLine('chmod: missing operand');
      return;
    }
    const perm = args[0];
    const file = args[1];
    const node = this.vfs.getNode(file, this.cwd);
    if (node) {
      if (/^[0-7]{3,4}$/.test(perm)) {
        const p = perm.slice(-3);
        const mapDigit = (d) => {
          const n = parseInt(d, 10);
          return (n & 4 ? 'r' : '-') + (n & 2 ? 'w' : '-') + (n & 1 ? 'x' : '-');
        };
        node.perm = mapDigit(p[0]) + mapDigit(p[1]) + mapDigit(p[2]);
      } else if (perm === '+x' || perm === 'u+x' || perm === '755') {
        node.perm = 'rwxr-xr-x';
      } else if (perm === '644') {
        node.perm = 'rw-r--r--';
      } else if (perm === '600') {
        node.perm = 'rw-------';
      }
      this.writeLine(`mode of '${file}' changed to ${node.perm}`);
      this.updateVFSInspector();
    } else {
      this.writeLine(`chmod: cannot access '${file}': No such file or directory`, 'text-red');
    }
  }

  cmdChown(args) {
    if (args.length < 2) {
      this.writeLine('chown: missing operand');
      return;
    }
    const owner = args[0];
    const file = args[1];
    const node = this.vfs.getNode(file, this.cwd);
    if (node) {
      node.owner = owner;
      this.writeLine(`changed ownership of '${file}' to ${owner}`);
    } else {
      this.writeLine(`chown: cannot access '${file}': No such file or directory`, 'text-red');
    }
  }

  cmdFind(args) {
    const nameIdx = args.indexOf('-name');
    let pattern = '*';
    if (nameIdx !== -1 && args[nameIdx + 1]) {
      pattern = args[nameIdx + 1].replace(/^["']|["']$/g, '');
    }
    const startPath = args[0] && !args[0].startsWith('-') ? args[0] : this.cwd;
    const matches = this.vfs.searchFiles(pattern, this.vfs.normalizePath(startPath, this.cwd));
    if (matches.length > 0) {
      matches.forEach(m => this.writeLine(m));
    } else {
      this.writeLine(`(no files matched '${pattern}')`, 'text-muted');
    }
  }

  cmdPs(args) {
    this.writeLine(`USER       PID  %CPU %MEM   VSZ   RSS TTY      STAT START   TIME COMMAND`);
    this.processes.forEach(p => {
      this.writeLine(`${p.user.padEnd(8)} ${p.pid.toString().padStart(5)}  ${p.cpu}  ${p.mem} 108420 14220 ?        Ss   10:00   0:01 ${p.cmd}`);
    });
  }

  cmdTop() {
    this.writeLine(`top - 10:16:00 up 14 days,  2 users,  load average: 0.08, 0.05, 0.02`);
    this.writeLine(`Tasks: 6 total, 1 running, 5 sleeping, 0 stopped, 0 zombie`);
    this.writeLine(`%Cpu(s):  1.5 us,  0.8 sy,  0.0 ni, 97.4 id,  0.3 wa,  0.0 hi,  0.0 si`);
    this.writeLine(`MiB Mem :   8192.0 total,   4210.4 free,   2180.2 used,   1801.4 buff/cache`);
    this.cmdPs([]);
  }

  cmdKill(args) {
    const pid = parseInt(args[0], 10);
    if (!pid) {
      this.writeLine('kill: usage: kill &lt;pid&gt;');
      return;
    }
    const pIdx = this.processes.findIndex(p => p.pid === pid);
    if (pIdx !== -1) {
      const removed = this.processes.splice(pIdx, 1)[0];
      this.writeLine(`[Terminated process PID ${pid} (${removed.cmd})]`, 'text-green');
    } else {
      this.writeLine(`kill: (${pid}) - No such process`, 'text-red');
    }
  }

  cmdCurl(args) {
    const url = args.find(a => !a.startsWith('-')) || 'http://localhost';
    this.writeLine(`HTTP/1.1 200 OK<br>Date: ${new Date().toUTCString()}<br>Server: LinuxQuest-Simulated/1.0<br>Content-Type: text/html; charset=UTF-8<br><br>&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;body&gt;&lt;h1&gt;LinuxQuest Gateway Connected&lt;/h1&gt;&lt;/body&gt;&lt;/html&gt;`);
  }

  cmdPing(args) {
    const host = args.find(a => !a.startsWith('-')) || '8.8.8.8';
    this.writeLine(`PING ${host} (${host}) 56(84) bytes of data.`);
    for (let i = 1; i <= 3; i++) {
      this.writeLine(`64 bytes from ${host}: icmp_seq=${i} ttl=58 time=${(12.4 + i * 1.2).toFixed(2)} ms`);
    }
    this.writeLine(`--- ${host} ping statistics ---<br>3 packets transmitted, 3 received, 0% packet loss`);
  }

  cmdMan(cmdName) {
    if (!cmdName) {
      this.writeLine('What manual page do you want? Try: man ls, man grep, man chmod');
      return;
    }

    if (window.LINUXQUEST_MAN_PAGES && window.LINUXQUEST_MAN_PAGES[cmdName]) {
      const p = window.LINUXQUEST_MAN_PAGES[cmdName];
      this.writeLine(`
<span style="color:#00f3ff; font-weight:bold;">${p.name.toUpperCase()}(1) &mdash; User Commands</span><br>
<strong>NAME</strong><br>&nbsp;&nbsp;${p.name} - ${p.summary}<br><br>
<strong>SYNOPSIS</strong><br>&nbsp;&nbsp;${p.synopsis}<br><br>
<strong>DESCRIPTION</strong><br>&nbsp;&nbsp;${p.description}<br><br>
<strong>EXAMPLES</strong><br>&nbsp;&nbsp;${(p.examples || []).join('<br>&nbsp;&nbsp;')}
      `);
      return;
    }

    // Default POSIX fallback
    this.writeLine(`
<span style="color:#00f3ff; font-weight:bold;">${cmdName.toUpperCase()}(1) &mdash; General Commands Manual</span><br>
<strong>NAME</strong><br>&nbsp;&nbsp;${cmdName} - standard POSIX shell utility<br><br>
<strong>SYNOPSIS</strong><br>&nbsp;&nbsp;${cmdName} [OPTIONS] [OPERANDS]<br><br>
<strong>DESCRIPTION</strong><br>&nbsp;&nbsp;Standard POSIX conformant system interface in LinuxQuest.
    `);
  }

  cmdTar(args) {
    this.writeLine(`tar: archive operations simulated successfully.`);
  }

  // --- NANO INLINE EDITOR ---
  openNano(filename = 'untitled.txt') {
    this.currentEditingFile = filename;
    const modal = document.getElementById('nanoModal');
    const titleEl = document.getElementById('nanoFilename');
    const textarea = document.getElementById('nanoTextArea');
    if (!modal || !titleEl || !textarea) return;

    titleEl.innerText = filename;
    const node = this.vfs.getNode(filename, this.cwd);
    textarea.value = node && node.type === 'file' ? node.content : '';

    modal.style.display = 'flex';
    textarea.focus();
  }

  saveNanoFile() {
    const textarea = document.getElementById('nanoTextArea');
    if (!textarea || !this.currentEditingFile) return;

    this.vfs.createFile(this.currentEditingFile, textarea.value, 'rw-r--r--', this.cwd);
    this.updateVFSInspector();
    this.closeNano();
    this.writeLine(`[ Wrote ${textarea.value.length} bytes to ${this.currentEditingFile} ]`, 'text-green');
    if (this.quest) this.verifyCurrentQuest();
  }

  closeNano() {
    const modal = document.getElementById('nanoModal');
    if (modal) modal.style.display = 'none';
    if (this.termInput) this.termInput.focus();
  }

  async verifyCurrentQuest() {
    if (!this.quest) return;

    try {
      const resp = await fetch(`/api/quests/${this.quest.id}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vfs_state: this.vfs.exportState(),
          command_history: this.history
        })
      });
      const data = await resp.json();
      if (data.success && !this.questCompleted) {
        this.questCompleted = true;
        if (window.soundEngine) window.soundEngine.playSuccessSound();

        const banner = document.getElementById('questSuccessBanner');
        if (banner) {
          banner.style.display = 'block';
          banner.innerHTML = `
            <div class="card" style="border-color: var(--neon-green); background: rgba(0,255,157,0.12); padding: 1.2rem; border-radius: 8px;">
              <h3 style="color: var(--neon-green); margin-bottom: 0.4rem;"><i class="fas fa-check-circle"></i> QUEST COMPLETED!</h3>
              <p style="color: #fff; margin-bottom: 0.4rem;">Outstanding execution! You earned <strong>+${data.xp_earned} XP</strong>!</p>
              ${data.new_badges && data.new_badges.length > 0 ? `<p style="color:var(--neon-gold); font-weight:bold;"><i class="fas fa-medal"></i> Unlocked Badges: ${data.new_badges.join(', ')}</p>` : ''}
            </div>
          `;
        }
      }
    } catch (err) {
      console.error("Quest verification error", err);
    }
  }
}

window.TerminalSimulator = TerminalSimulator;
window.VirtualFileSystem = VirtualFileSystem;
