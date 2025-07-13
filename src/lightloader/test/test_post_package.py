
import sys
sys.path.append('/home/chenpengyu/workspace/master_light4faas_pycg')

import unittest
from lazy_load import transform_code

class TestImportTransformer(unittest.TestCase):

    def setUp(self):
        # Ensure each test starts with a fresh state
        self.transform_code = transform_code

    def test_simple_import(self):
        source_code = """
import numpy as np

def create_numpy_array():
    array = np.array([1, 2, 3, 4, 5])
    return array
"""
        expected_output = """
def create_numpy_array():
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    return array
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_import_from(self):
        source_code = """
from PIL import Image
from io import BytesIO

def fetch_image_from_url(url):
    image = Image.open(BytesIO(url))
    return image
"""
        expected_output = """
def fetch_image_from_url(url):
    from PIL import Image
    from io import BytesIO
    image = Image.open(BytesIO(url))
    return image
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_nested_import_usage(self):
        source_code = """
import requests
from PIL import Image
from io import BytesIO

def fetch_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image
"""
        expected_output = """
def fetch_image_from_url(url):
    import requests
    response = requests.get(url)
    from PIL import Image
    from io import BytesIO
    image = Image.open(BytesIO(response.content))
    return image
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())
    
    def test_class_import(self):
        source_code = """
import numpy as np
import requests
from PIL import Image
from io import BytesIO
class Actor:
    print(np.array([2, 3, 4]))
    
    def __init__(self):
        self.name = 'Ben'
        self.image = Image.open('root/hello.jpg')
    def create_numpy_array(self):
        array = np.array([1, 2, 3, 4, 5])
        return array
"""
        expected_output = """
class Actor:
    import numpy as np
    print(np.array([2, 3, 4]))

    def __init__(self):
        self.name = 'Ben'
        from PIL import Image
        self.image = Image.open('root/hello.jpg')

    def create_numpy_array(self):
        import numpy as np
        array = np.array([1, 2, 3, 4, 5])
        return array
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())
    
    def test_only_remove_top_import(self):
        source_code = """
from PIL import Image
if a > 2:
    import numpy
    img = Image.open('root/hello.jpg')
else:
    a = 4
"""
        expected_output = """
if a > 2:
    import numpy
    from PIL import Image
    img = Image.open('root/hello.jpg')
else:
    a = 4
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())
    
    def test_null_import(self):
        source_code = """
from PIL import Image
"""
        expected_output = """
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_relative_import(self):
        source_code = """
from .. import numpy
from ..util.PIL import Image
from . import (
    ExifTags,
    ImageMode,
    TiffTags,
    UnidentifiedImageError,
    __version__,
    _plugins,
)
def f1():
    a = numpy.Array([2, 3])
    if ExifTags.Base.Orientation not in self._exif:
        xmp_tags = self.info.get("XML:com.adobe.xmp")
        for i in range(3):
            image = Image.open('example.jpg')
        
"""
        expected_output = """
def f1():
    from .. import numpy
    a = numpy.Array([2, 3])
    from ..util.PIL import Image
    from . import ExifTags, ImageMode, TiffTags, UnidentifiedImageError, __version__, _plugins
    from . import ExifTags, ImageMode, TiffTags, UnidentifiedImageError, __version__, _plugins
    if ExifTags.Base.Orientation not in self._exif:
        xmp_tags = self.info.get('XML:com.adobe.xmp')
        from ..util.PIL import Image
        for i in range(3):
            from ..util.PIL import Image
            image = Image.open('example.jpg')
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_example(self):
        source_code = """
"""
        expected_output = """
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_top_level_import(self):
        source_code = """
import logging
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from . import ExifTags
def create_numpy_array():
    array = np.array([1, 2, 3, 4, 5])
    return array

def fetch_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image
logger = logging.getLogger(__name__)
"""
        expected_output = """
def create_numpy_array():
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    return array

def fetch_image_from_url(url):
    import requests
    response = requests.get(url)
    from PIL import Image
    from io import BytesIO
    image = Image.open(BytesIO(response.content))
    return image
import logging
logger = logging.getLogger(__name__)
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_special_import(self):
        source_code = """
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from __future__ import annotations
import importlib.metadata 
import typing
import logging
logger = logging.getLogger(__name__)

