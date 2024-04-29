"""Analysis functions module for possible stego images.

Contains:
1. Enhanced LSB matching system for stego detection"""

from typing import Optional

from PIL import Image
import matplotlib.pyplot as plt

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

    # img = img.convert("L")

    # divide summed pixel intensities
    img = img.point(lambda i: i // 4)

    # 3. Compute histogram characteristic function (HCF) of the image

    # compile all values for last channel and plot them on a bar chart
    last_channel = [i[n - 1] for i in img.getdata()]
    plt.hist(last_channel, bins=256)
    # add axis and title labels
    plt.xlabel("Pixel Value")
    plt.ylabel("Frequency")
    plt.title(f"Histogram of Pixel Values in Last Channel for {image}")
    plt.show()

    # check if follows Gaussian distribution
    log.debug("Checking if last channel follows Gaussian distribution.")

    return StegoOrNot.NOT_STEGO
