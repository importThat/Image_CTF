# I reccommend the Image class from the Python Image Library for loading images
from PIL import Image

# Images can be read in like this
image1 = Image.open("cat2.jpg")
image2 = Image.open("EncodedImage.png")

# A image is made from some number of pixels each with an R,G,B and sometimes A value
# R = Red, G = Green, B = Blue, A = Alpha (transparency)

# A transparency channel can be added to an image using the putalpha() method
image1.putalpha(255)    # adds a transparency channel to an image and sets it to 255

# Image objects can be cast directly to numpy arrays so that their R,G,B,A values can be examined
import numpy as np

image1_array = np.array(image1)
image2_array = np.array(image2)

# Numpy arrays are fancy n-dimensional tables. The size of an array can be seen by using array.size
image1_array.size

# My image1_array is size (1172, 1920, 3), which corresponds to a picture that is 1172 pixels high, 1920 pixels wide,
# and each pixel has three values [R, G, B]. So it is a table 1172 high, 1920 wide, where each cell is a list of 3
# values

# The first pixels value can be accessed by:
image1_array[0, 0, :]

# The first row of pixels can be accessed by:
image1_array[0, :, :]

# More information on numpy array indexing can be found here: https://numpy.org/doc/stable/user/basics.indexing.html

# Mathematical operations are applied to an entire array
# To subtract [5, 5, 5, 5] from each of the elements in the array:
image1_array - 5

# Similarly, arrays can be added or subtracted to other arrays of the same shape
ones = np.ones_like(image1_array)       # Create an array of ones in the same shape as the image1 array
ones = ones * 50    # multiply each value in the array by 50
image1_array - ones     # Subtract every element in the image1_array by 50

# Arrays can also be tested, here we're testing to see whether every element in
# the array is greater than 20
image1_array > 20

# This returns a boolean mask which can then be applied to the array to get all True values
mask = image1_array > 20
image1_array[mask]

# You will notice that this flattens the array down to 1 dimension. np.any() and np.all() functions can instead be
# used to retain the dimensionality of the data
any_mask = np.any(image1_array > 100, axis=2)       # Returns a boolean mask showing where any RGBA value is > 100
all_mask = np.any(image1_array > 100, axis=2)       # Returns a boolean mask showing where any RGBA value is > 100







