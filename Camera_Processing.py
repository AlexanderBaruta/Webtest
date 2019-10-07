# Copyright 2019, Alexander Baruta
# check_length code Copyright 2018,
# Petr Zemek: https://blog.petrzemek.net/2018/04/22/on-incomplete-http-reads-and-the-requests-library-in-python/


# In python the structure of the data to be parsed is

# { camera_id: 1, images:[ { file_size: data}, {} ... ] }

# Which corresponds to
# A dictionary containing:
# camera_id: int
# images: list of dictionaries, each containing:
# file_size: int

# Understanding this is important for how the data is parsed, as well as for adding metadata to the images in the future



import sys
import random
import requests
from requests.exceptions import Timeout


# Constant value for if the domain the controller is pointing to is live
DOMAIN_LIVE = False

# Constant Value for the domain
Domain_Controller = "domain.com/camera/"


def main():
    # This function takes in the following command line arguments:
    # [n]: The number of cameras in the system
    # [timeout]: the amount of time to wait on results from each individual camera in seconds
    # Further functionality may be added by providing a slice/list functionality to check a subset of cameras
    # This assumes that there exists a camera with id 0, and that the argument passed in for n...
    # ...is the number of cameras and is 1 greater than the maximum camera_id

    n = 15
    timeout = 5.7

    #If provided sets the values from the command line arguments
    if len(sys.argv) == 3:
        n = int(sys.argv[1])
        timeout = float(sys.argv[2])

    camera_list = []

    for x in range(n):
        print("Getting Camera: " + str(x))
        c = Camera(x)
        c.get_data(Domain_Controller, timeout)
        # This method discards the photo data so that it is not stored needlessly since we need the metadata only
        c.discard_photos()
        camera_list.append(c)

    # This is for the largest images from each camera
    large_images = []

    # This is for the camera with the most images
    most_images = []
    image_number = 0

    # This is for the camera with the largest total size
    largest_total_size = []
    large_size = 0

    for x in camera_list:
        if x.valid:
            size = x.get_total_size()
            if size >= large_size:
                if size > large_size:
                    large_size = size
                    largest_total_size = []
                    largest_total_size.append((x.id, size))
                else:
                    largest_total_size.append((x.id, size))

            image_num = x.get_number_images()
            if image_num >= image_number:
                if image_num > image_number:
                    image_number = image_num
                    most_images = []
                    most_images.append((x.id, image_num))
                else:
                    most_images.append((x.id, image_num))

            large_images.append(x.get_largest_images())

    print("The camera(s) with the largest total storage size is:")
    print(largest_total_size)

    print("The camera(s) with the largest number of images is:")
    print(most_images)

    print("The largest images per camera are:")
    for x in large_images:
        print(  x)




class Camera:
    data = []
    id = int()
    valid = bool()

    def __init__(self, id):
        self.id = id

    def check_length(self, response):
        # Check that we have read all the data as the requests library does not
        # currently enforce this.
        expected_length = response.headers.get('Content-Length')
        if expected_length is not None:
            actual_length = response.raw.tell()
            expected_length = int(expected_length)
            if actual_length < expected_length:
                raise IOError(
                    'incomplete read ({} bytes read, {} more expected)'.format(
                        actual_length,
                        expected_length - actual_length
                    )
                )

    def get_data(self, location, time):
        # Status Message to return
        message = str()

        if DOMAIN_LIVE:
            try:
                resp = requests.get(str(location + str(id) + '/'), timeout=time, enforce_content_length=True)

                # This will check to ensure we have the entire document
                self.check_length(resp)

                if not resp:
                    # If there is a problem with the request this will handle it
                    message = "Request unsuccessful: status code = " + str(resp.status_code)
                else:
                    try:
                        self.data = resp.json()
                        self.parse_data()
                        self.valid = True
                    except ValueError as err:
                        message = err.args

            # Error handlers
            except Timeout:
                message = "Timeout exceeded"

            except IOError as err:
                message = err.value

            finally:
                self.valid = False
                return message

        else:
            self.generate_data_random()
            self.parse_data()
            self.valid = True
            return "Generated Data"

    # This is a method to generate data that exactly matches the specification
    # For what the program is expected to parse
    def generate_data_random(self):
        # Make a dictionary
        local = {}
        local.update({'camera_id' : self.id})
        photolist = []

        # Use a fairly large range for testing purposes
        # Between 0 and 1 million
        r = random.randint(0, 1000000)
        for x in range(0, r):
            photolist.append( {'file_size' : random.randint(1024, 2097152)})

        local.update({'images' : photolist})
        self.data = local

    # This is a method to generate a specific number of picture data sets
    def generate_data(self, x):
        # Make a dictionary
        local = {}
        local.update({'camera_id': self.id})
        photolist = []

        if int(x) < 0:
                raise ValueError('Value must not be negative')

        for p in range(0, int(x)):
            photolist.append({'file_size': random.randint(1024, 2097152)})

        local.update({'images': photolist})
        self.data = local

    def display_data(self):
        print(self.data.get('images'))

    def parse_data(self):
        # The function for parsing the camera data
        aggregate = 0
        number_images = 0
        largest = 0
        large_list = []

        for x in self.data.get('images'):
            im = int(x.get('file_size'))
            aggregate += im
            number_images += 1

            if im >= largest:
                if im == largest:
                    large_list.append((number_images, im))
                else:
                    large_list = []
                    large_list.append((number_images, im))

        self.data.update({'total_size' : aggregate, 'number_images' : number_images, 'largest_images' : large_list})

    def discard_photos(self):
        self.data.update({'images' : []})

    def get_total_size(self):
        return self.data.get('total_size')

    def get_number_images(self):
        return self.data.get('number_images')

    def get_largest_images(self):
        return ("Camera Number: " + str(self.id), self.data.get('largest_images'))
main()













