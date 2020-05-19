from flask import Flask, request, Response
from websocket_server import WebsocketServer
import json
import threading
import os.path

clients = {}


def new_client(client, server):  # 有新的使用者連線
    print("new client => ", client)


def client_left(client, server):  # 有使用者離線
    print("Client(%d) disconnected" % client['id'])


def message_received(client, server, message):  # 接收到使用者訊息
    data = json.loads(message)
    print("Message => ", data)
    if data['action'] == 'join':
        clients[client['id']] = data['name']
        server.send_message_to_all("%s 加入聊天室囉!" % data['name'])
    elif data['action'] == 'send':
        server.send_message_to_all("%s: %s" % (
            clients[client['id']], data['text']
        ))


def runWebsocket():
    server = WebsocketServer(9001)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()


class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Websocket Starting")
        runWebsocket()


thread1 = myThread()
thread1.start()


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)


# set the project root directory as the static folder, you can set others.
app = Flask(__name__)


@app.route('/')
def root():
    content = get_file('index.html')
    return Response(content, mimetype="text/html")


app.run(host='0.0.0.0', port=8080)
