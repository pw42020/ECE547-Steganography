import numpy as np
from PIL import Image

def encode(img, message, name):

    # getting image's [R, G, B] values
    cover = Image.open(img, "r")
    width, height = cover.size
    color_array = np.array(list(cover.getdata()))
    # print(color_array)

    message += "end" # delimiter
    message_binary = "".join([format(ord(i), "b") for i in message])
    total_pixels = len(message_binary)
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")

    pixels_amount = len(color_array)
    if total_pixels > pixels_amount:
        print("Image is too small to encode")
    else:
        i = 0 # index counter for message
        for pix in range(pixels_amount):
            for rgb in range(0, 3): # bit of R, G, and B
                if i < total_pixels: # as long as enough pixels
                    print(bin(color_array[pix][rgb]), message_binary[i])
                    print(f"Before: {color_array[pix][rgb]}")
                    if bin(color_array[pix][rgb])[-1] == "1" and message_binary[i] == "1":
                        pass
                    elif bin(color_array[pix][rgb])[-1] == "0" and message_binary[i] == "0":
                        pass
                    elif bin(color_array[pix][rgb])[-1] == "1" and message_binary[i] == "0":
                        color_array[pix][rgb] = color_array[pix][rgb] - 1
                    elif bin(color_array[pix][rgb])[-1] == "0" and message_binary[i] == "1":
                        color_array[pix][rgb] = color_array[pix][rgb] + 1
                    print(bin(color_array[pix][rgb]))
                    print(f"After: {color_array[pix][rgb]}\n")
                    i += 1

        color_array = color_array.reshape(height, width, 3)
        encoded_img = Image.fromarray(color_array.astype("uint8"), cover.mode)
        encoded_img.save(f"{name}")
        print("Image encoded")

def main():
    print("input: <cover> <message> <out_name.jpg>")
    # 10x10.jpg data encoded.jpg
    cover, message, name = input().split()

    encode(cover, message, name)

if __name__ == "__main__":
    main()