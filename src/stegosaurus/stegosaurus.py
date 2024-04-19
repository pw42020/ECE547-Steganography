import numpy as np
from PIL import Image
from Crypto.Cipher import AES
import os

def encode(img, message, name):

    # Getting image's [R, G, B] values
    cover = Image.open(img, "r")
    width, height = cover.size
    color_array = np.array(list(cover.getdata()))
    # print(color_array)

    message += "end"    # Delimiter
    message_binary = "".join([format(ord(i), "b") for i in message])
    total_pixels = len(message_binary)
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")

    pixels_amount = len(color_array)
    if total_pixels > pixels_amount:
        print("Image is too small to encode")
    else:
        i = 0       # Index counter for message
        for pix in range(pixels_amount):
            for rgb in range(0, 3):     # Bit of R, G, and B
                if i < total_pixels:    # As long as enough pixels
                    print(bin(color_array[pix][rgb]), message_binary[i])
                    print(f"Before: {color_array[pix][rgb]}")
                    if bin(color_array[pix][rgb])[-1] == "1" and message_binary[i] == "0":
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


def AES_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    nonce = cipher.nonce
    return ciphertext, nonce, tag


def AES_decrypt(ciphertext, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data
    

def main():
    #print("input: <cover> <message> <out_name.jpg>")
    # 10x10.jpg data encoded.jpg
    #cover, message, name = input().split()

    #encode(cover, message, name)
    
    # AES Encryption
    data = b'this is a test.'
    key = os.urandom(16)
    c, n, t = AES_encrypt(data, key)
    #print("CIPHERTEXT: ", c)
    pt = AES_decrypt(c, key, n, t)
    #print("DECRYPTED PLAINTEXT ", pt)

if __name__ == "__main__":
    main()