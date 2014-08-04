# JamPacket

![Strawberry](https://github.com/daviesjamie/jampacket/raw/master/strawberry.png)

JamPacket is a small GUI tool that performs a simple task: sending packets.

When developing network applications, scripts and test suites, debugging can be
difficult as it is often hard to replicate the packets being sent/received.

JamPacket allows you to quickly and easily send out a packet of a specified
protocol/type to a custom IP address, allowing you to view the packet and any
responses in any of the existing network capture tools (such as
[WireShark](http://www.wireshark.org/)).

The following protocols/types are currently supported:
 - ARP Requests
 - ICMP Echo Requests (Pings)
 - IGMP Membership Query
 - IGMPv2 Membership Report
 - IGMPv2 Leave Group


## Usage

JamPacket requires a couple of python packages to be installed in order to run;
these can be found in `requirements.txt` and installed with:

```
pip install -r requirements.txt
```

As JamPacket is a GUI tool written with the GTK toolkit, it is also necessary
that you have the GTK runtime and Python GTK bindings (`pygtk`) installed.

## Credits

Logo/Icon from the [IconArchive](http://www.iconarchive.com/show/food-icons-by-martin-berube/strawberry-icon.html).
