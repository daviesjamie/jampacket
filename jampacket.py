#!/usr/bin/env python

__author__  = 'Jamie Davies'
__version__ = '0.0.1'

import gtk
import netifaces as ni


class JamPacketApp(gtk.Window):

    def __init__(self):
        super(JamPacketApp, self).__init__()

        self.connect("destroy", gtk.main_quit)

        self.set_title('JamPacket v{}'.format(__version__))
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)

        cb_iface = gtk.combo_box_new_text()
        cb_iface.connect('changed', self.iface_changed)
        for iface in ni.interfaces():
            if iface.startswith('eth') or iface.startswith('wlan'):
                cb_iface.append_text('{} - {}'.format(
                    iface, ni.ifaddresses(iface)[ni.AF_INET][0]['addr']))

        cb_proto = gtk.combo_box_new_text()
        cb_proto.connect('changed', self.protocol_changed)
        cb_proto.append_text('ARP')
        cb_proto.append_text('ICMP')
        cb_proto.append_text('IGMP')

        table = gtk.Table(4, 2, False)
        table.set_row_spacings(10)
        table.set_col_spacings(10)

        table.attach(gtk.Label("Interface"), 0, 1, 0, 1)
        table.attach(cb_iface, 1, 2, 0, 1)
        table.attach(gtk.Label("Protocol"), 0, 1, 1, 2)
        table.attach(cb_proto, 1, 2, 1, 2)

        self.add(table)

        self.show_all()

    def iface_changed(self, widget):
        print 'Interface changed to {}'.format(widget.get_active_text())

    def protocol_changed(self, widget):
        print 'Changed to {}'.format(widget.get_active_text())


JamPacketApp()
gtk.main()