def create_numpy_array():
    array = np.array([1, 2, 3, 4, 5])
    return array
"""
        expected_output = """
from __future__ import annotations
import importlib.metadata
import typing
import logging
logger = logging.getLogger(__name__)

def create_numpy_array():
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    return array
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    # for top-level func
    def test_param_hint(self):
        source_code = """
import numpy as np
from PIL import Image
import logging
 
class Actor:
    print(np.array([2,3,4]))
    def __init__(self):
        self.name = 'Ben'
        self.image = Image.open('root/hello.jpg')

    def create_numpy_array(self):
        array = np.array([1, 2, 3, 4, 5])
        return array

def create_numpy_array():
    array = np.array([1, 2, 3, 4, 5])
    return array
logger = logging.getLogger(__name__)

def func_param_type(n: np.array, f: int) -> Image:
    print(n)
"""
        expected_output = """
from PIL import Image
import numpy as np

class Actor:
    import numpy as np
    print(np.array([2, 3, 4]))

    def __init__(self):
        self.name = 'Ben'
        from PIL import Image
        self.image = Image.open('root/hello.jpg')

    def create_numpy_array(self):
        import numpy as np
        array = np.array([1, 2, 3, 4, 5])
        return array

def create_numpy_array():
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    return array
import logging
logger = logging.getLogger(__name__)

def func_param_type(n: np.array, f: int) -> Image:
    print(n)
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_param_hint_multi_return(self):
        source_code = """
import numpy as np
from PIL import Image
from requests import Request
from typing import Tuple

def func_param_type(n: np.array, f: int) -> Image.Image:
    a = Request()
    print(n)

class Animal:
    def __init__(self):
        self.name = 'lion'
    def bark():
        print('wow')
    
def func_param_type2(n: np.array, f: int) -> Tuple[Image.Image, Animal, Request]:
    print(n)
"""
        expected_output = """
from requests import Request
from PIL import Image
import numpy as np
from typing import Tuple

def func_param_type(n: np.array, f: int) -> Image.Image:
    from requests import Request
    a = Request()
    print(n)

class Animal:

    def __init__(self):
        self.name = 'lion'

    def bark():
        print('wow')

def func_param_type2(n: np.array, f: int) -> Tuple[Image.Image, Animal, Request]:
    print(n)
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_decorator(self):
        source_code = """
from abc import ABC, abstractmethod
class FieldABC(ABC):

    parent = None
    name = None
    root = None

    @abstractmethod
    def serialize(self, attr, obj, accessor=None):
        pass

    @abstractmethod
    def deserialize(self, value):
        pass

    @abstractmethod
    def _serialize(self, value, attr, obj, **kwargs):
        pass

    @abstractmethod
    def _deserialize(self, value, attr, data, **kwargs):
        pass

import functools

@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        expected_output = """
from abc import ABC, abstractmethod
import functools

class FieldABC(ABC):
    parent = None
    name = None
    root = None

    @abstractmethod
    def serialize(self, attr, obj, accessor=None):
        pass

    @abstractmethod
    def deserialize(self, value):
        pass

    @abstractmethod
    def _serialize(self, value, attr, obj, **kwargs):
        pass

    @abstractmethod
    def _deserialize(self, value, attr, data, **kwargs):
        pass

@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_class_inheritance(self):
        source_code = """
import enum
from numpy import array
class EIClass(enum.IntEnum):
    a = 2
    b = 3
class Array(array):
    d = 4
"""
        expected_output = """
from numpy import array
import enum

class EIClass(enum.IntEnum):
    a = 2
    b = 3

class Array(array):
    d = 4
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_param_default_impo(self):
        source_code = """
