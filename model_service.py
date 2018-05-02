import operator
import os
import numpy as np
from skimage import io, transform
import skimage

from caffe2.python import workspace

DATA_DIR = "./data"
CAFFE_MODELS = DATA_DIR + "/models"

LUT_TABLE = DATA_DIR + "/LookUpTable"
CLASS_GROUP_TABLE = DATA_DIR + "/ClassGroupTable"

MODEL = 'squeezenet', 'init_net.pb', 'predict_net.pb', 227


def get_percent(conf):
    return float("{0:.2f}".format(conf * 100))


def get_class(pred):
    return LUT_MAP[int(pred)]


def load_codes(codes_file):
    with open(codes_file) as f:
        res = f.readlines()
    codes = {}
    for line in res:
        key, value = line.partition(":")[::2]
        key = key.strip()
        value = value.replace("'", "")
        if key.isdigit():
            value = value.split(",")[0][1:]
            if value.isdigit():
                codes[int(key)] = int(value)
            else:
                codes[int(key)] = value
    return codes


def crop_center(img, cropx, cropy):
    y, x, c = img.shape
    startx = x // 2 - (cropx // 2)
    starty = y // 2 - (cropy // 2)
    return img[starty:starty + cropy, startx:startx + cropx]


def rescale(img, input_height, input_width):
    aspect = img.shape[1] / float(img.shape[0])
    if aspect > 1:
        res = int(aspect * input_height)
        img_scaled = transform.resize(img, (input_width, res))
    if aspect < 1:
        res = int(input_width / aspect)
        img_scaled = transform.resize(img, (res, input_height))
    if aspect == 1:
        img_scaled = transform.resize(img, (input_width, input_height))
    return img_scaled


def prepare_image(image, mean):
    if isinstance(image, str):
        prepared = skimage.img_as_float(io.imread(image)).astype(np.float32)
    else:
        prepared = image
    prepared = rescale(prepared, 227, 227)
    prepared = crop_center(prepared, 227, 227)
    prepared = prepared.swapaxes(1, 2).swapaxes(0, 1)
    prepared = prepared[(2, 1, 0), :, :]
    prepared = prepared * 255 - mean
    prepared = prepared[np.newaxis, :, :, :].astype(np.float32)
    return prepared


LUT_MAP = load_codes(LUT_TABLE)
KEYWORD_MAP = load_codes(CLASS_GROUP_TABLE)


class RecognizeResult:
    def __init__(self, breed_code=None, breed_name=None, breed_class=None, conf=None):
        self.breed_code = breed_code
        self.breed_name = breed_name
        self.breed_class = breed_class
        self.conf = conf

    def __str__(self):
        return "Prediction: %s \n" % self.breed_code + \
               "\tClass Name: %s \n" % self.breed_name + \
               "\tConfidence: %s" % get_percent(self.conf)

    def __eq__(self, other):
        return self.breed_code == other.breed_code and self.breed_class == other.breed_class


class Recognizer:

    def __init__(self):
        self._mean = 128
        self._predictor = self._load_model()
        self._image_size = MODEL[3]

    def recognize(self, image):
        example = self._predictor.run({'data': prepare_image(image, self._mean)})
        example = np.asarray(example)
        preds = np.squeeze(example)
        group, example_conf = max(enumerate(preds), key=operator.itemgetter(1))
        keyword = KEYWORD_MAP.get(group)

        return keyword

    def _load_model(self):
        INIT_NET = os.path.join(CAFFE_MODELS, MODEL[0], MODEL[1])
        PREDICT_NET = os.path.join(CAFFE_MODELS, MODEL[0], MODEL[2])
        with open(INIT_NET, "rb") as f:
            init_net = f.read()
        with open(PREDICT_NET, "rb") as f:
            predict_net = f.read()

        predictor = workspace.Predictor(init_net, predict_net)
        return predictor


instance = Recognizer()
