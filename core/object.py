class Object:
    def __init__(self, box, type_class, confidence):
        self.box = box
        self.xCenter = Object.calculate_center(box[0], box[1])
        self.yCenter = Object.calculate_center(box[2], box[3])
        self.typeClass = type_class
        self.confidence = confidence
        self.matched = False

    @staticmethod
    def calculate_center(start, end):
        return (start + end) / 2
