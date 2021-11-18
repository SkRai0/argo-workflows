import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Plugin(BaseHTTPRequestHandler):

    def args(self):
        return json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

    def reply(self, reply):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(reply).encode("UTF-8"))

    def unsupported(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/v1/template.execute':
            args = self.args()
            if 'python' in args['template'].get('plugin', {}):
                try:
                    expression = args['template']['plugin']['python']['expression']
                    # obvs, this is bad, untrusted code execution
                    result = eval(expression)
                    self.reply({'node': {'phase': 'Succeeded', 'message': str(result)}})
                except Exception as err:
                    self.reply({'node': {'phase': 'Failed', 'message': repr(err)}})
            else:
                self.reply({})
        else:
            self.unsupported()


if __name__ == '__main__':
    httpd = HTTPServer(('', 7984), Plugin)
    httpd.serve_forever()
