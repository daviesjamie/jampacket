#!/usr/bin/env python

__author__  = 'Jamie Davies'
__version__ = '0.0.1'

import gtk
import netifaces as ni
import re
import sys

ARP = 'ARP Request'
ICMP_PING = 'ICMP Echo Request (Ping)'
IGMP_QUERY = 'IGMP Membership Query'
IGMP_JOIN = 'IGMPv2 Membership Report'
IGMP_LEAVE = 'IGMPv2 Leave Group'


def is_ip(ip):
    """Takes a string and returns whether is matches a valid IPv4 address."""
    match = re.match('^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', ip)
    if not match:
        return False
    quad = []
    for number in match.groups():
        quad.append(int(number))
    for number in quad:
        if number > 255 or number < 0:
            return False
    return True


class JamPacketApp(gtk.Window):

    def __init__(self):
        super(JamPacketApp, self).__init__()

        self.connect("destroy", gtk.main_quit)

        self.set_title('JamPacket v{}'.format(__version__))
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(10)

        try:
            self.set_icon_from_file("strawberry.png")
        except Exception, e:
            sys.stderr.write(e.message)

        cb_iface = gtk.combo_box_new_text()
        cb_iface.connect('changed', self.iface_changed)
        for iface in ni.interfaces():
            if iface.startswith('eth') or iface.startswith('wlan'):
                cb_iface.append_text('{} - {}'.format(
                    iface, ni.ifaddresses(iface)[ni.AF_INET][0]['addr']))

        cb_proto = gtk.combo_box_new_text()
        cb_proto.connect('changed', self.protocol_changed)
        cb_proto.append_text(ARP)
        cb_proto.append_text(ICMP_PING)
        cb_proto.append_text(IGMP_QUERY)
        cb_proto.append_text(IGMP_JOIN)
        cb_proto.append_text(IGMP_LEAVE)

        e_target = gtk.Entry()
        e_target.add_events(gtk.gdk.KEY_RELEASE_MASK)
        e_target.connect('key-release-event', self.target_changed)

        btn_send = gtk.Button('Send Packet')
        btn_send.connect('clicked', self.send)

        table = gtk.Table(4, 2, False)
        table.set_row_spacings(10)
        table.set_col_spacings(10)

        table.attach(gtk.Label("Interface"), 0, 1, 0, 1)
        table.attach(cb_iface, 1, 2, 0, 1)
        table.attach(gtk.Label("Protocol"), 0, 1, 1, 2)
        table.attach(cb_proto, 1, 2, 1, 2)
        table.attach(gtk.Label("IP"), 0, 1, 2, 3)
        table.attach(e_target, 1, 2, 2, 3)
        table.attach(btn_send, 0, 2, 3, 4)

        self.add(table)

        self.show_all()

    def iface_changed(self, widget):
        self.iface = widget.get_active_text().split(' ')[0]
        self.source = widget.get_active_text().split(' ')[2]

    def protocol_changed(self, widget):
        self.protocol = widget.get_active_text()

    def target_changed(self, widget, event):
        self.target = widget.get_text()
        if is_ip(widget.get_text()):
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('green'))
        else:
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('red'))

    def send(self, widget):
        if is_ip(self.target):
            print '{} packet sent from {} ({}) to {}'.format(
                self.protocol, self.iface, self.source, self.target)
        else:
            md = gtk.MessageDialog(self,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_WARNING,
                                   gtk.BUTTONS_CLOSE,
                                   '{} is not a valid IP address'.format(self.target))
            md.run()
            md.destroy()


JamPacketApp()
gtk.main()
