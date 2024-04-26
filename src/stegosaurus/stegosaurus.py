import numpy as np
from PIL import Image
from Crypto.Cipher import AES
import random

from utils import log, generate_aes_key


def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1


def encode(key: bytes, img: str, message: bytes, name: str) -> None:
    """
    Description
    -----------
    Encode a message into an image.

    Parameters
    ----------
    key : bytes
        The AES key.
    img : str
        The path to the image.
    message : bytes
        The message to encode.
    name : str
        The name of the output image.

    Returns
    -------
    None
    """

    # Getting image's [R, G, B] values
    cover = Image.open(img, "r")
    width, height = cover.size
    color_array = np.array(list(cover.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4

    # Convert message to binary
    # message += b"$3cur17y"  # Delimeter so we can find the end of the message
    message = [str(access_bit(message, i)) for i in range(len(message) * 8)]
    message_binary = "".join(message)
    total_pixels = len(message_binary)      # Number of pixels needed to encode our message
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")
    pixels_amount = len(color_array)        # Number of pixels in the image
    
    """
    Randomly getting the indexes to change using the key using:

        1. Seed the random number generator to the AES key
        2. Randomly select indexes to change
            a. If index is already in the list, skip it
        3. Change the LSB of the RGB values of the selected indexes
    """
    random.seed(key)

    if total_pixels > pixels_amount:    # Check if image is big enough to store message data
        print("Image is too small to encode")
    else:
        indexes_to_change = []
        while len(indexes_to_change) < total_pixels:    # Generate order of pixels to edit
            try_index: int = random.randint(0, pixels_amount - 1)
            if try_index not in indexes_to_change:
                indexes_to_change.append(try_index)

        log.debug("Indexes to change: %s", indexes_to_change)
        i = 0  # Index counter for message
        for pix in indexes_to_change:
            for rgb in range(0, n):     # Bit of R, G, and B
                if i < total_pixels:    # For every bit in our message
                    # log.debug("before: %s", color_array[pix][rgb])
                    # Change bits accordingly to hide message
                    if (
                        bin(color_array[pix][rgb])[-1] == "1"
                        and message_binary[i] == "0"
                    ):
                        color_array[pix][rgb] = color_array[pix][rgb] - 1
                    elif (
                        bin(color_array[pix][rgb])[-1] == "0"
                        and message_binary[i] == "1"
                    ):
                        color_array[pix][rgb] = color_array[pix][rgb] + 1
                    # log.debug("after: %s", color_array[pix][rgb])
                    i += 1

        color_array = color_array.reshape(height, width, n)
        encoded_img = Image.fromarray(color_array.astype("uint8"), cover.mode)
        encoded_img.save(f"{name}")
        print("End: Stego Object Image Created\n")
        return i


def decode(stegoimg, key, total_pixels):
    # Getting image's [R, G, B] values
    stego = Image.open(stegoimg, "r")
    color_array = np.array(list(stego.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4
    pixels_amount = len(color_array)    # Number of pixels in the image
    
    random.seed(key)    # Set seed using key - will give same index order as before!

    indexes_to_change = []
    while len(indexes_to_change) < total_pixels:    # Generate order of pixels to edit
        try_index: int = random.randint(0, pixels_amount - 1)
        if try_index not in indexes_to_change:
            indexes_to_change.append(try_index)
    log.debug("Indexes to change: %s", indexes_to_change)
    
    # Retrieve message bits
    retrieve_bits = ""
    pixels_amount = len(color_array)
    for pix in range(pixels_amount):
        for rgb in range(n):  # Bit of R, G, and B
            retrieve_bits += bin(color_array[pix][rgb])[-1]
    print("DECRYPT - BinaryStream:", retrieve_bits)
    return retrieve_bits


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
    # User input
    print("Info: cover can be .jpg/.png etc, out file is in .png")
    print("Enter Input: <cover> <data file.txt> <out_name.png> <key_file [Optional]>")
    # 10x10.jpg data.txt test.png

    # AES Encryption
    list_input: list[str] = input().split()
    cover, data, out_name = list_input[0], list_input[1], list_input[2]
    f = open(data, "r")
    text = f.read()
    f.close()
    data_bytes = str.encode(text)

    # If key provided, use it. Otherwise, make one.
    key: bytes = b""
    if len(list_input) > 3:
        key = open(list_input[3], "rb").read()
    else:
        key: bytes = generate_aes_key()
    # Save key for use later
        # In practice, users would write this down or save it in some other secure manner
    save_key = open("key.bin", "wb")
    save_key.write(key)
    cipher, nonce, tag = AES_encrypt(data_bytes, key)   # Encrypt plaintext with AES

    print(f"Original Text: {text}")
    print(f"Original Ciphertext: {cipher}")

    # Encode ciphertext into stego cover image
    L = encode(key, cover, cipher, out_name)
    
    print("Do you want to decode? Yes or No")
    decoding = input()
    if decoding == "Yes":
        # deciphering given image
        print("Info: give stego object and output txt")
        print("Enter Input: <stego_object.png>")
        stego = input()
        original = decode(stego, key, L)
        print(f"original: {original}")
        bytetext = str.encode(original) # This is wrong - need to properly change this back to bytes
        
        plaintext = AES_decrypt(bytetext, key, nonce, tag)
        print(f"DECRYPTED PLAINTEXT: {plaintext}")
    else:
        pass


if __name__ == "__main__":
    main()
