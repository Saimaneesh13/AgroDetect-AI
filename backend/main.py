from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import json
import os

from backend.treatment import get_treatment
from tensorflow.keras.applications.efficientnet import preprocess_input

# =============================
# APP INIT
# =============================
app = FastAPI(title="AgroDetect AI API")

# ✅ VERY IMPORTANT (fixes Streamlit connection issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# PATHS
# =============================
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "plant_disease_model_best.keras")
CLASS_INDEX_PATH = os.path.join(BASE_DIR, "model", "class_indices.json")

# =============================
# LOAD MODEL
# =============================
print("🔄 Loading model...")

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_INDEX_PATH, "r") as f:
    class_indices = json.load(f)

# reverse mapping
idx_to_class = {v: k for k, v in class_indices.items()}

print("✅ Model loaded successfully")

IMG_SIZE = 224

# =============================
# IMAGE PREPROCESS
# =============================
def prepare_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(image)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


# =============================
# HEALTH CHECK
# =============================
@app.get("/")
def root():
    return {"message": "AgroDetect AI Backend Running"}


# =============================
# PREDICT ENDPOINT
# =============================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # preprocess
        img_array = prepare_image(image)

        # prediction
        preds = model.predict(img_array)[0]
        class_idx = int(np.argmax(preds))
        confidence = float(preds[class_idx])

        disease_name = idx_to_class.get(class_idx, "Unknown")

        # get treatment
        treatment = get_treatment(disease_name)

        return {
            "disease": disease_name,
            "confidence": confidence,  # ✅ already 0–1
            "treatment": treatment,
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# =============================
# RUN (optional)
# =============================
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)