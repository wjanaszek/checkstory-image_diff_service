import math

import cv2

from core.object import Object


class Image:
    def __init__(self, path):
        self.npArray = cv2.imread(path)
        self.blob = cv2.dnn.blobFromImage(cv2.resize(self.npArray, (300, 300)), 0.007843, (300, 300), 127.5)
        self.detectedObjects = []
        self.h = self.npArray.shape[:2][0]
        self.w = self.npArray.shape[:2][1]

    def find_detected(self, object: Object, MAX_DISTANCE):
        print('searching for ' + object.typeClass)
        matched = []
        for detectedObject in self.detectedObjects:
            print('\tdistance from ' + detectedObject.typeClass + ' = ' + str(
                Image.calculate_distance_between_points(detectedObject.xCenter,
                                                        object.xCenter,
                                                        detectedObject.yCenter,
                                                        object.yCenter)))
            if Image.calculate_distance_between_points(detectedObject.xCenter,
                                                       object.xCenter,
                                                       detectedObject.yCenter,
                                                       object.yCenter) < MAX_DISTANCE or \
                    (abs(detectedObject.box[0] - object.box[0]) < MAX_DISTANCE
                     and abs(detectedObject.box[1] - object.box[1]) < MAX_DISTANCE
                     and abs(detectedObject.box[2] - object.box[2]) < MAX_DISTANCE
                     and abs(detectedObject.box[3] - object.box[3]) < MAX_DISTANCE):
                detectedObject.matched = True
                matched.append(detectedObject)

        for matchedObject in matched:
            print('\tmatched - ' + matchedObject.typeClass)
            if matchedObject.typeClass == object.typeClass:
                return matchedObject

        return None

    @staticmethod
    def calculate_distance_between_points(x2, x1, y2, y1):
        return math.hypot(x2 - x1, y2 - y1)
