import numpy as np
from PIL import Image
from Crypto.Cipher import AES
import os

def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1


def encode(img, message, name):
    # Getting image's [R, G, B] values
    cover = Image.open(img, "r")
    width, height = cover.size
    color_array = np.array(list(cover.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4

    # Translating message into binary
    # message += b'' # Delimiter
    print("\n", message)
    message = [str(access_bit(message, i)) for i in range(len(message)*8)]
    message_binary = "".join(message)
    total_pixels = len(message_binary)
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")

    # Modifying LSB values
    pixels_amount = len(color_array)
    if total_pixels > pixels_amount:
        print("Image is too small to encode")
    else:
        i = 0       # Index counter for message
        for pix in range(pixels_amount):
            for rgb in range(0, n):     # Bit of R, G, and B
                if i < total_pixels:    # As long as enough pixels
                    # print(bin(color_array[pix][rgb]), message_binary[i])
                    # print(f"Before: {color_array[pix][rgb]}")
                    if bin(color_array[pix][rgb])[-1] == "1" and message_binary[i] == "0":
                        color_array[pix][rgb] = color_array[pix][rgb] - 1
                    elif bin(color_array[pix][rgb])[-1] == "0" and message_binary[i] == "1":
                        color_array[pix][rgb] = color_array[pix][rgb] + 1
                    # print(bin(color_array[pix][rgb]))
                    # print(f"After: {color_array[pix][rgb]}\n")
                    i += 1
        print(color_array)
        color_array = color_array.reshape(height, width, n)
        encoded_img = Image.fromarray(color_array.astype("uint8"), cover.mode)
        encoded_img.save(f"{name}")
        print("Image encoded")
    return i

def decode(stegoimg, L):
    # Getting image's [R, G, B] values
    stego = Image.open(stegoimg, "r")
    width, height = stego.size
    color_array = np.array(list(stego.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4

    doesthiswork = ""
    # Modifying LSB values
    pixels_amount = len(color_array)
    i = 0       # Index counter for message
    for pix in range(pixels_amount):
        for rgb in range(n):     # Bit of R, G, and B
            if i < L:    # As long as enough pixels
                doesthiswork += bin(color_array[pix][rgb])[-1]
                i += 1
    print("BinaryStream2:", doesthiswork)
        
    # Translating message into binary
    """message = [str(access_bit(message, i)) for i in range(len(message)*8)]
    message_binary = "".join(message)
    # print(message_binary)
    total_pixels = len(message_binary)
    # image_rrg.png encoded.jpg
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")"""


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
    # AES Encryption
    data = b'this is a test'
    key = os.urandom(16)
    c, n, t = AES_encrypt(data, key)

    print("If RGB --> .jpg, If RGBA --> .png")
    print("input: <cover> <out_name.jpg or out_name.png>")
    # 10x10.jpg data encoded.jpg
    cover, name = input().split()
    L = encode(cover, c, name)
    decode("encrypted.png", L)
    #print("CIPHERTEXT: ", c)
    # pt = AES_decrypt(c, key, n, t)
    #print("DECRYPTED PLAINTEXT ", pt)

if __name__ == "__main__":
    main()
