from unittest import TestCase
from Camera_Processing import Camera


class TestCamera(TestCase):

    def test_get_data(self):
        test = Camera(0)

    def test_generate_data(self):
        test = Camera(0)
        test.generate_data(-5)
        self.assertRaises(ValueError)

    def test_generate_data_random(self):
        test = Camera(0)
        test.generate_data_random()
        self.assertNotEqual(test.data.get('images'), [])

    def test_display_data(self):
        test = Camera(0)
        test.generate_data_random()
        self.assertIsNotNone(test.data.get('images'))

    def test_parse_data(self):
        test = Camera(0)
        test.generate_data(10)
        test.parse_data()
        self.assertEqual(test.data.get('number_images'), 10)

    def test_discard_photos(self):
        test = Camera(0)
        test.generate_data(4)
        test.discard_photos()
        self.assertEqual(test.data.get('images'), [])
