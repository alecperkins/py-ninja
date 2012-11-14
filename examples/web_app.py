"""
An example web app that displays a list of devices, with links to a page for
each device's data. The device page updates every 2 seconds with the latest
heartbeat.

Note: requires Flask
"""

from _examples import *

from flask import Flask
from ninja.api import NinjaAPI

import json



api = NinjaAPI(secrets.ACCESS_TOKEN)
app = Flask(__name__)



device_cache = {}

BASE_HTML = """
    <link rel="icon" href="">
    <style>
        table {
            font-family: monospace;
        }
        td.label {
            padding-right: 1em;
            font-style: italic;
        }
        body {
            max-width: 600px;
            margin: 0 auto;
            padding-top: 1em;
        }
    </style>
    <script src="//cdnjs.cloudflare.com/ajax/libs/zepto/1.0rc1/zepto.min.js"></script>
"""

def getDevice(guid):
    if not guid in device_cache:
        device = api.getDevice(guid)
        device_cache[guid] = device
    else:
        device = device_cache[guid]
    return device



@app.route('/')
def hello():
    user = api.getUser()
    devices = api.getDevices()
    html = BASE_HTML

    html += """
        <h1>Devices for {user.name}</h1>
        <p>User ID: ({user.id})</p>
    """.format(user=user)

    html += """
        <table>
        <thead>
            <tr>
                <th>Device</th>
                <th>ID</th>
            </tr>
        </thead>
        <tbody>
        """

    for device in devices:
        device_cache[device.guid] = device
        html += """
            <tr>
                <td class="label">{device}</td>
                <td><a href="/{device.guid}/">{device.guid} &raquo;</a></td>
            </tr>
        """.format(device=device)
    html += '</tbody></table>'
    return html



@app.route('/<guid>/')
def showDevice(guid):
    device = getDevice(guid)

    html = BASE_HTML

    html += """
        <h1>{device}</h1>
        <a href="/">&laquo; index</a>        
        <p>Device heartbeat every 2 seconds [<a href="heartbeat.json">raw</a>]</p>
        <table>
    """.format(device=device)

    for field in device.asDict():
        html += "<tr><td class='label'>%s</td><td>&hellip;</td></tr>" % (field,)

    html += '</table>'

    html += """
        <script>
            var $table = $('table');

            function fetch(){
                $.getJSON('heartbeat.json', function(response){
                    render(response);
                });
            }

            function render(device){
                var html = '';
                for(k in device){
                    html += '<tr><td class="label">' + k + '</td><td>' + device[k] + '</td></tr>';
                }
                $table.html(html);
            }
            setInterval(fetch, 2000);
        </script>
    """
    return html



@app.route('/<guid>/heartbeat.json')
def deviceHeartbeat(guid):
    device = getDevice(guid)
    device.heartbeat()
    return json.dumps(device.asDict(for_json=True))



app.run(debug=True)


