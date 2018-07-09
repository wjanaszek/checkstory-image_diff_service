# import the necessary packages
from skimage.measure import compare_ssim
import imutils
import cv2
from PIL import Image


def resize_image(wanted_width, image):
    basewidth = wanted_width
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    return image.resize((basewidth, hsize), Image.ANTIALIAS)


def find_differences_between_images(original_image_name, modified_image_name, resize=False, boundingRectangles=False,
                                    lineThickness=5):

    # load the two input images
    imageA = cv2.imread(original_image_name)
    imageB = cv2.imread(modified_image_name)

    # convert the images to greyscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # denoise grayscale images
    grayA = cv2.fastNlMeansDenoising(grayA, 1, 10, 7, 21)
    grayB = cv2.fastNlMeansDenoising(grayB, 1, 10, 7, 21)

    # apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(1.0, (50, 50))
    grayA = clahe.apply(grayA)
    grayB = clahe.apply(grayB)

    # compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype('uint8')
    print('SSIM: {}'.format(score))

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    resultImage = cv2.imread(modified_image_name)

    # if boundingRectangles == True:
    print('bounding rectangles')
    for c in cnts:
        # compute the bounding box of the contour and then draw the bounding box on both input images to represent where the two images differ
        (x, y, w, h) = cv2.boundingRect(c)
        # @TODO get this values from user
        if w > 100 and h > 100:
            cv2.rectangle(resultImage, (x, y), (x + w, y + h), (0, 0, 255), lineThickness)

    cv2.imwrite('result.jpg', resultImage)
