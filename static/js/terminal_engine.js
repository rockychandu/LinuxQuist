/* ==========================================================================
   LINUXQUEST — VIRTUAL FILE SYSTEM & TERMINAL SIMULATOR ENGINE
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
                'notes.txt': { type: 'file', name: 'notes.txt', owner: 'hero', perm: 'rw-r--r--', content: 'Welcome to LinuxQuest!\nMaster commands, complete quests, earn XP!' }
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
                'syslog': { type: 'file', name: 'syslog', owner: 'root', perm: 'rw-r--r--', content: 'INFO: System booted successfully.\nINFO: Network interface eth0 up.\nCRITICAL: Database connection failed at 10:00:05.\nCRITICAL: Auth service offline.\nINFO: Retry scheduled.' },
                'auth.log': { type: 'file', name: 'auth.log', owner: 'root', perm: 'rw-r-----', content: 'Aug 25 10:00:01 server sshd[1024]: Accepted password for hero from 192.168.1.100 port 52140 ssh2' }
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
            'passwd': { type: 'file', name: 'passwd', owner: 'root', perm: 'rw-r--r--', content: 'root:x:0:0:root:/root:/bin/bash\nhero:x:1000:1000:Hero User:/home/hero:/bin/bash' },
            'hostname': { type: 'file', name: 'hostname', owner: 'root', perm: 'rw-r--r--', content: 'linuxquest-server' }
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

    const dirNode = this.getNode(dirPath);
    if (!dirNode || dirNode.type !== 'dir') return false;

    dirNode.children[fileName] = {
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
    const lastSlash = absPath.lastIndexOf('/');
    const dirPath = absPath.substring(0, lastSlash) || '/';
    const dirName = absPath.substring(lastSlash + 1);

    const parentNode = this.getNode(dirPath);
    if (!parentNode || parentNode.type !== 'dir') return false;

    parentNode.children[dirName] = {
      type: 'dir',
      name: dirName,
      owner: 'hero',
      perm: 'rwxr-xr-x',
      children: {}
    };
    return true;
  }

  removePath(pathStr, cwd = '/home/hero') {
    const absPath = this.normalizePath(pathStr, cwd);
    const lastSlash = absPath.lastIndexOf('/');
    const dirPath = absPath.substring(0, lastSlash) || '/';
    const targetName = absPath.substring(lastSlash + 1);

    const parentNode = this.getNode(dirPath);
    if (!parentNode || !parentNode.children[targetName]) return false;

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
      return `<div class="tree-item file"><i class="fas fa-file-alt text-cyan"></i> ${node.name}</div>`;
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
}

class TerminalSimulator {
  constructor(containerId, questData = null) {
    this.container = document.getElementById(containerId);
    this.vfs = new VirtualFileSystem(questData ? JSON.parse(questData.initial_vfs_json || '{}') : null);
    this.cwd = '/home/hero';
    this.user = 'hero';
    this.history = [];
    this.historyIdx = -1;
    this.quest = questData;
    
    this.init();
  }

  init() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="terminal-window">
        <div class="terminal-header">
          <div class="terminal-dots">
            <span class="dot dot-red"></span>
            <span class="dot dot-yellow"></span>
            <span class="dot dot-green"></span>
          </div>
          <div class="terminal-title"><i class="fas fa-terminal"></i> bash - linuxquest@hero: ${this.cwd}</div>
          <div><i class="fas fa-volume-up sound-toggle-icon" onclick="window.soundEngine.toggleMute()" style="cursor:pointer;" title="Toggle Sound"></i></div>
        </div>
        <div class="terminal-body" id="termBody">
          <div class="terminal-line"><span style="color:#00ff9d;">Welcome to LinuxQuest Quest Terminal v2.4</span></div>
          <div class="terminal-line"><span style="color:#8a99ad;">Type <strong style="color:#00f3ff;">help</strong> for available commands or start your quest!</span></div>
        </div>
        <div class="terminal-input-wrapper" style="padding: 0.8rem 1.25rem; background: #0b0f19; border-top: 1px solid var(--border-subtle);">
          <span class="terminal-prompt" id="termPrompt">${this.user}@linuxquest:${this.cwd}$</span>
          <input type="text" class="terminal-input" id="termInput" autocomplete="off" spellcheck="false" placeholder="Enter command...">
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
    if (titleEl) titleEl.innerHTML = `<i class="fas fa-terminal"></i> bash - linuxquest@hero: ${displayPath}`;
  }

  updateVFSInspector() {
    const vfsEl = document.getElementById('vfsTreeContainer');
    if (vfsEl) {
      vfsEl.innerHTML = this.vfs.renderTreeHTML();
    }
  }

  handleKeyDown(e) {
    if (window.soundEngine) window.soundEngine.playKeyClick();

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

  writeLine(text, className = '') {
    const line = document.createElement('div');
    line.className = `terminal-line ${className}`;
    line.innerHTML = text;
    this.termBody.appendChild(line);
    this.termBody.scrollTop = this.termBody.scrollHeight;
  }

  executeCommand(rawCmd) {
    if (window.soundEngine) window.soundEngine.playCommandChime();

    const parts = rawCmd.split(/\s+/);
    const cmd = parts[0];
    const args = parts.slice(1);

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

      case 'echo':
        this.cmdEcho(args);
        break;

      case 'grep':
        this.cmdGrep(args);
        break;

      case 'chmod':
        this.cmdChmod(args);
        break;

      case 'sudo':
        if (args.length > 0) this.executeCommand(args.join(' '));
        else this.writeLine('usage: sudo command');
        break;

      case 'whoami':
        this.writeLine(this.user);
        break;

      case 'clear':
        this.termBody.innerHTML = '';
        break;

      case 'help':
        this.writeLine(`
<span style="color:#00f3ff; font-weight:bold;">LINUXQUEST AVAILABLE COMMANDS:</span>
  pwd                - Print current working directory
  ls [-la]           - List directory contents
  cd &lt;path&gt;          - Change directory
  mkdir [-p] &lt;dir&gt;   - Create directory
  touch &lt;file&gt;       - Create empty file
  rm [-rf] &lt;path&gt;    - Delete file or directory
  cat &lt;file&gt;         - Display file contents
  echo "text" &gt; &lt;f&gt;  - Write text to file
  grep "str" &lt;f&gt;     - Filter matching lines
  chmod &lt;perm&gt; &lt;f&gt;   - Change permissions (e.g. +x or 755)
  sudo &lt;cmd&gt;         - Run command with root privileges
  whoami             - Show current active user
  clear              - Clear screen
        `);
        break;

      default:
        this.writeLine(`bash: ${cmd}: command not found. Type 'help' for guidance.`, 'text-red');
    }

    // Auto-check Quest Objective verification after command execution
    if (this.quest) {
      this.verifyCurrentQuest();
    }
  }

  cmdLs(args) {
    const showAll = args.includes('-a') || args.includes('-la') || args.includes('-al');
    const showLong = args.includes('-l') || args.includes('-la') || args.includes('-al');

    const node = this.vfs.getNode(this.cwd);
    if (!node || !node.children) return;

    const items = Object.values(node.children);
    if (showLong) {
      items.forEach(item => {
        if (!showAll && item.name.startsWith('.')) return;
        const color = item.type === 'dir' ? '#00f3ff' : '#00ff9d';
        this.writeLine(`${item.perm} 1 ${item.owner} hero 4096 Aug 25 10:00 <span style="color:${color};">${item.name}</span>`);
      });
    } else {
      const names = items
        .filter(item => showAll || !item.name.startsWith('.'))
        .map(item => `<span style="color:${item.type === 'dir' ? '#00f3ff' : '#00ff9d'}; font-weight:bold;">${item.name}</span>`);
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
      this.writeLine('mkdir: missing operand');
      return;
    }
    this.vfs.createDirectory(path, this.cwd);
    this.updateVFSInspector();
  }

  cmdRm(args) {
    const target = args.find(a => !a.startsWith('-'));
    if (!target) return;
    this.vfs.removePath(target, this.cwd);
    this.updateVFSInspector();
  }

  cmdCat(path) {
    if (!path) return;
    const node = this.vfs.getNode(path, this.cwd);
    if (!node) this.writeLine(`cat: ${path}: No such file or directory`);
    else if (node.type === 'dir') this.writeLine(`cat: ${path}: Is a directory`);
    else this.writeLine(node.content || '');
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
        const existingContent = existingNode ? existingNode.content + '\n' : '';
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
    const pattern = args[0] ? args[0].replace(/^["']|["']$/g, '') : '';
    const file = args[1];
    const node = this.vfs.getNode(file, this.cwd);
    if (!node || node.type !== 'file') {
      this.writeLine(`grep: ${file}: No such file`);
      return;
    }
    const lines = node.content.split('\n');
    lines.forEach(line => {
      if (line.includes(pattern)) {
        const highlighted = line.replace(new RegExp(pattern, 'g'), `<span style="color:#ff3366; font-weight:bold;">${pattern}</span>`);
        this.writeLine(highlighted);
      }
    });
  }

  cmdChmod(args) {
    if (args.length < 2) return;
    const perm = args[0];
    const file = args[1];
    const node = this.vfs.getNode(file, this.cwd);
    if (node) {
      if (perm === '+x') node.perm = 'rwxr-xr-x';
      else if (perm === '755') node.perm = 'rwxr-xr-x';
      else if (perm === '600') node.perm = 'rw-------';
      this.writeLine(`changed permissions of ${file} to ${node.perm}`);
    }
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
            <div class="card" style="border-color: var(--neon-green); background: rgba(0,255,157,0.1);">
              <h3 style="color: var(--neon-green);"><i class="fas fa-check-circle"></i> QUEST COMPLETED!</h3>
              <p>Great job! You earned <strong>+${data.xp_earned} XP</strong>!</p>
              ${data.new_badges && data.new_badges.length > 0 ? `<p style="color:var(--neon-gold);">Unlocked Badges: ${data.new_badges.join(', ')}</p>` : ''}
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
