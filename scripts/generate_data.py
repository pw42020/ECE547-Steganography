"""generate data from all images and check how likely they are to be caught by the ones vs zeros matching system."""

import sys
import os
import csv
from typing import Final
from pathlib import Path

NUM_IMAGES_TO_CHECK: Final[int] = 100
PATH_TO_IMAGES: Final[Path] = Path(__file__).parent.parent / "images" / "cover"
PATH_TO_GENERATED_IMAGES: Final[Path] = (
    Path(__file__).parent.parent / "images" / "stego"
)
PATH_TO_STEGANALYSIS: Final[Path] = Path(__file__).parent.parent / "steganalysis"
PATH_TO_STEGOSAURUS: Final[Path] = Path(__file__).parent.parent / "stegosaurus"

DATA_50B: Final[Path] = Path(__file__).parent.parent / "assets" / "data_50B.txt"
DATA_500B: Final[Path] = Path(__file__).parent.parent / "assets" / "data_500B.txt"
DATA_3KB: Final[Path] = Path(__file__).parent.parent / "assets" / "data_3k.txt"

sys.path.append(str(PATH_TO_STEGANALYSIS))
sys.path.append(str(PATH_TO_STEGOSAURUS))


def main():
    from steganalysis.analyze import ones_vs_zeros_matching
    from stegosaurus.stegosaurus import encode, AES_encrypt
    from stegosaurus.utils import generate_aes_key

    STEGO_KEY: Final[bytes] = generate_aes_key()

    names = ["50B", "500B", "3KB"]

    if not os.path.exists(PATH_TO_GENERATED_IMAGES):
        os.mkdir(PATH_TO_GENERATED_IMAGES)

    continue_from_this_image = False
    with open("values.csv", "w") as file:
        writer = csv.writer(file)
        columns = ["Image", "Original", "50B", "500B", "3KB"]
        writer.writerow(columns)
        for image in os.listdir(PATH_TO_IMAGES)[:NUM_IMAGES_TO_CHECK]:
            if image.endswith(".JPEG"):
                stego_percent_likely: list[float] = []
                for i, path in enumerate([DATA_50B, DATA_500B, DATA_3KB]):
                    f = open(DATA_50B, "r")
                    text = f.read()
                    f.close()
                    data_bytes = str.encode(text)
                    cipher, nonce, tag = AES_encrypt(
                        data_bytes, STEGO_KEY
                    )  # Encrypt plaintext with AES
                    filename = str(
                        PATH_TO_GENERATED_IMAGES / f"stego_{names[i]}.{image}"
                    )
                    length = encode(
                        STEGO_KEY,
                        str(PATH_TO_IMAGES / image),
                        cipher,
                        filename,
                    )
                    if length == -1:
                        continue_from_this_image = True
                        break
                    stego_or_not, percent_likely = ones_vs_zeros_matching(filename)
                    stego_percent_likely.append(percent_likely)

                if continue_from_this_image:
                    continue_from_this_image = False
                    continue
                stego_or_not, percent_likely = ones_vs_zeros_matching(
                    str(PATH_TO_IMAGES / image)
                )
                writer.writerow(
                    [os.path.basename(image), percent_likely] + stego_percent_likely
                )


if __name__ == "__main__":
    main()
