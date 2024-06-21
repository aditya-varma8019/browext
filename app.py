from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
import pyautogui
from sklearn.cluster import KMeans

app = Flask(__name__)

# Path to the extracted model directory
model_dir = "ssd_mobilenet_v2_coco_2018_03_29/saved_model"
model = tf.saved_model.load(model_dir)
infer = model.signatures["serving_default"]

# COCO dataset category indices
category_index = {
    1: "person",
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    5: "airplane",
    6: "bus",
    7: "train",
    8: "truck",
    9: "boat",
    10: "traffic light",
    11: "fire hydrant",
    13: "stop sign",
    14: "parking meter",
    15: "bench",
    16: "bird",
    17: "cat",
    18: "dog",
    19: "horse",
    20: "sheep",
    21: "cow",
    22: "elephant",
    23: "bear",
    24: "zebra",
    25: "giraffe",
    27: "backpack",
    28: "umbrella",
    31: "handbag",
    32: "tie",
    33: "suitcase",
    34: "frisbee",
    35: "skis",
    36: "snowboard",
    37: "sports ball",
    38: "kite",
    39: "baseball bat",
    40: "baseball glove",
    41: "skateboard",
    42: "surfboard",
    43: "tennis racket",
    44: "bottle",
    46: "wine glass",
    47: "cup",
    48: "fork",
    49: "knife",
    50: "spoon",
    51: "bowl",
    52: "banana",
    53: "apple",
    54: "sandwich",
    55: "orange",
    56: "broccoli",
    57: "carrot",
    58: "hot dog",
    59: "pizza",
    60: "donut",
    61: "cake",
    62: "chair",
    63: "couch",
    64: "potted plant",
    65: "bed",
    67: "dining table",
    70: "toilet",
    72: "tv",
    73: "laptop",
    74: "mouse",
    75: "remote",
    76: "keyboard",
    77: "cell phone",
    78: "microwave",
    79: "oven",
    80: "toaster",
    81: "sink",
    82: "refrigerator",
    84: "book",
    85: "clock",
    86: "vase",
    87: "scissors",
    88: "teddy bear",
    89: "hair drier",
    90: "toothbrush",
}


def load_image(image_data):
    image = Image.open(BytesIO(image_data))
    image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    return image_rgb


def detect_objects(image):
    input_tensor = tf.convert_to_tensor(image, dtype=tf.uint8)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = infer(inputs=input_tensor)
    return detections


def preprocess_image(image_rgb):
    height, width = image_rgb.shape[:2]
    zoom_factor = 1
    new_height = int(height * zoom_factor)
    new_width = int(width * zoom_factor)
    zoomed_image = cv2.resize(
        image_rgb, (new_width, new_height), interpolation=cv2.INTER_LINEAR
    )
    center_y, center_x = new_height // 2, new_width // 2
    start_y = center_y - height // 2
    end_y = start_y + height
    start_x = center_x - width // 2
    end_x = start_x + width
    cropped_image = zoomed_image[start_y:end_y, start_x:end_x]
    normalized_image = cropped_image / 255.0
    preprocessed_image = (normalized_image * 255).astype(np.uint8)
    return preprocessed_image


def get_dominant_color(image):
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)

    # Perform k-means clustering to find the most common colors
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(pixels)

    # Get the RGB values of the centers
    colors = kmeans.cluster_centers_

    # Convert RGB to HSV for better color naming
    colors_hsv = cv2.cvtColor(np.uint8([colors]), cv2.COLOR_RGB2HSV)[0]

    # Define color ranges in HSV
    color_ranges = {
        "red": ([0, 100, 100], [10, 255, 255]),
        "orange": ([11, 100, 100], [20, 255, 255]),
        "yellow": ([21, 100, 100], [30, 255, 255]),
        "green": ([31, 100, 100], [80, 255, 255]),
        "blue": ([81, 100, 100], [130, 255, 255]),
        "purple": ([131, 100, 100], [170, 255, 255]),
        "pink": ([171, 100, 100], [180, 255, 255]),
        "brown": ([0, 100, 20], [20, 255, 200]),
        "white": ([0, 0, 200], [180, 30, 255]),
        "gray": ([0, 0, 70], [180, 30, 200]),
        "black": ([0, 0, 0], [180, 255, 70]),
    }

    # Find the dominant color
    for color, (lower, upper) in color_ranges.items():
        if np.all(colors_hsv[0] >= lower) and np.all(colors_hsv[0] <= upper):
            return color

    return ""


def get_amazon_link(color, query):
    return f"https://www.amazon.com/s?k={color}+{query}"


def crop_object(image, box):
    ymin, xmin, ymax, xmax = box
    height, width, _ = image.shape
    left, right, top, bottom = (
        int(xmin * width),
        int(xmax * width),
        int(ymin * height),
        int(ymax * height),
    )
    return image[top:bottom, left:right]


@app.route("/")
def index():
    return "Welcome to the Object Detection API"


@app.route("/detect", methods=["POST"])
def detect():
    try:
        # Take a screenshot of the entire screen
        screenshot = pyautogui.screenshot()
        image_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)
        img = preprocess_image(image_rgb)
        detections = detect_objects(img)

        detected_objects = []
        for i in range(len(detections["detection_boxes"][0])):
            box = detections["detection_boxes"][0][i].numpy()
            class_id = int(detections["detection_classes"][0][i])
            score = detections["detection_scores"][0][i].numpy()
            if score > 0.5:
                label = category_index.get(class_id, "Unknown")
                cropped_img = crop_object(img, box)
                color = get_dominant_color(cropped_img)
                _, buffer = cv2.imencode(".jpg", cropped_img)
                img_str = base64.b64encode(buffer).decode("utf-8")
                detected_objects.append(
                    {
                        "label": label,
                        "color": color,
                        "image": img_str,
                        "amazon_link": get_amazon_link(color, label),
                    }
                )

        unique_objects = list(
            {f"{obj['color']} {obj['label']}": obj for obj in detected_objects}.values()
        )
        return jsonify({"detected_objects": unique_objects})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
