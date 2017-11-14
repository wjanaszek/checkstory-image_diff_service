from rest_framework.decorators import api_view
from rest_framework.response import Response
from core import image_diff


@api_view(['POST'])
def api_root(request, format=None):
    image_diff.find_difference_between_images()
    return Response('post request', 200, None, None, 'application/json')
