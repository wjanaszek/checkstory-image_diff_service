# USAGE
# python deep_learning_object_detection.py --image images/example_01.jpg \
#	--prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
import numpy as np
import argparse
import cv2
from image import Image
from object import Object


class ImageService:
    MAX_DISTANCE = 250
    RED_COLOR = (0, 0, 255)
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-i1", "--image1", required=True, help="path to input image 1")
        ap.add_argument("-i2", "--image2", required=True, help="path to input image 2")
        ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
        ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
        ap.add_argument("-c", "--confidence", type=float, default=0.2,
                        help="minimum probability to filter weak detections")
        args = vars(ap.parse_args())
        self.net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        self.originalImagePath = args["image1"]
        self.modifiedImagePath = args["image2"]
        self.confidence = args["confidence"]

    def detect_and_compare_images(self):
        # read images
        originalImage = Image(self.originalImagePath)
        modifiedImage = Image(self.modifiedImagePath)
        # recognize and save objects from images
        self.recognize_objects(originalImage)
        self.recognize_objects(modifiedImage)
        # compare and save differences
        self.compare_images(originalImage, modifiedImage)
        self.save_image(originalImage, 'result1')
        self.save_image(modifiedImage, 'result2')

    def recognize_objects(self, image: Image):
        print("[INFO] computing object detections...")
        self.net.setInput(image.blob)
        detections = self.net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > self.confidence:
                # extract the index of the class label from the `detections`,
                # then compute the (x, y)-coordinates of the bounding box for
                # the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([image.w, image.h, image.w, image.h])
                (startX, startY, endX, endY) = box.astype("int")
                detectedObject = Object((startX, startY, endX, endY), self.CLASSES[idx], confidence)
                image.detectedObjects.append(detectedObject)

    def draw_matches(self, image: Image, box, confidence, idx):
        (startX, startY, endX, endY) = box
        # display the prediction
        label = "{}: {:.2f}%".format(self.CLASSES[idx], confidence * 100)
        print("[INFO] {}".format(label))
        cv2.rectangle(image.npArray, (startX, startY), (endX, endY),
                      self.COLORS[idx], 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(image.npArray, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)

    def draw_matches_by_detected_object(self, image: Image, detected: Object):
        (startX, startY, endX, endY) = detected.box
        # display the prediction
        label = "{}: {:.2f}%".format(detected.typeClass, detected.confidence * 100)
        # print("[INFO] {}".format(label))
        cv2.rectangle(image.npArray, (startX, startY), (endX, endY),
                      self.RED_COLOR, 7)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(image.npArray, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.RED_COLOR, 2)

    def save_image(self, image: Image, name):
        cv2.imwrite(name + '.jpg', image.npArray)

    def compare_images(self, original: Image, modified: Image):
        for detectedOriginal in original.detectedObjects:
            found = modified.find_detected(detectedOriginal, self.MAX_DISTANCE)
            if found is None:
                print(detectedOriginal.typeClass + ' not found')
                self.draw_matches_by_detected_object(original, detectedOriginal)
            else:
                detectedOriginal.matched = True
                print('matched ' + detectedOriginal.typeClass)
                if found.typeClass != detectedOriginal.typeClass:
                    print(found.typeClass + ' another class type ' + detectedOriginal.typeClass)
                    self.draw_matches_by_detected_object(original, detectedOriginal)
                else:
                    print('comparing the same class objects')
                # call method for comparing the same class objects

        for detectedModified in modified.detectedObjects:
            if detectedModified.matched is False:
                print('not matched object ' + detectedModified.typeClass)
                self.draw_matches_by_detected_object(original, detectedModified)

        #
        # for detectedOriginal in original.detectedObjects:
        #     if detectedOriginal.matched is False:
        #         print('2 not matched object ' + detectedOriginal.typeClass)
        #         self.draw_matches_by_detected_object(original, detectedOriginal)


# if __name__ == '__main__':
#     net = DeepLearningObjectDetection()
#     net.detect_and_compare_images()