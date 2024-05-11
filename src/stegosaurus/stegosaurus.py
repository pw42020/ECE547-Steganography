import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
from Crypto.Cipher import AES
import random
import os
from .utils import log, generate_aes_key
import argparse


# ../images/dog.png stegosaurus/data.txt hello.png
def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1


def encode(key: bytes, img: str, message: bytes, name: str) -> int:
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
    int
        The number of pixels used to encode the message.
    """

    # Getting image's [R, G, B] values
    cover = Image.open(img, "r")
    width, height = cover.size
    color_array = np.array(list(cover.getdata()))
    if type(color_array[0]) == np.int64:
        return -1
    elif len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4

    # Convert message to binary
    message += b"$3cur17y"  # Delimeter so we can find the end of the message
    # change message into string of 1s and 9s
    message = "".join([format(byte, "08b") for byte in message])
    print(f"MESSAGE: {message}")
    message_binary = "".join(message)
    needed_pixels_to_encode = len(
        message_binary
    )  # Number of pixels needed to encode our message
    print(
        f"Total Pixels: {needed_pixels_to_encode} \nBinary Stream: {message_binary}\n"
    )
    pixels_in_cover = len(color_array)  # Number of pixels in the image

    """
    Randomly getting the indexes to change using the key using:

        1. Seed the random number generator to the AES key
        2. Randomly select indexes to change
            a. If index is already in the list, skip it
        3. Change the LSB of the RGB values of the selected indexes
    """
    random.seed(key)

    if (
        needed_pixels_to_encode > pixels_in_cover
    ):  # Check if image is big enough to store message data
        print(
            f"Image is too small to encode\nHave {needed_pixels_to_encode} pixels needed {pixels_in_cover} pixels"
        )
    else:
        indexes_to_change = []
        while (
            len(indexes_to_change) < needed_pixels_to_encode
        ):  # Generate order of pixels to edit
            try_index: int = random.randint(0, pixels_in_cover - 1)
            if try_index not in indexes_to_change:
                indexes_to_change.append(try_index)

        log.debug("Indexes to change: %s", indexes_to_change)
        i = 0  # Index counter for message
        for pix in indexes_to_change:
            if i < needed_pixels_to_encode:  # For every bit in our message
                # log.debug("before: %s", color_array[pix][rgb])
                # Change bits accordingly to hide message
                if bin(color_array[pix][n - 1])[-1] == "1" and message_binary[i] == "0":
                    color_array[pix][n - 1] = color_array[pix][n - 1] - 1
                elif (
                    bin(color_array[pix][n - 1])[-1] == "0" and message_binary[i] == "1"
                ):
                    color_array[pix][n - 1] = color_array[pix][n - 1] + 1
                # log.debug("after: %s", color_array[pix][rgb])
                i += 1

        color_array = color_array.reshape(height, width, n)
        encoded_img = Image.fromarray(color_array.astype("uint8"), cover.mode)
        encoded_img.save(name)
        print(f"saved to ${name}")
        print("End: Stego Object Image Created\n")
        return i


def decode(stegoimg: str, key: bytes, total_pixels: int) -> bytes:
    """
    Description
    -----------
    Decode a message from an image.

    Parameters
    ----------
    stegoimg : str
        The path to the stego image.
    key : bytes
        The AES key.
    total_pixels : int
        The number of pixels used to encode the message.

    Returns
    -------
    bytes
        The decoded message.
    """
    # Getting image's [R, G, B] values
    stego = Image.open(stegoimg, "r")
    color_array = np.array(list(stego.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4
    pixels_in_cover = len(color_array)  # Number of pixels in the image

    random.seed(key)  # Set seed using key - will give same index order as before!

    indexes_to_change = []
    # Generate order of pixels to edit for all pixels in image (cause we don't know length)
    for index in range(pixels_in_cover * n):
        try_index: int = random.randint(0, pixels_in_cover - 1)
        if try_index not in indexes_to_change:
            indexes_to_change.append(try_index)
    print("Indexes to change: %s", indexes_to_change)

    # Retrieve message bits
    retrieve_bits = ""
    pixels_in_cover = len(color_array)
    delimeter_binary = (
        "0010010000110011011000110111010101110010001100010011011101111001"
    )
    for index in indexes_to_change:
        # print(f"Bits: {retrieve_bits}")
        retrieve_bits += bin(color_array[index][n - 1])[-1]
        if retrieve_bits[-64:] == delimeter_binary:
            retrieve_bits = retrieve_bits[: len(retrieve_bits) - 64]
            break

    get_message = bytes(
        int(retrieve_bits[i : i + 8], 2) for i in range(0, len(retrieve_bits), 8)
    )
    return get_message


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
    cipher, nonce, tag = AES_encrypt(data_bytes, key)  # Encrypt plaintext with AES

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

        plaintext = AES_decrypt(original, key, nonce, tag)
        print(f"DECRYPTED PLAINTEXT: {plaintext.decode()}")
    else:
        pass


if __name__ == "__main__":
    main()
