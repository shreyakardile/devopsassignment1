import os, tempfile, unittest, threading, urllib.request, urllib.parse, json
from http.server import ThreadingHTTPServer
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app

class StudentPlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        app.DB_PATH = __import__('pathlib').Path(cls.tmp.name) / 'test.db'
        app.init_db()
        cls.server = ThreadingHTTPServer(('127.0.0.1',0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.tmp.cleanup()
    def setUp(self):
        with app.connect() as db:
            db.execute('DELETE FROM students')
            db.executemany('INSERT INTO students(name,roll_no,course,email,marks) VALUES(?,?,?,?,?)', [
                ('Aarav Patil','STU-1001','Computer Science','aarav@example.com',86),
                ('Isha Deshmukh','STU-1002','Information Technology','isha@example.com',92),
                ('Rohan Kulkarni','STU-1003','Computer Science','rohan@example.com',74),
                ('Ananya Shah','STU-1004','Electronics','ananya@example.com',88),
            ])
    def test_health_endpoint(self):
        with urllib.request.urlopen(self.base+'/health') as r: self.assertEqual(json.loads(r.read())['status'],'ok')
    def test_seeded_student_records(self):
        with urllib.request.urlopen(self.base+'/api/students') as r: self.assertEqual(len(json.loads(r.read())),4)
    def test_add_student(self):
        data=urllib.parse.urlencode({'name':'Test Student','roll_no':'TEST-1','course':'Computer Science','email':'test@example.com','marks':'90'}).encode()
        req=urllib.request.Request(self.base+'/add',data=data,method='POST')
        with urllib.request.urlopen(req) as response: self.assertEqual(response.status,200)
        with urllib.request.urlopen(self.base+'/api/students') as r: self.assertEqual(len(json.loads(r.read())),5)
    def test_duplicate_roll_number_rejected(self):
        data=urllib.parse.urlencode({'name':'Duplicate','roll_no':'STU-1001','course':'CS','email':'dup@example.com','marks':'70'}).encode()
        req=urllib.request.Request(self.base+'/add',data=data,method='POST')
        with self.assertRaises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
        self.assertEqual(e.exception.code,409)
    def test_homepage_and_csv_export(self):
        with urllib.request.urlopen(self.base+'/') as r: self.assertIn(b'Student overview',r.read())
        with urllib.request.urlopen(self.base+'/export') as r: self.assertIn(b'roll_no',r.read())

if __name__=='__main__': unittest.main(verbosity=2)
