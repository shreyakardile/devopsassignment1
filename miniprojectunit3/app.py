"""Student Record & Academic Management Platform — runnable standard-library demo.
This implementation uses Python's built-in HTTP server and SQLite so it runs offline.
See README for how to switch to Flask/Jenkins/Docker/Kubernetes in the assignment stack.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sqlite3, json, html, os

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('STUDENT_DB', BASE / 'students.db'))


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            email TEXT NOT NULL,
            marks REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        count = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        if count == 0:
            db.executemany('INSERT INTO students(name,roll_no,course,email,marks) VALUES(?,?,?,?,?)', [
                ('Aarav Patil','STU-1001','Computer Science','aarav@example.com',86),
                ('Isha Deshmukh','STU-1002','Information Technology','isha@example.com',92),
                ('Rohan Kulkarni','STU-1003','Computer Science','rohan@example.com',74),
                ('Ananya Shah','STU-1004','Electronics','ananya@example.com',88),
            ])


def page():
    with connect() as db:
        students = [dict(r) for r in db.execute('SELECT * FROM students ORDER BY id DESC')]
        total = len(students)
        avg = round(sum(s['marks'] for s in students) / total, 1) if total else 0
        courses = len(set(s['course'] for s in students))
        top = sum(1 for s in students if s['marks'] >= 85)
    rows = ''.join(f'''<tr><td><span class="avatar">{html.escape(s['name'][:1].upper())}</span><span class="student-name">{html.escape(s['name'])}</span></td><td><span class="roll">{html.escape(s['roll_no'])}</span></td><td>{html.escape(s['course'])}</td><td>{html.escape(s['email'])}</td><td><div class="score"><span>{s['marks']:g}%</span><div class="track"><i style="width:{max(0,min(100,s['marks']))}%"></i></div></div></td><td><span class="status">Active</span></td><td><form method="post" action="/delete" onsubmit="return confirm('Delete this student?')"><input type="hidden" name="id" value="{s['id']}"><button class="icon-btn" title="Delete student">⋯</button></form></td></tr>''' for s in students)
    if not rows: rows = '<tr><td colspan="7" class="empty">No students found. Add your first student.</td></tr>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CampusFlow | Student Records</title><link rel="stylesheet" href="/style.css"></head><body>
    <aside class="sidebar"><div class="brand"><div class="brand-mark">C</div><div><b>CampusFlow</b><small>ACADEMIC SUITE</small></div></div><div class="workspace">WORKSPACE</div><a class="nav active" href="/"><span>▦</span> Overview</a><a class="nav" href="#students"><span>♙</span> Students <em>{total}</em></a><a class="nav" href="#courses"><span>▤</span> Courses</a><a class="nav" href="#reports"><span>▥</span> Reports</a><div class="side-bottom"><div class="help-icon">?</div><div><b>Need a hand?</b><small>Visit help center</small></div><span class="arrow">↗</span></div></aside>
    <main class="main"><header><div class="crumb">Workspace <span>/</span> <b>Students</b></div><div class="head-right"><span class="live"><i></i> System operational</span><div class="bell">♧<b></b></div><div class="user"><div class="user-avatar">AD</div><div><b>Admin User</b><small>Administrator</small></div><span>⌄</span></div></div></header>
    <section class="welcome"><div><div class="eyebrow">ACADEMIC MANAGEMENT</div><h1>Student overview <span>✦</span></h1><p>Manage student records, track academic performance, and keep everything in one place.</p></div><button class="primary" onclick="document.getElementById('addPanel').classList.toggle('show')">＋ Add student</button></section>
    <section class="stats"><article class="stat"><div class="stat-top"><span>Total students</span><div class="stat-icon purple">♙</div></div><div class="stat-number">{total:02d}</div><div class="stat-foot"><span class="up">↗ Live count</span><span>registered records</span></div></article><article class="stat"><div class="stat-top"><span>Average marks</span><div class="stat-icon blue">▥</div></div><div class="stat-number">{avg}<small>%</small></div><div class="stat-foot"><span class="up">↗ Academic</span><span>overall average</span></div></article><article class="stat"><div class="stat-top"><span>Active courses</span><div class="stat-icon orange">▤</div></div><div class="stat-number">{courses:02d}</div><div class="stat-foot"><span class="neutral">● Current</span><span>unique courses</span></div></article><article class="stat"><div class="stat-top"><span>High performers</span><div class="stat-icon green">✧</div></div><div class="stat-number">{top:02d}</div><div class="stat-foot"><span class="up">↗ 85% and above</span><span>students excelling</span></div></article></section>
    <section id="addPanel" class="add-panel"><div class="panel-heading"><div><h2>Add a student</h2><p>Enter student and academic details below.</p></div><button class="close" onclick="document.getElementById('addPanel').classList.remove('show')">×</button></div><form action="/add" method="post" class="add-form"><label>Full name<input required name="name" placeholder="e.g. Priya Sharma"></label><label>Roll number<input required name="roll_no" placeholder="STU-1005"></label><label>Course<input required name="course" placeholder="Computer Science"></label><label>Email address<input required type="email" name="email" placeholder="student@example.com"></label><label>Marks (%)<input required type="number" min="0" max="100" step="0.1" name="marks" placeholder="85"></label><button class="primary" type="submit">Save student</button></form></section>
    <section class="table-card" id="students"><div class="table-heading"><div><h2>All students <span class="count">{total}</span></h2><p>A complete list of registered student records.</p></div><div class="table-actions"><div class="search">⌕ <input id="search" placeholder="Search students..." oninput="filterRows()"></div><button class="secondary" onclick="location.href='/export'">↓ Export CSV</button></div></div><div class="table-wrap"><table><thead><tr><th>STUDENT</th><th>ROLL NO.</th><th>COURSE</th><th>EMAIL ADDRESS</th><th>MARKS</th><th>STATUS</th><th></th></tr></thead><tbody id="studentRows">{rows}</tbody></table></div><div class="table-footer"><span>Showing <b id="visibleCount">{total}</b> of {total} students</span><span>Data stored locally · SQLite <span class="footer-dot">●</span></span></div></section>
    <footer><span>© 2026 CampusFlow Academic Suite</span><span><i></i> All systems normal <b>·</b> v1.0.0</span></footer></main><script>function filterRows(){{let q=document.getElementById('search').value.toLowerCase(),rows=[...document.querySelectorAll('#studentRows tr')],n=0;rows.forEach(r=>{{let show=r.innerText.toLowerCase().includes(q);r.style.display=show?'':'none';if(show)n++}});document.getElementById('visibleCount').innerText=n}}</script></body></html>'''

CSS = r'''
@import url('');
*{box-sizing:border-box}body{margin:0;background:#f7f8fc;color:#20243a;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px}.sidebar{width:232px;background:#fff;border-right:1px solid #e9eaf1;position:fixed;inset:0 auto 0 0;padding:27px 16px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:11px;padding:0 8px 34px}.brand-mark{width:37px;height:37px;border-radius:12px;background:linear-gradient(145deg,#6b57e8,#8e7af8);color:#fff;font-size:23px;font-weight:800;display:grid;place-items:center;box-shadow:0 5px 12px #7868df35}.brand b{font-size:17px;letter-spacing:-.5px}.brand small{display:block;font-size:9px;color:#9397aa;letter-spacing:1.5px;margin-top:3px}.workspace{font-size:10px;font-weight:700;letter-spacing:1.1px;color:#a1a4b5;padding:0 12px 12px}.nav{display:flex;align-items:center;gap:12px;padding:12px 13px;margin:2px 0;border-radius:9px;text-decoration:none;color:#777b91;font-weight:550}.nav span{font-size:17px;width:19px;text-align:center}.nav.active{background:#f0edff;color:#6854d8;font-weight:700}.nav em{margin-left:auto;background:#e6e0ff;padding:3px 7px;border-radius:5px;font-size:10px;font-style:normal}.side-bottom{margin-top:auto;border:1px solid #eeeef5;border-radius:11px;padding:13px 10px;display:flex;align-items:center;gap:9px}.help-icon{height:28px;width:28px;background:#f0edff;color:#705de1;border-radius:8px;display:grid;place-items:center;font-weight:800}.side-bottom b{font-size:11px}.side-bottom small{display:block;color:#9296a9;margin-top:4px;font-size:10px}.arrow{margin-left:auto;color:#999}.main{margin-left:232px;padding:0 34px;max-width:1800px}header{height:76px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #e9eaf1}.crumb{color:#9a9daf}.crumb span{padding:0 9px;color:#c6c7d1}.crumb b{color:#44485e;font-weight:600}.head-right{display:flex;align-items:center;gap:23px}.live{color:#73778b;font-size:11px}.live i,footer i{display:inline-block;width:6px;height:6px;background:#38b982;border-radius:50%;margin-right:5px}.bell{position:relative;font-size:20px;color:#74788c}.bell b{position:absolute;right:-1px;top:1px;width:6px;height:6px;background:#ef7e85;border-radius:50%;border:1px solid white}.user{display:flex;align-items:center;gap:9px;border-left:1px solid #e9eaf1;padding-left:20px}.user-avatar{width:34px;height:34px;border-radius:50%;background:#e7e1ff;color:#6855d8;display:grid;place-items:center;font-weight:800;font-size:11px}.user b{display:block;font-size:11px}.user small{display:block;color:#9699aa;margin-top:4px;font-size:10px}.user>span{color:#8c90a3;margin-left:7px}.welcome{display:flex;justify-content:space-between;align-items:center;padding:29px 0 23px}.eyebrow{font-size:10px;letter-spacing:1.35px;font-weight:750;color:#7866dc;margin-bottom:9px}.welcome h1{font-size:27px;letter-spacing:-.8px;margin:0;font-weight:750}.welcome h1 span{color:#8b78ee;font-size:18px}.welcome p{margin:9px 0 0;color:#85899c;font-size:12px}.primary{border:0;background:#705be5;color:#fff;padding:11px 17px;border-radius:8px;font-weight:650;font-size:12px;box-shadow:0 4px 9px #715de52b;cursor:pointer}.primary:hover{background:#5e49d3}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px}.stat{background:#fff;border:1px solid #ececf3;border-radius:12px;padding:18px 19px 15px;box-shadow:0 2px 5px #272c4a03}.stat-top{display:flex;justify-content:space-between;align-items:center;color:#777b90;font-size:11px;font-weight:550}.stat-icon{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-size:17px}.purple{background:#f0edff;color:#7a66e7}.blue{background:#e9f4ff;color:#5099e8}.orange{background:#fff2e4;color:#e69a43}.green{background:#e5f8ef;color:#39b982}.stat-number{font-size:29px;font-weight:750;letter-spacing:-1px;margin:9px 0 10px}.stat-number small{font-size:16px;margin-left:2px}.stat-foot{display:flex;gap:7px;align-items:center;color:#a0a3b2;font-size:9px}.up{color:#36a87d;font-weight:650}.neutral{color:#e19a42;font-weight:650}.table-card{background:white;border:1px solid #e9eaf1;border-radius:12px;margin-top:23px;overflow:hidden}.table-heading{display:flex;align-items:center;justify-content:space-between;padding:20px 21px 17px}.table-heading h2,.panel-heading h2{font-size:15px;margin:0;font-weight:750}.count{font-size:10px;color:#7764df;background:#f0edff;border-radius:5px;padding:3px 7px;margin-left:5px;vertical-align:2px}.table-heading p,.panel-heading p{margin:6px 0 0;color:#9699aa;font-size:11px}.table-actions{display:flex;gap:10px}.search{border:1px solid #e8e9f0;border-radius:7px;padding:8px 10px;color:#999daf;display:flex;align-items:center;gap:6px;font-size:19px;width:185px}.search input{border:0;outline:0;width:100%;font:inherit;font-size:11px;color:#45495f}.search input::placeholder{color:#a5a8b7}.secondary{border:1px solid #e7e8ef;background:#fff;color:#565a70;border-radius:7px;padding:8px 12px;font-weight:600;font-size:11px;cursor:pointer}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:870px}thead{background:#fafaff}th{text-align:left;font-size:9px;letter-spacing:.65px;color:#9699aa;font-weight:750;padding:12px 13px;border-top:1px solid #f0f0f5;border-bottom:1px solid #f0f0f5}th:first-child,td:first-child{padding-left:21px}td{padding:13px 13px;border-bottom:1px solid #f2f2f7;color:#777b90;font-size:10px;white-space:nowrap}tbody tr:last-child td{border-bottom:0}.avatar{display:inline-grid;place-items:center;width:29px;height:29px;border-radius:9px;background:#eeeaff;color:#715ee0;font-size:11px;font-weight:750;vertical-align:middle;margin-right:9px}.student-name{color:#383c53;font-weight:650;font-size:11px}.roll{font-family:ui-monospace,monospace;background:#f6f6fb;padding:5px 6px;border-radius:4px;color:#686d84;font-size:10px}.score{display:flex;align-items:center;gap:8px;color:#4e536b;font-weight:650}.track{width:45px;height:4px;border-radius:6px;background:#eeeef6;overflow:hidden}.track i{height:100%;display:block;background:#7967e8;border-radius:6px}.status{background:#e7f8f0;color:#2b9b70;padding:5px 8px;border-radius:5px;font-size:9px;font-weight:700}.icon-btn{border:0;background:transparent;color:#9a9daf;font-size:18px;cursor:pointer}.table-footer{padding:14px 21px;border-top:1px solid #f0f0f5;display:flex;justify-content:space-between;color:#a0a3b2;font-size:10px}.table-footer b{color:#656980}.footer-dot{color:#37b881;font-size:8px;margin-left:4px}.add-panel{display:none;background:white;border:1px solid #e9eaf1;border-radius:12px;padding:20px;margin-top:10px}.add-panel.show{display:block}.panel-heading{display:flex;justify-content:space-between;margin-bottom:17px}.close{border:0;background:transparent;font-size:22px;color:#999}.add-form{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px}.add-form label{font-size:11px;color:#777b90;display:flex;flex-direction:column;gap:7px}.add-form input{border:1px solid #e7e8f0;border-radius:7px;padding:10px;font:inherit;outline-color:#8774ed}.add-form button{align-self:end;justify-self:start}footer{display:flex;justify-content:space-between;color:#a3a6b5;font-size:10px;padding:20px 1px 25px}footer b{font-weight:400;padding:0 5px;color:#d1d2dc}form{margin:0}input[type=hidden]{display:none}.empty{text-align:center;padding:28px;color:#999} @media(max-width:1100px){.sidebar{width:190px}.main{margin-left:190px;padding:0 20px}.stats{gap:10px}.stat{padding:14px}.head-right{gap:12px}}@media(max-width:800px){.sidebar{display:none}.main{margin-left:0;padding:0 14px}.stats{grid-template-columns:repeat(2,1fr)}.welcome{gap:15px;align-items:flex-start}.welcome h1{font-size:23px}.head-right .live,.user small,.user>span{display:none}.table-heading{align-items:flex-start;gap:15px;flex-direction:column}.table-actions{width:100%}.search{flex:1}.add-form{grid-template-columns:1fr 1fr}header{height:62px}}'''

class Handler(BaseHTTPRequestHandler):
    def send(self, body, status=200, content_type='text/html; charset=utf-8'):
        raw = body if isinstance(body, bytes) else body.encode()
        self.send_response(status); self.send_header('Content-Type', content_type); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/style.css': return self.send(CSS, content_type='text/css; charset=utf-8')
        if path == '/health': return self.send(json.dumps({'status':'ok','service':'student-record-platform'}), content_type='application/json')
        if path == '/api/students':
            with connect() as db: data = [dict(r) for r in db.execute('SELECT * FROM students ORDER BY id')]
            return self.send(json.dumps(data), content_type='application/json')
        if path == '/export':
            import csv, io
            out=io.StringIO(); w=csv.writer(out); w.writerow(['id','name','roll_no','course','email','marks'])
            with connect() as db:
                for r in db.execute('SELECT id,name,roll_no,course,email,marks FROM students ORDER BY id'): w.writerow(tuple(r))
            return self.send(out.getvalue(), content_type='text/csv; charset=utf-8')
        if path == '/': return self.send(page())
        return self.send('Not found',404,'text/plain; charset=utf-8')
    def do_POST(self):
        path = urlparse(self.path).path
        size = int(self.headers.get('Content-Length','0')); form = parse_qs(self.rfile.read(size).decode())
        get = lambda k: form.get(k,[''])[0].strip()
        if path == '/add':
            name,roll,course,email,marks=get('name'),get('roll_no'),get('course'),get('email'),get('marks')
            try:
                if not all([name,roll,course,email,marks]): raise ValueError('All fields are required')
                score=float(marks)
                if score < 0 or score > 100: raise ValueError('Marks must be between 0 and 100')
                with connect() as db: db.execute('INSERT INTO students(name,roll_no,course,email,marks) VALUES(?,?,?,?,?)',(name,roll,course,email,score))
                self.send_response(303); self.send_header('Location','/'); self.end_headers()
            except sqlite3.IntegrityError: self.send('Roll number already exists',409,'text/plain; charset=utf-8')
            except (ValueError,sqlite3.Error) as e: self.send(str(e),400,'text/plain; charset=utf-8')
            return
        if path == '/delete':
            try:
                with connect() as db: db.execute('DELETE FROM students WHERE id=?',(int(get('id')),))
                self.send_response(303); self.send_header('Location','/'); self.end_headers()
            except (ValueError,sqlite3.Error): self.send('Invalid student ID',400,'text/plain; charset=utf-8')
            return
        self.send('Not found',404,'text/plain; charset=utf-8')
    def log_message(self, *_): pass

if __name__ == '__main__':
    init_db()
    port=int(os.environ.get('PORT','8000'))
    print(f'Student Record Platform running at http://127.0.0.1:{port}')
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
