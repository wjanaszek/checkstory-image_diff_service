from rest_framework.decorators import api_view
from rest_framework.response import Response
from core import image_diff

import base64


@api_view(['POST'])
def api_root(request, format=None):
    # get original image from request
    original_image_data = base64.b64decode(request.data['original'])
    original_image_type = request.data['originalType']

    # get modified image from request
    modified_image_data = base64.b64decode(request.data['modified'])
    modified_image_type = request.data['modifiedType']

    # write temporary both images on disc
    with open('original.' + original_image_type, 'wb') as f:
        f.write(original_image_data)

    with open('modified.' + modified_image_type, 'wb') as f:
        f.write(modified_image_data)

    image_diff.find_differences_between_images('original.' + original_image_type, 'modified.' + modified_image_type)

    result_image_data = base64.b64encode('result.jpg')

    return Response('post request', 200, None, None, 'application/json')
