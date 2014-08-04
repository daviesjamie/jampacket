#!/usr/bin/env python

__author__  = 'Jamie Davies'
__version__ = '1.0.0'

import gtk
import netifaces as ni
import re
import socket
import sys

# Disable annoying logging from Scapy
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)

from scapy.all import ARP, Ether, ICMP, IP
from scapy.contrib.igmp import IGMP

PROTO_ARP        = 'ARP Request'
PROTO_ICMP_PING  = 'ICMP Echo Request (Ping)'
PROTO_IGMP_QUERY = 'IGMP Membership Query'
PROTO_IGMP_JOIN  = 'IGMPv2 Membership Report'
PROTO_IGMP_LEAVE = 'IGMPv2 Leave Group'

ICMP_PING  = 8
IGMP_QUERY = 0x11
IGMP_JOIN  = 0x16
IGMP_LEAVE = 0x17


def is_ip(ip):
    """Takes a string and returns whether is matches a valid IPv4 address."""
    if not ip:
        return False
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


def create_arp(src_mac, src_ip, dst_ip):
    """Creates a new ARP packet based on the given addresses."""
    a = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
    b = ARP(hwsrc=src_mac, hwdst='ff:ff:ff:ff:ff:ff', psrc=src_ip, pdst=dst_ip)
    return a / b


def create_icmp(src_mac, src_ip, dst_ip):
    """Creates a new ICMP packet based on the given addresses."""
    a = Ether(src=src_mac)
    b = IP(src=src_ip, dst=dst_ip)
    c = ICMP(type=ICMP_PING)
    return a / b / c


def create_igmp(src_mac, src_ip, group_ip, igmp_type=IGMP_QUERY):
    """Creates a new IGMP packet based on the given addresses."""
    a = Ether(src=src_mac)
    b = IP(src=src_ip)
    c = IGMP(type=igmp_type, gaddr=group_ip)
    c.igmpize(b, a)
    return a / b / c


class JamPacketApp(gtk.Window):

    def __init__(self):
        super(JamPacketApp, self).__init__()

        self.iface = None
        self.protocol = None
        self.source = None
        self.target = None

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
        cb_proto.append_text(PROTO_ARP)
        cb_proto.append_text(PROTO_ICMP_PING)
        cb_proto.append_text(PROTO_IGMP_QUERY)
        cb_proto.append_text(PROTO_IGMP_JOIN)
        cb_proto.append_text(PROTO_IGMP_LEAVE)

        self.lbl_ip = gtk.Label("Target IP")
        self.lbl_ip.set_size_request(90, -1)

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
        table.attach(self.lbl_ip, 0, 1, 2, 3)
        table.attach(e_target, 1, 2, 2, 3)
        table.attach(btn_send, 0, 2, 3, 4)

        self.add(table)

        self.show_all()

    def iface_changed(self, widget):
        self.iface = widget.get_active_text().split(' ')[0]
        self.source = widget.get_active_text().split(' ')[2]

    def protocol_changed(self, widget):
        self.protocol = widget.get_active_text()
        if self.protocol == IGMP_QUERY or self.protocol == IGMP_JOIN or self.protocol == IGMP_LEAVE:
            self.lbl_ip.set_text('Multicast IP')
        else:
            self.lbl_ip.set_text('Target IP')

    def target_changed(self, widget, event):
        self.target = widget.get_text()
        if is_ip(widget.get_text()):
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('green'))
        else:
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('red'))

    def popup(self, message_type, message):
        md = gtk.MessageDialog(self,
                               gtk.DIALOG_DESTROY_WITH_PARENT,
                               message_type,
                               gtk.BUTTONS_CLOSE,
                               message)
        md.run()
        md.destroy()

    def send(self, widget):
        if not self.iface:
            self.popup(gtk.MESSAGE_WARNING, 'You must select a network interface to send from!')
            return False
        if not self.protocol:
            self.popup(gtk.MESSAGE_WARNING, 'You must select a packet protocol!')
            return False
        if not self.target:
            self.popup(gtk.MESSAGE_WARNING,
                       'You must enter a {} address!'.format(self.lbl_ip.get_text()))
            return False
        if not is_ip(self.target):
            self.popup(gtk.MESSAGE_WARNING, '{} is not a valid IP address!'.format(self.target))
            return False

        src_mac = ni.ifaddresses(self.iface)[ni.AF_LINK][0]['addr']
        src_ip  = ni.ifaddresses(self.iface)[ni.AF_INET][0]['addr']
        dst_ip  = self.target

        try:
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
            sock.bind((self.iface, 0))
        except:
            self.popup(gtk.MESSAGE_ERROR,
                       'Could not open raw socket for transmission!\n' +
                       'Are you running this with root privileges?')
            return False

        if self.protocol == PROTO_ARP:
            try:
                sock.sendall(str(create_arp(src_mac, src_ip, dst_ip)))
            except Exception, e:
                self.popup(gtk.MESSAGE_ERROR, 'Unable to send packet: {}'.format(e.message))
                return False
            return True

        if self.protocol == PROTO_ICMP_PING:
            try:
                sock.sendall(str(create_icmp(src_mac, src_ip, dst_ip)))
            except:
                self.popup(gtk.MESSAGE_ERROR, 'Unable to send packet: {}'.format(e.message))
                return False
            return True

        if self.protocol == PROTO_IGMP_QUERY:
            try:
                sock.sendall(str(create_igmp(src_mac, src_ip, dst_ip, igmp_type=IGMP_QUERY)))
            except:
                self.popup(gtk.MESSAGE_ERROR, 'Unable to send packet: {}'.format(e.message))
                return False
            return True

        if self.protocol == PROTO_IGMP_JOIN:
            try:
                sock.sendall(str(create_igmp(src_mac, src_ip, dst_ip, igmp_type=IGMP_JOIN)))
            except:
                self.popup(gtk.MESSAGE_ERROR, 'Unable to send packet: {}'.format(e.message))
                return False
            return True

        if self.protocol == PROTO_IGMP_LEAVE:
            try:
                sock.sendall(str(create_igmp(src_mac, src_ip, dst_ip, igmp_type=IGMP_LEAVE)))
            except:
                self.popup(gtk.MESSAGE_ERROR, 'Unable to send packet: {}'.format(e.message))
                return False
            return True

JamPacketApp()
gtk.main()
