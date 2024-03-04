import numpy as np
from math import log2, ceil
from functools import reduce, partial


def convert_to_binary(decimal_integer, pad_length=None):
    """
     Converts a decimal integer to a binary in the form of a padded string, e.g. 10 = "001010"
    :param pad_length: The length the binary should be padded too
    """
    binary = bin(decimal_integer)
    # Drop the "0b" at the start
    binary = binary[2:]

    # Pad to length
    if len(binary) < pad_length:
        binary = "0" * (pad_length - len(binary)) + binary

    return binary


def split_to_RGBA(num, channel_width):
    """
    splits a number between 4 dimensions of the RGBA domain
    """
    # So think about this like buckets filling with water. The alpha channel fills first and
    # then flows onto the red channel. The red channel fills next and once it's full flows into
    # the green channel and so on. The only difference to this analogy is once a bucket fills it
    # then resets to zero.

    # The Modulus term leaves the incoming number untouched if it is below the channel width, or reduces it
    # to the overflow value if it's above the channel width. So if num = 6 and channel_width[3] = 4, this
    # would reduce to the overflow which is 2.
    alpha = num % channel_width[3]

    # The num // channel_width[3] term checks to see how many times the previous channel has
    # overflowed. This term is then modulus'd by the current channels width to see how much remainder there is
    r = num // channel_width[3] % channel_width[2]

    # Here the num // (channel_width[3] * channel_width[2]) term checks to see how many times the previous 2 channels
    # have overflowed
    g = num // (channel_width[3] * channel_width[2]) % channel_width[1]
    b = num // (channel_width[3] * channel_width[2] * channel_width[1]) % channel_width[0]

    return r, g, b, alpha


def create_rgba_map(n, channel_width=255, mode="sneaky"):
    """
    Splits the RGBA range (256*256*256*256) into n and returns a dict of {binary:colour}. Fills
    up one channel first before moving onto the next. Channel width determines the total value range
    allowable in any given channel. Can be a flat number or a list of values e.g [10, 20 ,10, 5].

    n: The total number of possible symbols (2 to the power of the symbol length, '101' = 2**3 = 8)
    channel_width: The width that can be written to in the colour channels
    mode: Whether to return colours that are next to each other (sneaky) or distant (safe)
    """
    if type(channel_width) == int:
        if channel_width < 0 or channel_width >= 256:
            raise ValueError(f"create_rgba_map xpected an int <= 255, got {channel_width}")

        width = [channel_width, channel_width, channel_width, channel_width]

    elif type(channel_width) == list and len(channel_width) != 4:
        raise TypeError(f"create_rgba_map xpected an int <= 255, or list of length 4, got {channel_width}")
    else:
        width = channel_width

    # ok so given a channel width and a number of samples, we need to encode those samples into the relevant channels

    sample_space = reduce(lambda x, y: x * y, width)    # Multiplies all the numbers in the width to get the total space
    if n > sample_space:    # If we're being asked for more symbols than there is room
        raise ValueError(f"Sample space is {sample_space} but Symbol Space is {n}. Symbols must be <= Samples")

    # separate our total sample space equally amongst the symbols # TO DO ENCODE SNEAKY MODE
    if mode == 'safe':
        space_between_vals = int(sample_space/n)     # **There's a possible overflow error here**
    else:
        space_between_vals = 1      # Fit the samples in the least possible room? needs testing

    # Create an iterator that will split up the sample space by the spaces between the vals
    rgba_vals = range(0, sample_space, space_between_vals)

    # Maps the split function to the values of the iterator above. the map_fun partial allows us to pass
    # the width variable into the map function
    map_fun = partial(split_to_RGBA, channel_width=width)
    rgba_vals = map(map_fun, rgba_vals)

    # Compute the mapping from above and put it into a numpy array. dtype = uint8 because we have values 0-255
    # This is now an array of size (n,4), where n is the number of symbols we want. looks like [[R, G, B, A], ...]
    rgba_vals = np.array([i for i in rgba_vals], dtype=np.uint8)

    # Now that we have the colour values we just have to figure out the binary values that map to those colours

    # Find the binary length, e.g 3 for 8 ('101' for 8 symbols)
    binary_length = ceil(log2(n))

    # Great np function that creates binary strings of a specific width. So here we're creating all the
    # binary strings from 0 to n and packing them into a list using a list comprehension
    binaries = [np.binary_repr(i, width=binary_length) for i in range(n)]

    # Finally, join the binaries and the colour values up to make the modulating map. The code below is
    # a dictionary comprehension which takes values from the zipped together binaries and rgba_vals
    modulating_map = {key: value.tolist() for (key, value) in zip(binaries, rgba_vals)}

    return modulating_map

