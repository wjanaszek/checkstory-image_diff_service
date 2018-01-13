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


def find_differences_between_images(original_image_name, modifed_image_name, resize=False, boundingRectangles=True, lineThickness=2):

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

    # denoise color images
    imageA = cv2.fastNlMeansDenoisingColored(imageA, 10, 10, 7, 21)
    imageB = cv2.fastNlMeansDenoisingColored(imageB, 10, 10, 7, 21)

    # convert the images to greyscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute thr Structural Similarity Index (SSIM) between the two images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype('uint8')
    print('SSIM: {}'.format(score))

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    if not boundingRectangles:
        # draw final image (with differences between the two uploaded images (no rectangles)
        finalImage = cv2.imread('modified.jpg')
        cv2.drawContours(finalImage, cnts, -1, (0, 0, 255), lineThickness)
        cv2.imwrite('result.jpg', finalImage)
    else:
        for c in cnts:
            # compute the bounding box of the contour and then draw the bounding box on both input images to represent where the two images differ
            (x, y, w, h) = cv2.boundingRect(c)
            if w > 150 and h > 150:
                cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), lineThickness)

        cv2.imwrite('result.jpg', imageB)
