import threading
from http.server import ThreadingHTTPServer
from http.server import SimpleHTTPRequestHandler
import cgi

key_lock = threading.Lock()
votes = []


class MyHttpRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith('/welcome'):
            self.path = 'welcome.html'
        if self.path.endswith('/vote'):
            self.path = 'vote_form.html'

        if self.path.endswith(".jpg"):
            file = open(self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(file.read())
            file.close()

        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):

        if self.path.endswith('/vote'):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            content_length = int(self.headers.get('Content-length'))
            pdict['CONTENT-LENGTH'] = content_length
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

                # TODO: Critical section open
                key_lock.acquire()

                first_name = fields.get('first_name')
                last_name = fields.get('last_name')
                sex = fields.get('sex')
                working = fields.get('working')
                print(first_name[0], last_name[0], sex[0], working[0])
                voter = {first_name[0], last_name[0], sex[0], working[0]}
                votes.append(voter)
                f = open("vote_db", "a")
                f.write(f'\n {len(votes)}: {first_name[0]} {last_name[0]}, {sex[0]}, working: {working[0]}')
                f.close()

                key_lock.release()
                # TODO: Critical section close

            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()


request_handler = MyHttpRequestHandler

my_server = ThreadingHTTPServer(("localhost", 8080), request_handler)

print('Server is running...')
my_server.serve_forever()
