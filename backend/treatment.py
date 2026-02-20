def get_treatment(disease_name: str) -> str:
    treatments = {
        "Tomato_Septoria_leaf_spot":
            "Remove infected leaves and apply fungicide containing chlorothalonil.",
        "Tomato_Late_blight":
            "Apply copper-based fungicide and avoid overhead watering.",
        "Potato_Early_blight":
            "Use crop rotation and apply appropriate fungicide.",
        "Pepper__bell___healthy":
            "Your plant looks healthy. Maintain proper watering and nutrition.",
    }

    return treatments.get(
        disease_name,
        "Consult an agriculture expert."
    )