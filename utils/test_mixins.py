import io

from PIL import Image
from rest_framework.test import APITestCase

from utils.mixins import ImageOptimizable


class ImageOptimizableTest(APITestCase):
    """
    Test to ImageOptimizable mixin
    """

    def setUp(self):
        self.image = Image.new('RGB', size=(500, 680))
        self.image_optimizable = ImageOptimizable()

    def test_crop_square(self):
        """
        Test the cropping
        """
        w, h = self.image.size
        image = self.image_optimizable.crop_square(image=self.image, width=w, height=h)
        self.assertEqual(image.size, (500, 500))

    def test_resize(self):
        """
        Test the resizing
        """

        image = self.image_optimizable.resize(image=self.image, size=200)
        self.assertEqual(image.size, (200, 200))
