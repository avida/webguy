#!/usr/bin/python3
import sys
import logging
from plumbum import cli
from flask_socketio import SocketIO


class ServerApplication(cli.Application):
    server_type = cli.switches.SwitchAttr(["--app", "-a"], str, 
    default = "raspi",
    help = 
    """Specify type of server to run """)

    def main(self, *srcfiles):
        if self.server_type == "raspi":
            print ("rapsi")
            sys.path.append("raspi")
            from flask_raspi import app
        socketio = SocketIO(app)
        socketio.run(app, host="0.0.0.0", port=80)

log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)
    
ServerApplication.run()
# vim: ts=4 sw=4 et
