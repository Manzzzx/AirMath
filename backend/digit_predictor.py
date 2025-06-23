import tensorflow as tf
import numpy as np
import cv2

# Load model saat import
model = tf.keras.models.load_model("digit_model.h5")

def predict_digit(image):
    """
    Terima image 28x28 grayscale (numpy array),
    return prediksi angka (0–9)
    """
    if image.shape != (28, 28):
        image = cv2.resize(image, (28, 28))

    image = image.astype("float32") / 255.0
    image = image.reshape(1, 28, 28, 1)
    preds = model.predict(image)
    return np.argmax(preds)
