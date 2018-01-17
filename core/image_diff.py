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


def find_differences_between_images(original_image_name, modifed_image_name, resize=False, boundingRectangles=False, lineThickness=5):

    print('original image name = ' + original_image_name)
    if resize:
        # resize image A to smaller
        imgA = Image.open(original_image_name)
        imgA = resize_image(1920, imgA)
        imgA.save('original.jpg')
    
        # resize image B to smaller
        imgB = Image.open(modifed_image_name)
        imgB = resize_image(1920, imgB)
        imgB.save('modified.jpg')
    else:
        # do not resize images
        imgA = Image.open(original_image_name)
        imgA.save('original.jpg')
        
        imgB = Image.open(modifed_image_name)
        imgB.save('modified.jpg')
    
    # load the two input images
    imageA = cv2.imread('original.jpg')
    imageB = cv2.imread('modified.jpg')

    # denoise color images (take much time)
    # imageA = cv2.fastNlMeansDenoisingColored(imageA, 3, 10, 7, 21)
    # imageB = cv2.fastNlMeansDenoisingColored(imageB, 3, 10, 7, 21)

    # convert the images to greyscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # denoise grayscale images
    grayA = cv2.fastNlMeansDenoising(grayA, 1, 10, 7, 21)
    grayB = cv2.fastNlMeansDenoising(grayB, 1, 10, 7, 21)

    # apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(1.0, (50, 50))
    grayA = clahe.apply(grayA)
    # cv2.imwrite('test1.png', grayA)
    grayB = clahe.apply(grayB)
    # cv2.imwrite('test2.png', grayB)

    # denoise grayscale images
    # grayA = cv2.fastNlMeansDenoising(grayA, 3, 10, 7, 21)
    # grayB = cv2.fastNlMeansDenoising(grayB, 3, 10, 7, 21)

    # compute the Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype('uint8')
    print('SSIM: {}'.format(score))

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    resultImage = cv2.imread('modified.jpg')

    if not boundingRectangles:
        # draw final image (with differences between the two uploaded images (no rectangles)
        print('no reactangles')
        cv2.drawContours(resultImage, cnts, -1, (0, 0, 255), lineThickness)
        cv2.imwrite('result.png', resultImage)
    else:
        for c in cnts:
            # compute the bounding box of the contour and then draw the bounding box on both input images to represent where the two images differ
            (x, y, w, h) = cv2.boundingRect(c)
            # @TODO get this values from user
            if w > 100 and h > 100:
                cv2.rectangle(resultImage, (x, y), (x + w, y + h), (0, 0, 255), lineThickness)

        cv2.imwrite('result.png', resultImage)
