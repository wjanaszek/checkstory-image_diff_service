import base64

from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.image_service import ImageService
from image_processing_backend import utils


# USAGE: python3 manage.py runserver


@api_view(['POST'])
def api_root(request, format=None):
    # get first image from request
    first_image_data = base64.b64decode(request.data['first'] + '=' * (-len(request.data['first']) % 4))
    first_image_type = request.data['firstType']

    # get second image from request
    second_image_data = base64.b64decode(request.data['second'] + '=' * (-len(request.data['second']) % 4))
    second_image_type = request.data['secondType']

    sensitivity = request.data['sensitivity']

    image_service = ImageService(first_image_data, second_image_data, sensitivity)
    image_service.detect_and_compare_images()

    # read result image and send it as a response
    with open('result.jpg', 'rb') as f:
        result_image_data = f.read()
    base64encoded_result = base64.b64encode(result_image_data)

    # clear used resources
    utils.remove_created_files()

    return Response(base64encoded_result, 200, None, None, 'application/json')