import numpy as np

def process_array(arr=np.array([1, 2, 3])):
    print("Array:", arr)
    print("Array type:", type(arr))
    print("Array shape:", arr.shape)

process_array()

process_array(np.array([4, 5, 6, 7]))
"""
        expected_output = """
import numpy as np

def process_array(arr=np.array([1, 2, 3])):
    print('Array:', arr)
    print('Array type:', type(arr))
    print('Array shape:', arr.shape)
process_array()
process_array(np.array([4, 5, 6, 7]))
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_top_if_condition(self):
        source_code = """
import sys

from .packages import six
if not six.PY2:
    class RequestModule(sys.modules[__name__].__class__):
        print('hello')
    sys.modules[__name__].__class__ = RequestModule
"""
        expected_output = """
from .packages import six
import sys
if not six.PY2:
    import sys

    class RequestModule(sys.modules[__name__].__class__):
        print('hello')
    import sys
    sys.modules[__name__].__class__ = RequestModule
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_else_import(self):
        source_code = """
import time
if sys.platform == 'win32':
    preferred_clock = time.perf_counter
else:
    preferred_clock = time.time
"""
        expected_output = """
if sys.platform == 'win32':
    import time
    preferred_clock = time.perf_counter
else:
    import time
    preferred_clock = time.time
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

    def test_hierachy_import(self):
        source_code = """
import os.path
import urllib3.connection
if not cert_loc or not os.path.exists(cert_loc):
    print('hello')
if 3 > 4:
    a = urllib3.connection.HTTPConnection()
"""
        expected_output = """
import os.path
if not cert_loc or not os.path.exists(cert_loc):
    print('hello')
if 3 > 4:
    import urllib3.connection
    a = urllib3.connection.HTTPConnection()
"""
        self.assertEqual(transform_code(source_code).strip(), expected_output.strip())

    def test_example(self):
        source_code = """
"""
        expected_output = """
"""
        self.assertEqual(transform_code(source_code).strip(), expected_output.strip())

    def test_full_module(self):
        source_code = """
import numpy as np
import requests
from PIL import Image
from io import BytesIO

class Actor:
    print(np.array([2,3,4]))
    def __init__(self):
        self.name = 'Ben'
        self.image = Image.open('root/hello.jpg')

    def create_numpy_array(self):
        array = np.array([1, 2, 3, 4, 5])
        return array

def create_numpy_array():
    array = np.array([1, 2, 3, 4, 5])
    return array

def fetch_image_from_url(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

def resize_image(image, size):
    resized_image = image.resize(size)
    return resized_image

if __name__ == "__main__":
    numpy_array = create_numpy_array()
    print("Numpy Array:", numpy_array)
    image_url = "https://example.com/path/to/image.jpg"
    image = fetch_image_from_url(image_url)
    image.show()
    resized_image = resize_image(image, (100, 100))
    resized_image.show()
"""
        expected_output = """
class Actor:
    import numpy as np
    print(np.array([2, 3, 4]))

    def __init__(self):
        self.name = 'Ben'
        from PIL import Image
        self.image = Image.open('root/hello.jpg')

    def create_numpy_array(self):
        import numpy as np
        array = np.array([1, 2, 3, 4, 5])
        return array

def create_numpy_array():
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    return array

def fetch_image_from_url(url):
    import requests
    response = requests.get(url)
    from PIL import Image
    from io import BytesIO
    image = Image.open(BytesIO(response.content))
    return image

def resize_image(image, size):
    resized_image = image.resize(size)
    return resized_image
if __name__ == '__main__':
    numpy_array = create_numpy_array()
    print('Numpy Array:', numpy_array)
    image_url = 'https://example.com/path/to/image.jpg'
    image = fetch_image_from_url(image_url)
    image.show()
    resized_image = resize_image(image, (100, 100))
    resized_image.show()
"""
        self.assertEqual(self.transform_code(source_code).strip(), expected_output.strip())

if __name__ == "__main__":
    unittest.main()