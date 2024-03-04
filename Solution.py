import pickle
import random

from PIL import Image
import numpy as np
from collections import Counter
from random import shuffle


def apply_map(colours, demod_map, symbols=False):
    """
    given a dictionary of [colour] : "letter", attempts to translate from colour to letter and returns the results
    """
    out = ''
    for colour in colours:
        try:
            out += demod_map[tuple(colour)]

        except:
            if not symbols:
                out += "😹"  # missing character symbol
            else:
                out += str(colour)
    return out

# Read in the images
enc_img = Image.open("EncodedImage.png")
orig_img = Image.open("time_travel_image.jpg")
# Add in an alpga channel to the original image. We should probably have that in already
orig_img.putalpha(255)
# Add in

# Convert to arrays
enc_img = np.array(enc_img, dtype=np.int16)
orig_img = np.array(orig_img, dtype=np.int16)


# Find the difference between the two
mask = np.any(enc_img != orig_img, axis=2)
diff = abs(enc_img[mask] - orig_img[mask])
diff = diff.tolist()


# Cool function to count up the occurrences of the colours. The map(tuple) bit is to convert
# the list to tuples.
diff_counted = Counter(map(tuple, diff))

# The most common colour is probably a space
# Lets make a test dictionary and try to just solve it by hand
test_dict = {(1, 0, 0, 7): " ",
             (2, 0, 0, 19): "e"}


apply_map(diff, test_dict, symbols=False)

# Looks kind of like text

# there's a 3 digit word ending in e, that's probably 'the'
test_dict = {(1, 0, 0, 7): " ",
             (2, 0, 0, 19): "e",
             (4, 0, 0, 4): "h"}
print(apply_map(diff, test_dict, symbols=False))

# Add in the 't'
test_dict = {(1, 0, 0, 7): " ",
             (2, 0, 0, 19): "e",
             (2, 0, 0, 22): "h",
             (3, 0, 0, 9): "t"}
print(apply_map(diff, test_dict, symbols=False))

# we have 'the'!


# I see a h😹😹 the first 😹 is ether a i or o  i guess
test_dict = {(1, 0, 0, 7): " ",
             (2, 0, 0, 19): "e",
             (2, 0, 0, 22): "h",
             (3, 0, 0, 9): "t",
             (2, 0, 0, 15): "a"}

print(apply_map(diff, test_dict, symbols=False))

# a looks right
# I see a ha😹 that's probably a d I guess
test_dict = {(1, 0, 0, 7): " ",
             (2, 0, 0, 19): "e",
             (2, 0, 0, 22): "h",
             (3, 0, 0, 9): "t",
             (2, 0, 0, 15): "a",
             (2, 0, 0, 28): "d"}

print(apply_map(diff, test_dict, symbols=False))

# And so on... But this is too much work! I didn't get into programming to work
# This is basically a substitution cipher - we have swapped letters for colours

# (Of course I know ahead of time that 1 colour = 1 letter, but that would always be my first guess anyway, and
# can be figured out pretty easily (just by swapping " " into the most common letter and looking at the result))

# Lets instead write a program to solve the cipher

# To do this, I would like to code up the algorithm described by Thomas Jakobsen in
# “A Fast Method for the Cryptanalysis of Substitution Ciphers”.
#
# https://www.researchgate.net/publication/266714630_A_fast_method_for_cryptanalysis_of_substitution_ciphers

# The algorithm goes like this:
# 1. Construct an initial guess of the key
# 2. Use this key to decrypt the message and calculate how much close the decrypted text is to english
#    Jacobsen uses a digram (two-letter) frequency table to do this.

# 3. Swap of the elements in the key
# 4. Again calculate how close the decrypted message is to english and if it's closer store the new key
# 5. Repeat from step 3 until the key hasn't changed for some number of cycles

# Jakobsen then does some smart stuff to speed it up, but let's just try this and see how it goes


