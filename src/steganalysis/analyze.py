"""Analysis functions module for possible stego images.

Contains:
1. Enhanced LSB matching system for stego detection"""

import os
from typing import Optional, Final
from pathlib import Path

PATH_TO_IMAGES: Final[Path] = Path(__file__).parent.parent.parent / "images"

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

from .utils import log, StegoOrNot


def enhanced_lsb_matching(image: str) -> StegoOrNot:
    """
    Description
    -----------
    Enhanced LSB matching system for stego detection.

    Parameters
    ----------
    image : str
        The path to the image file.

    Notes
    -----
    Using Calibrated HCF COM Detector method from paper.
    Method is
    1. Downsample by factor of 2 in each dimension.
    2. They divide the summed pixel intensities by four and take the
        integer part to reach images with the same range of values as
        the originals.
    3. Compute histogram characteristic function (HCF) of the image.
    4. Compute the COM of the HCF.

    Returns
    -------
    StegoOrNot
        The type of image object.
    """
    log.debug("Enhanced LSB matching system for stego detection.")

    # open image
    img = Image.open(image)
    n: Optional[int] = None
    if len(img.getdata()[0]) == 3:
        n = 3
    elif len(img.getdata()[0]) == 4:
        n = 4

    log.debug("Image has %s channels.", n)
    log.debug("Exclusively checking last channel")

    # 1. Downsample by factor of 2 in each dimension
    img = img.resize((img.width // 2, img.height // 2))
    # 2. Divide the summed pixel intensities by four and take the integer part
    # to reach images with the same range of values as the originals
    # 3. Compute histogram characteristic function (HCF) of the image
    # compile histograms for all 16x16 blocks of the image

    # compile all values for last channel and plot them on a bar chart
    NEW_PATH: Final[Path] = PATH_TO_IMAGES / image.split("/")[-1].replace(".png", "")
    if not os.path.exists(NEW_PATH):
        os.mkdir(NEW_PATH)
    img_data = list(img.getdata())
    for i in range(len(img_data) // 64):
        images_sliced = img_data[i * 64 : (i + 1) * 64]
        last_channel = [i[n - 1] for i in images_sliced]
        plt.hist(last_channel, bins=256)
        # add axis and title labels
        plt.xlabel("Pixel Value")
        plt.ylabel("Frequency")
        plt.title(f"Histogram of Pixel Values in Last Channel for {image}")
        plt.savefig(f"{NEW_PATH}/histogram_{i}.png")

    # check if follows Gaussian distribution
    log.debug("Checking if last channel follows Gaussian distribution.")

    return StegoOrNot.NOT_STEGO


def ones_vs_zeros_matching(image: str) -> tuple[StegoOrNot, float]:
    """
    Description
    -----------
    Ones vs Zeros matching system for stego detection.

    Parameters
    ----------
    image : str
        The path to the image file.

    Returns
    -------
    tuple[StegoOrNot, float]
        The type of image object and the percent likelihood of 1 vs 0.
    """
    log.debug("Ones vs Zeros matching system for stego detection.")

    # open image
    img = Image.open(image)
    n: Optional[int] = None
    img_data = list(img.getdata())
    if type(img_data[0]) == int:
        n = 1
        last_channel = img_data
    elif len(img_data[0]) == 3:
        n = 3
        last_channel = [i[n - 1] for i in img_data]
    elif len(img_data[0]) == 4:
        n = 4
        last_channel = [i[n - 1] for i in img_data]

    # count number of 1s vs number of 0s for all last signifiacnt bits

    num_ones = sum([1 for i in last_channel if i % 2 == 1])
    num_zeros = sum([1 for i in last_channel if i % 2 == 0])

    log.debug("Number of 1s: %d, Number of 0s: %d", num_ones, num_zeros)
    log.debug(
        "Percent likelihood of 1 vs 0: %.5f",
        float(num_ones) / float(num_ones + num_zeros),
    )
    binomial = np.random.binomial(
        1, float(num_ones) / float(num_ones + num_zeros), num_ones + num_zeros
    )
    log.info(
        "Percent likelihood that the binomial is organic: %d",
        sum(binomial) / len(binomial),
    )

    return (StegoOrNot.NOT_STEGO, float(num_ones) / float(num_ones + num_zeros))
