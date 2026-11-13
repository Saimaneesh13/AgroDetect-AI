import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image
import os

# ======================
# LOAD MODEL
# ======================
MODEL_PATH = os.path.join("model", "plant_disease_model_best.keras")
CLASS_JSON_PATH = os.path.join("model", "class_indices.json")

model = tf.keras.models.load_model(MODEL_PATH)

# ======================
# LOAD CLASS INDICES
# ======================
with open(CLASS_JSON_PATH, "r") as f:
    class_indices = json.load(f)

# reverse mapping: index → class name
idx_to_class = {v: k for k, v in class_indices.items()}

print("Model and class indices loaded")


# ======================
# PREDICTION FUNCTION
# ======================
def predict_disease(img_path):
    """
    Predict plant disease from image path
    """

    # load image
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)

    # preprocess for EfficientNet
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    # prediction
    preds = model.predict(img_array, verbose=0)
    pred_index = np.argmax(preds)
    confidence = float(np.max(preds))

    disease_name = idx_to_class[pred_index]

    return {
        "class": disease_name,
        "confidence": round(confidence * 100, 2)
    }
