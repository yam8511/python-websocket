#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Flask, request, Response
from websocket_server import WebsocketServer
import logging
import json
import threading
import os.path
import urllib

clients = {}


def new_client(client, server):  # 有新的使用者連線
    print("new client => ", client)


def client_left(client, server):  # 有使用者離線
    if client is None:
        return
    print(" ===> ", client)
    server.send_message_to_all("%s 離開聊天室囉!" % clients[client['id']])
    del clients[client['id']]


def message_received(client, server, message):  # 接收到使用者訊息
    data = json.loads(message)
    print("Message => ", data)
    if data['action'] == 'join':
        name = urllib.parse.unquote(data['name'])
        clients[client['id']] = name
        server.send_message_to_all("%s 加入聊天室囉!" % name)
    elif data['action'] == 'send':
        server.send_message_to_all("%s: %s" % (
            clients[client['id']], urllib.parse.unquote(data['text'])
        ))


def runWebsocket():
    server = WebsocketServer(9001, host='0.0.0.0')
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


# set the project root directory as the static folder, you can set others.
app = Flask(__name__)


@app.route('/')
def root():
    content = """
    <!DOCTYPE html>
        <html>

        <head>
            <meta charset="utf-8">
            <title>多人聊天室</title>
            <style>
                body {
                    overflow: hidden;
                }

                h2 {
                    margin-top: 30px;
                    text-align: center;
                    background-color: #393D49;
                    color: #fff;
                    padding: 15px 0;
                }

                #chat {
                    text-align: center;
                }

                #win {
                    margin-top: 20px;
                    text-align: center;
                }

                #sse {
                    margin-top: 10px;
                    text-align: center;
                }

                button {
                    background-color: #009688;
                    color: #fff;
                    height: 40px;
                    border: 0;
                    border-radius: 3px 3px;
                    padding-left: 10px;
                    padding-right: 10px;
                    cursor: pointer;
                }

                #join {
                    display: flex;
                    padding-left: 37%;
                }

                #online {
                    display: none;
                }
            </style>
        </head>

        <body>
            <h2>多人聊天室</h2>

            <div id="join">
                <input type="text" name="nickname" id="nickname" placeholder="輸入暱稱..." />
                <button onclick="join()">加入</button>
            </div>

            <div id="online">
                <div id="chat">
                    <textarea id="history" cols="80" rows="20"></textarea>
                </div>

                <div id="win">
                    <textarea id="messagewin" cols="80" rows="5"></textarea>
                </div>

                <div id="sse">
                    <button onclick="sendMessage()">傳送對話</button>
                </div>
            </div>

            <script>
                let isJoin = false
                let ws;

                function join() {
                    if (isJoin) return;
                    let name = document.getElementById('nickname').value.trim()
                    console.log("Join", name)
                    isJoin = true;
                    document.getElementById('join').style.display = 'none'
                    document.getElementById('online').style.display = 'block'

                    if ("WebSocket" in window) {
                        if (window.location.hostname === '') {
                            ws = new WebSocket("ws://localhost:9001")
                        } else {
                            ws = new WebSocket("ws://" + window.location.hostname + ":9001")
                        }
                        ws.onopen = function (e) {
                            console.log('==>', e)
                            ws.send(JSON.stringify({
                                action: 'join',
                                name: encodeURIComponent(name),
                            }))
                        }
                        ws.onmessage = function (e) {
                            let txt = document.getElementById('history').value
                            console.log('history -> ', txt)
                            if (txt === '') {
                                document.getElementById('history').value = e.data
                            } else {
                                document.getElementById('history').value = txt + '\\n' + e.data
                            }
                        }
                        ws.onclose = function () { isJoin = false }
                    } else {
                        isJoin = false
                        window.alert('您的瀏覽器不支援 Websocket!')
                    }
                }

                function sendMessage() {
                    let msg = document.getElementById('messagewin').value.trim()
                    console.log('Send', msg)
                    if (msg && msg !== '' && ws) {
                        ws.send(JSON.stringify({
                            action: 'send',
                            text: encodeURIComponent(msg),
                        }));
                        document.getElementById('messagewin').value = ''
                    }
                }
            </script>
        </body>

        </html>
    """
    return Response(content, mimetype="text/html")


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


@app.route('/dev')
def dev():
    content = get_file('index.html')
    return Response(content, mimetype="text/html")


app.run(host='0.0.0.0', port=8080)