def calc_fit(key, text, language_freqs):
    decrypted_message = apply_map(text, key)        # Returns a string
    decrypted_message = [decrypted_message[i:i+2] for i in range(len(decrypted_message))]   # Make it a list of bigrams

    # Count up occurrences of the bigrams then cast it to an array
    char_count = np.array(Counter(decrypted_message).most_common())

    counts = char_count[:, 1].astype(np.int16)
    total = counts.sum()
    counts = counts/total   # get the frequency of each letter

    # Replace the counts with the frequencies
    char_count[:, 1] = counts

    # Sum up the differences between the two arrays
    # Find where they intersect
    _, lang_inds, msg_inds = np.intersect1d(language_freqs[:, 0], char_count[:, 0], return_indices=True)
    lang_freqs = language_freqs[lang_inds, 1].astype(np.float32)
    msg_freqs = char_count[msg_inds, 1].astype(np.float32)

    # Missing freqs
    missing_chars = np.setdiff1d(language_freqs[:, 0], char_count[:, 0])
    _, missing_inds, _ = np.intersect1d(language_freqs[:, 0], missing_chars, return_indices=True)
    missing_freqs = sum(language_freqs[missing_inds, 1].astype(np.float32))

    diff = abs(msg_freqs - lang_freqs)
    diff = diff.sum() + missing_freqs

    return diff


def make_key(alphabet, message, guesses=None):
    """
    Makes a random key based on some alphabet. Can take in some known guesses if any values are known already
    """
    # Construct a new key container from the initial guesses
    if guesses:
        key = guesses.copy()
    else:
        key = {}

    # Get the unique values in the message
    unique_colours = set(map(tuple, message))
    unique_colours = [i for i in unique_colours]       # swap back to a list

    # The alphabet is longer than the unique_colours list, which means that a few characters don't
    # occur in our message.
    # Lets just pad it out with random values I guess
    while len(unique_colours) < len(alphabet):
        random_colour = np.random.randint(0, 255, (4,))
        random_colour = random_colour.tolist()
        random_colour = tuple(random_colour)

        if random_colour not in unique_colours:
            unique_colours.append(random_colour)
        else:
            continue

    # Get the unique values which aren't in the initial guess
    alphabet = [i for i in alphabet if i not in key.values()]
    unique_colours = [i for i in unique_colours if i not in key.keys()]

    # Zip the key: values together and add them into the key container
    for colour, char in zip(unique_colours, alphabet):
        key[tuple(colour)] = char

    return key


def swap_values(key):
    """
    Given a dictionary, swaps two of the values at random
    """
    swap_one, swap_two = np.random.choice(len(key), 2, replace=False)

    keys_list = [i for i in key.keys()]

    key_one, key_two = keys_list[swap_one], keys_list[swap_two]
    val_one, val_two = key.pop(key_one), key.pop(key_two)

    key[key_one] = val_two
    key[key_two] = val_one


def randomness(stop_counter, max_count):
    # randomly returns a larger number as the stop counter gets bigger
    steps = max_count/4
    increment = stop_counter // steps

    low = 1 + increment
    end = 2 * (2 + increment)
    n = np.random.randint(int(low), int(end))

    return n


# I couldn't find any letter frequency lists online that included space, so I quickly figured out the frequencies
# from Mary Shelly's Frankenstein. They look pretty close to the ones online
with open("bigram_freqs.pkl", 'rb') as f:
    text_freqs = pickle.load(f)

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ !,." # think that's all
colours = diff      # the different pixels that we found before
guesses = {(1, 0, 0, 7): " ", (2, 0, 0, 19): "E"}


# 1. Construct an initial guess of the key
# 2. Use this key to decrypt the message and calculate how much close the decrypted text is to english
#    Jacobsen uses a digram (two-letter) frequency table to do this. I'm just going to try one letter

# 3. Swap of the elements in the key
# 4. Again calculate how close the decryted message is to english and if it's closer store the new key
# 5. Repeat from step 3 until the key hasn't changed for some number of cycles

# Make a key
key = make_key(alphabet, colours, guesses=guesses)
best_key = key.copy()


# Calculate the fitness
best_fitness = 1 - calc_fit(key, colours, text_freqs)

# Cycles to stop
stop_counter = 0
max_count = 5000


for i in range(40000):
    key = best_key.copy()

    # It's kind of getting stuck in local minima, so let's input some randomness to the swap values
    # function
    n = randomness(stop_counter, max_count)

    for j in range(n):
        swap_values(key)

    new_fitness = 1 - calc_fit(key, colours, text_freqs)

    if new_fitness > best_fitness:
        best_key = key.copy()
        best_fitness = new_fitness
        stop_counter = 0
        bad_swap_list = []

    else:
        stop_counter += 1

    if i % 500 == 0:
        print(f"Iteration: {i} New fitness: {new_fitness:.2f} Best fitness: {best_fitness:.2f}")

    if stop_counter >= max_count:
        break

print(apply_map(colours, best_key))

# Well that pretty much works! I'm calling that a win

