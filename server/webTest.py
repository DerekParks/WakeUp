#!/usr/bin/env python
import socket
import struct
from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api, reqparse
import flask_restful
from flask_restful.utils import cors


parser = reqparse.RequestParser()

app = Flask(__name__)
api = Api(app)

_MACS = {
}

def check_mac(macaddress):
    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')
    return macaddress

def wake_on_lan(macaddress):
    """ Switches on remote computers using WOL. """
    print "waking up", macaddress
    macaddress = check_mac(macaddress)
 
    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = '' 

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))

def abort_if_machine_doesnt_exist(machine):
    if machine not in _MACS.keys():
        abort(404, "Machine {} doesn't exist".format(machine))

class MACSList(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
      return jsonify(_MACS)

    def post(self):
      args = parser.parse_args()
      jsonArgs = request.get_json()
      if not jsonArgs:
        abort(400, "Could not parse JSON") 

      macaddress = jsonArgs['mac']
      try:
        macaddress = check_mac(macaddress)
      except ValueError:
        abort(400, "Invalid MACS address")

      _MACS[jsonArgs['name']] = macaddress
      return args, 201

class MACS(Resource):
    @cors.crossdomain(origin='*')
    def get(self, machine):
        abort_if_machine_doesnt_exist(machine)
        return jsonify({machine: _MACS[machine]})

class Wakeup(Resource):
    @cors.crossdomain(origin='*')
    def get(self, machine):
        abort_if_machine_doesnt_exist(machine)
        wake_on_lan(_MACS[machine])
                
        return jsonify({machine: _MACS[machine]})

api.add_resource(MACSList, '/machines')
api.add_resource(MACS, '/<string:machine>')
api.add_resource(Wakeup, '/wakeup/<string:machine>')

#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
  from tornado.wsgi import WSGIContainer
  from tornado.httpserver import HTTPServer
  from tornado.ioloop import IOLoop

  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(5000)
  IOLoop.instance().start()

