#!/usr/bin/env python

__author__  = 'Jamie Davies'
__version__ = '0.0.1'

import gtk


class JamPacketApp(gtk.Window):
    def __init__(self):
        super(JamPacketApp, self).__init__()

        self.connect("destroy", gtk.main_quit)

        self.set_title('JamPacket v{}'.format(__version__))
        self.set_size_request(300, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        self.show()


JamPacketApp()
gtk.main()
