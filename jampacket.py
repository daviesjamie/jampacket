#!/usr/bin/env python

__author__  = 'Jamie Davies'
__version__ = '0.0.1'

import gtk


class JamPacketApp(gtk.Window):

    def __init__(self):
        super(JamPacketApp, self).__init__()

        self.connect("destroy", gtk.main_quit)

        self.set_title('JamPacket v{}'.format(__version__))
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)

        cb_proto = gtk.combo_box_new_text()
        cb_proto.connect('changed', self.protocol_changed)
        cb_proto.append_text('ARP')
        cb_proto.append_text('ICMP')
        cb_proto.append_text('IGMP')

        table = gtk.Table(4, 2, False)
        table.set_row_spacings(10)
        table.set_col_spacings(10)

        table.attach(gtk.Label("Protocol"), 0, 1, 0, 1)
        table.attach(cb_proto, 1, 2, 0, 1)

        self.add(table)

        self.show_all()

    def protocol_changed(self, widget):
        print 'Changed to {}'.format(widget.get_active_text())


JamPacketApp()
gtk.main()
