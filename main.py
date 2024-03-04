from math import floor
from Modulator_RGBA import Modulator
from MapCreator import *
from PIL import Image
from functools import reduce

"""
Reads in an image from file and modulates that image by writing in a message into 
the RGBA colour values of the image.
"""

# Create the modulating map
# The amount which we will modulate the pixels by.
# The total number of symbols we can encode into this width is them all multiplied by each other
CHANNEL_WIDTH = [200, 100, 100, 100]
IMAGE = 'time_travel_image.jpg'
MESSAGE = "longer_message.txt"
SYMBOL_LENGTH = 8      # int or None. Specify how long the symbols are, will use the maximum possible if unspecified
                        # or invalid
np.random.seed(1337)    # Set the seed


# Multiplies them all together
max_space = reduce(lambda x, y: x * y, CHANNEL_WIDTH)

# Given the max symbol space allowed by our channel width, this is the longest our symbols can be
symbol_length = floor(log2(max_space))
symbol_length = min(symbol_length, SYMBOL_LENGTH)


# Create the modulating map
print("Creating the modulating map")
modulating_map = create_rgba_map(n=2**symbol_length,
                                 channel_width=CHANNEL_WIDTH,
                                 mode="safe")     # mode = 'safe' or 'sneaky'. sneaky can take a while for large
                                                    # channel widths

# Create the modulator. This object handles reading in the text and converting it to RGBA values as per
# the modulating map.
print("Creating the modulator")
mod = Modulator(file=MESSAGE,
                symbol_len=symbol_length,
                rgba_map=modulating_map)

# Now we need to do some processing on the modulated message to get it to fit over the picture
# To do this we need to figure out the image size and then alter the modulated message size accordingly

print("Reading in Image")
image = Image.open(IMAGE)
image.putalpha(255)       # Adds an alpha channel to the image and sets it to 255
image = np.array(image)
image_shape = image.shape
n_pixels = int(image.size / 4)  # /4 because of RGBA. i.e just get the count of pixels
message_len = len(mod.message_modulated)

# If the message is longer than the number of pixels, trim it down
if message_len > n_pixels:
    mod.message_modulated = mod.message_modulated[0:n_pixels]

# Now lets randomly sample the pixels
chosen_pixels = np.random.choice(n_pixels, len(mod.message_modulated), replace=False)
# put them in ascending order
chosen_pixels.sort()

# Time to write message to pixels
# Flatten the image to essentially a list of pixel values
img_16 = image.astype(np.int16)
img_16 = img_16.reshape((-1, 4))

# Convert the message to an array, dtype = int 16 because we're going to do some stuff with masks
msg_16 = np.array(mod.message_modulated, dtype=np.int16)

# We want to change the pixel values of the image by the message values, however we don't want to push
# the pixel values over 255 because this causes them to wrap around to 0.
# So, instead we want to subtract the pixel values when it would otherwise push the sum over 255
# To do this we sum them up (as int16s) then create a mask that will swap our message to negative where appropriate

# Just sum up the randomly chosen pixels, we aren't changing the others
summed_image = img_16[chosen_pixels] + msg_16
mask = summed_image > 255       # Boolean mask, Trues are values where the summed image was > 255
mask = mask.astype(np.int8)     # Convert to integers, Falses are now 0s and Trues are 1s
mask = (mask * -2) + 1          # Multiply by -2, so trues are now -2 and Falses are 0, then add 1 so trues are -1
                                # and falses are 1

msg_16 = mask * msg_16          # Use the mask to make the appropriate spots negative

# Alter the image at the chosen pixels then cast back to uint8
img_16[chosen_pixels] = img_16[chosen_pixels] + msg_16
img_16 = img_16.astype(np.uint8)

# Reshape the image to the original shape
img_16 = img_16.reshape(image_shape)

# Convert to image and show and save
img_16 = Image.fromarray(img_16, "RGBA")
img_16.show()


img_16.save(f"EncodedImage.png")

# ******************************************************************************
# Code to show the changed pixels
# Find the changed pixels
mask = np.any(image != img_16, axis=2)

# Turn them white
image[mask] = [250, 255, 255, 255]

# Show the image
Image.fromarray(image).show()












