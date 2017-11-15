from rest_framework.decorators import api_view
from rest_framework.response import Response
from core import image_diff

import base64


@api_view(['POST'])
def api_root(request, format=None):
    # get original image from request
    original_image_data = base64.b64decode(request.data['original'] + '=' * (-len(request.data['original']) % 4))
    original_image_type = request.data['originalImageType']

    # get modified image from request
    modified_image_data = base64.b64decode(request.data['modified'] + '=' * (-len(request.data['modified']) % 4))
    modified_image_type = request.data['modifiedImageType']

    # write temporary both images on disc
    with open('original.' + original_image_type, 'wb') as f:
        f.write(original_image_data)

    with open('modified.' + modified_image_type, 'wb') as f:
        f.write(modified_image_data)

    image_diff.find_differences_between_images('original.' + original_image_type, 'modified.' + modified_image_type)

    # read result image and send it as a response
    with open('result.jpg', 'rb') as f:
        result_image_data = f.read()
    base64encoded_result = base64.b64encode(result_image_data)

    return Response(base64encoded_result, 200, None, None, 'application/json')
