import pickle


class Modulator:
    """
    Converts a message from text to binary using the ASCII encoding scheme, and then uses a binary:colour map
    to convert that message to a list of colours which can then be used to modulate an image.
    """
    def __init__(self, file='message.txt', symbol_len=3, rgba_map=None, rgba_map_file=None):
        self.rgba_map = None
        self.message_binary = None
        self.rgba_map = None
        self.rgba_map_file = rgba_map_file
        self.symbol_len = symbol_len
        self.num_symbols = 2**self.symbol_len

        # Compile the message into flat padded binary
        self.message_text = self.read_message(file)
        self.message_binary = self.message_to_bin()
        self.bin_flat = ''.join(self.message_binary)
        self.bin_pad = self.pad_message()

        # Load in the map
        if rgba_map:
            self.rgba_map = rgba_map
        else:
            self.load_map()

        # modulate the message
        self.message_modulated = self.modulate_message_rgba()

    def read_message(self, file):
        out = ''
        with open(file, mode='r', encoding='utf-8') as f:
            for line in f:
                out += line

            f.close()

        return out

    def load_map(self):
        """
        Reads in a symbol map object from file. Should be a pickle object
        """
        with open(self.rgba_map_file, 'rb') as f:
            self.rgba_map = pickle.load(f)

    def convert_to_binary(self, decimal_integer, pad_length=None):
        """
         Converts a decimal integer to a binary in the form of a padded string, e.g. 10 = "001010"
        :param pad_length: The length the binary should be padded too
        """
        if not pad_length:
            pad_length = self.symbol_len

        binary = bin(decimal_integer)
        # Drop the "0b" at the start
        binary = binary[2:]

        # Pad to length
        if len(binary) < pad_length:
            binary = "0" * (pad_length - len(binary)) + binary
        return binary

    def message_to_bin(self, length=8):
        """
        Converts text message to flat binary. Length=8 to keep it simple. This will drop any characters whose
        ascii number is greater than 256
        """
        out = []

        for char in self.message_text:
            dec = ord(char)
            binary = self.convert_to_binary(dec, length)
            if len(binary) == 8:
                out.append(binary)
            else:
                continue

        return out

    def pad_message(self):
        """
        If the message isn't nicely divisible by the symbol size then pad it out
        """
        out = self.bin_flat
        while len(out) % self.symbol_len != 0:
            out += '00111111'

        return out

    def modulate_message_rgba(self):
        """
        Maps the message from a flat binary string to a list of RGBA colour values
        """
        x = 0

        output = []

        while x < len(self.bin_pad):
            output.append(self.rgba_map[self.bin_pad[x:x + self.symbol_len]])

            x += self.symbol_len

        return output

    def demodulate_message(self, colours):
        """
        Takes in a list of colours values and a map dictionary. Turns the colours into the corresponding
        value stored in the dictionary
        """
        keys = [i for i in self.rgba_map.values()]
        vals = [i for i in self.rgba_map.keys()]

        output = ''

        for colour in colours:
            i = keys.index(colour)
            output += vals[i]

        return output




