from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import six
import imghdr
import cv2
# from image_processing_backend.models import Image


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data, file_name):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            # if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                # header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Get the file name extension:
            file_extension = self.get_file_extension(decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension)

            data = ContentFile(decoded_file, name=complete_file_name)

            cv2.imwrite('test.jpg', data)

            print('before data show')
            cv2.imshow("Original", data)
            cv2.waitKey(0)
            print('after data show')
        return

    def get_file_extension(self, decoded_file):
        extension = imghdr.what(decoded_file)
        return extension


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    image = Base64ImageField(max_length=None, use_url=None)

    class Meta:
        #model = Image
        fields = ('image')
