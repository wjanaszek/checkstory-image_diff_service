# USAGE
# python deep_learning_object_detection.py --image images/example_01.jpg \
#	--prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

import cv2
# import the necessary packages
import numpy as np
import os

from core.image import Image
from core.object import Object


class ImageService:
    RED_COLOR = (0, 0, 255)
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    def __init__(self, first_image_path: str, second_image_path: str, max_distance: int, confidence=0.2):
        print(os.listdir())
        # read result image and send it as a response
        with open('MobileNetSSD_deploy.prototxt.txt', 'rb') as f:
            prototxt = f.read()

        with open('MobileNetSSD_deploy.caffemodel', 'rb') as f:
            model = f.read()

        self.net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')
        self.firstImagePath = first_image_path
        self.secondImagePath = second_image_path
        self.confidence = confidence
        self.MAX_DISTANCE = max_distance

    def detect_and_compare_images(self):
        # read images
        first_image = Image(self.firstImagePath)
        second_image = Image(self.secondImagePath)
        # recognize and save objects from images
        self.recognize_objects(first_image)
        self.recognize_objects(second_image)
        # compare and save differences
        self.compare_images(first_image, second_image)
        self.save_image(first_image, 'result', 'jpg')

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
                detected_object = Object((startX, startY, endX, endY), self.CLASSES[idx], confidence)
                image.detectedObjects.append(detected_object)

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

    def save_image(self, image: Image, name: str, extension: str):
        cv2.imwrite(name + '.' + extension, image.npArray)

    def compare_images(self, original: Image, modified: Image):
        for detectedOriginal in original.detectedObjects:
            found = modified.find_detected(detectedOriginal, self.MAX_DISTANCE)
            if found is None:
                self.draw_matches_by_detected_object(original, detectedOriginal)
            else:
                detectedOriginal.matched = True
                if found.typeClass != detectedOriginal.typeClass:
                    self.draw_matches_by_detected_object(original, detectedOriginal)

        for detectedModified in modified.detectedObjects:
            if detectedModified.matched is False:
                self.draw_matches_by_detected_object(original, detectedModified)
