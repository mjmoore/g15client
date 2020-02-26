Spotify for Logitech G510 
=========================

Linux based client application for writing spotify dbus information to a Logitech G510 device.

#### Description

The g15daemon opens a local socket on port `15550`.
It accepts a `bytebuffer` which toggles pixels on or off. 

Spotify metadata is read from a Session DBus, which in turn is is loaded into a font, 
rendered in monochrome and then translated into the `bytebuffer`.


#### Requirements

 * [g15daemon](https://www.archlinux.org/packages/community/x86_64/g15daemon/)
 
If running a G510 series keyboard, see the following links on patching:
 * [Arch wiki](https://wiki.archlinux.org/index.php/Logitech_Gaming_Keyboards#G510_on_g15daemon)
 * [Forum post](https://bbs.archlinux.org/viewtopic.php?pid=1421825)
 
#### Setup

 * Ensure g15daemon is installed and running:
       
       $ sudo pacman -S g15daemon
       $ sudo g15daemon

 * Install python requirements
 
       $ pip install --requirement requirements.txt

#### Usage

 * Simply run the client:
 
       $ python ./g15client.py

