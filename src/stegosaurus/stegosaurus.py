import numpy as np
from PIL import Image
from Crypto.Cipher import AES
import random

from .utils import log, generate_aes_key


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

    message += b"$3cur17y"  # delimeter so we know where message ends
    # print(f"Message w/ delimiter: {message}")
    message = [str(access_bit(message, i)) for i in range(len(message) * 8)]
    message_binary = "".join(message)
    total_pixels = len(message_binary)
    print(f"Total Pixels: {total_pixels} \nBinary Stream: {message_binary}\n")

    pixels_amount = len(color_array)
    """
    Randomly getting the indexes to change using the key using:

        1. seed the random number generator to the AES key
        2. randomly select indexes to change
            a. if index is already in the list, skip it
        3. change the LSB of the RGB values of the selected indexes
    """
    random.seed(key)

    if total_pixels > pixels_amount:
        print("Image is too small to encode")
    else:
        indexes_to_change = []
        while len(indexes_to_change) < total_pixels:
            try_index: int = random.randint(0, pixels_amount)
            if try_index not in indexes_to_change:
                indexes_to_change.append(try_index)

        log.debug("Indexes to change: %s", indexes_to_change)
        i = 0  # Index counter for message
        for pix in indexes_to_change:
            for rgb in range(0, n):  # Bit of R, G, and B
                if i < total_pixels:  # As long as enough pixels
                    # print(bin(color_array[pix][rgb]), message_binary[i])
                    # print(f"Before: {color_array[pix][rgb]}")
                    log.debug("before: %s", color_array[pix][rgb])
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

                    log.debug("after: %s", color_array[pix][rgb])
                    # otherwise, keeping these values the same
                    # print(bin(color_array[pix][rgb]))
                    # print(f"After: {color_array[pix][rgb]}\n")
                    i += 1

        # print(color_array)
        color_array = color_array.reshape(height, width, n)
        encoded_img = Image.fromarray(color_array.astype("uint8"), cover.mode)
        encoded_img.save(f"{name}")
        print("End: Stego Object Image Created\n")
        # return i


def decode(stegoimg):
    # Getting image's [R, G, B] values
    stego = Image.open(stegoimg, "r")
    color_array = np.array(list(stego.getdata()))
    if len(color_array[0]) == 3:
        n = 3
    elif len(color_array[1]) == 4:
        n = 4

    # retrieve message bits
    retrieve_bits = ""
    pixels_amount = len(color_array)
    for pix in range(pixels_amount):
        for rgb in range(n):  # Bit of R, G, and B
            retrieve_bits += bin(color_array[pix][rgb])[-1]
    print("DECRYPT - BinaryStream:", retrieve_bits)

    delimiter = b"$3cur17y"
    delimiter_to_bits = bin(int.from_bytes(delimiter, byteorder="big"))[2:]
    print(f"Delimiter in Binary: {delimiter_to_bits}\n")
    temp = retrieve_bits.partition(delimiter_to_bits)
    print(temp)
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

    # creating stego object
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

    key: bytes = b""
    if list_input[3]:
        key = open(list_input[3], "rb").read()
    else:
        key: bytes = generate_aes_key()
    cipher, nonce, tag = AES_encrypt(data_bytes, key)

    print(f"Original Text: {text}")

    encode(key, cover, cipher, out_name)
    save_key = open("key.bin", "wb")
    save_key.write(key)

    print("Do you want to decode? Yes or No")
    decoding = input()
    if decoding == "Yes":
        # deciphering given image
        print("Info: give stego object and output txt")
        print("Enter Input: <stego_object.png>")
        stego = input()
        original = decode(stego)
        print(f"original: {original}")
        plaintext = AES_decrypt(original, key, nonce, tag)
        print(f"DECRYPTED PLAINTEXT: {plaintext}")
    else:
        pass
    # check
    # print("CIPHERTEXT: ", cipher)
    # pt = AES_decrypt(cipher, key, nonce, tag)
    # print("DECRYPTED PLAINTEXT ", pt)


if __name__ == "__main__":
    main()
