#!/bin/python
import socket
import time
from datetime import datetime
from enum import Enum

import dbus

from render.font import Font


class SpotifyClient(object):

    def __init__(self, props_interface):

        self.player_props = props_interface.GetAll("org.mpris.MediaPlayer2.Player")

        self.metadata = Metadata(self.player_props["Metadata"])
        self.playback_status = self.player_props["PlaybackStatus"]

    @classmethod
    def init(cls):

        bus_name = 'org.mpris.MediaPlayer2.spotify'
        object_path = '/org/mpris/MediaPlayer2'

        while True:
            try:
                proxy = dbus.SessionBus().get_object(bus_name, object_path)
                props_interface = dbus.Interface(proxy, dbus_interface='org.freedesktop.DBus.Properties')
                break
            except dbus.DBusException:
                time.sleep(0.5)

        return SpotifyClient(props_interface)

    def __repr__(self):
        return "Artist: %s\nAlbum: %s\nTitle: %s" % \
            (self.metadata.get_artist(), self.metadata.get_album(),
             self.metadata.get_title())


class Metadata(object):

    def __init__(self, metadata: dbus.Dictionary):
        self.metadata = metadata

    def get_artist(self):
        return self.metadata["xesam:artist"][0] if len(self.metadata["xesam:artist"]) else ""

    def get_title(self):
        return self.metadata["xesam:title"]

    def get_album(self):
        return self.metadata["xesam:album"]

    def get_length(self):
        return self.metadata["mrpis:length"]


class ScreenType(Enum):
    """ Init strings to be sent to the g15daemon to set display mode. """
    Pixel = b"GBUF"
    Text = b"TBUF"
    Bitmap = b"WBUF"


class Display(object):

    height = 43
    width = 160
    buffer_size = height * width


class G15(object):

    def __init__(self, host='127.0.0.1', port=15550):

        self.screen = bytearray(Display.buffer_size)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Attempt initial connection
        try:
            self.socket.connect((host, port))
        except Exception as e:
            print("Could not connect to G15 daemon at %s:%d" % (host, port))
            print("Cause: %s" % e)

        # Check response
        response = self.socket.recv(16)
        if response == b"G15 daemon HELLO":
            print("Received expected response from daemon.")
        else:
            raise Exception("Incorrect response received: %s", response)

        self.socket.send(ScreenType.Pixel.value)

        # Initialize empty character buffer for screen
        self.clear()

        font_path = "/usr/share/fonts/nerd-fonts-complete/ttf/Bitstream Vera Sans Mono Nerd Font Complete Mono.ttf"
        self.font = FontWrapper(font_path, 10)

    def clear(self):
        self.screen = bytearray(Display.buffer_size)
        self.display()

    def display(self):
        self.socket.send(self.screen)

    def write(self, strings):
        self.clear()

        if type(strings) is str:
            strings = [strings]

        for i, string in enumerate(strings):

            bitmap = self.font.from_string(string)
            y_offset = (self.font.vertical_padding * i) + (i * self.font.char_height)

            for y in range(bitmap.height):
                for x in range(bitmap.width):
                    index = G15.translate_coordinates(x, y_offset + y)
                    text_coords = x + (y * bitmap.width)
                    self.screen[index] = bitmap.pixels[text_coords]

        self.display()

    @staticmethod
    def translate_coordinates(x, y):
        """
        Translates a 2d coordinate pair (x, y) to an index for an array
        """

        if x < 0 or y < 0 or x >= Display.width \
                or y >= Display.height or x * y > Display.buffer_size:
            raise Exception("Invalid coordinates: %d, %d" % (x, y))

        return (y * Display.width) + x


class FontWrapper(object):

    def __init__(self, font_filepath, font_size):

        self.padding = "..."
        self.vertical_padding = 2
        self.font = Font(font_filepath, font_size)

        # Render an arbitrary character to calculate how many can fit in a screen
        char = self.font.render_text(".")
        self.char_width, self.char_height = char.width, font_size
        self.max_characters = Display.width // self.char_width

    def _truncate_string(self, string):
        return string[:self.max_characters - len(self.padding)] + self.padding

    def from_string(self, string):
        width, _, _ = self.font.text_dimensions(string)

        text = self._truncate_string(string) if width > Display.width else string
        return self.font.render_text(text)


def main():
    g15 = G15()

    info = (get_time_string(), "Waiting for Spotify")
    g15.write(info)

    last_hash = hash(info)

    while True:

        spotify_client = SpotifyClient.init()

        # Write to display only if content has changed
        info = (get_time_string(), spotify_client.metadata.get_artist(), spotify_client.metadata.get_title())
        if last_hash != hash(info):
            g15.write(info)
            last_hash = hash(info)

        time.sleep(1)


def get_time_string():
    return datetime.now().strftime("%Y-%m-%d | %H:%M | %a")


if __name__ == "__main__":
    main()
