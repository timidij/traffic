# classifier/utils.py
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
from io import BytesIO
import base64


# Custom Layer Fix for DepthwiseConv2D
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import register_keras_serializable

@register_keras_serializable()
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_config(cls, config):
        config.pop('groups', None)
        return cls(**config)

# Model Loading with Custom Fix
def load_custom_model(model_path):
    return load_model(
        model_path,
        custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D}
    )

# Load model once when the app starts
MODEL = load_custom_model('keras_model.h5')
IMAGE_SIZE = (224, 224)
CLASS_NAMES = ['Traffic', 'No traffic'] # Make sure these match your model's output exactly

def preprocess_image(img_bytes):
    # """Process image bytes for prediction"""
    try:
        # Open image from bytes and convert to RGB
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        img = img.resize(IMAGE_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalize
        return img_array
    except Exception as e:
        print(f"Image processing error: {str(e)}")
        return None

def predict_image(img_bytes):
    """Make prediction from image bytes"""
    preprocessed_img = preprocess_image(img_bytes)
    if preprocessed_img is None:
        return None
    try:
        return MODEL.predict(preprocessed_img)
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return None

def get_prediction_result(img_bytes):
    # """Get prediction with image for display"""
    prediction = predict_image(img_bytes)
    if prediction is None:
        return None
        
    # Process results
    predicted_class = CLASS_NAMES[np.argmax(prediction)]
    
    confidence = float(np.max(prediction))
    
    # Prepare image for display (resize to reasonable dimensions)
    img = Image.open(BytesIO(img_bytes))
    img.thumbnail((300, 300))  # Create thumbnail for display
    
    # Convert to base64 for HTML display
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return {
        'class': predicted_class,
        'confidence': confidence,
        'image': img_str # This is the base64 string
    }

def get_traffic_demand(predictions):
    """
    Extracts simple boolean traffic demand from individual predictions.
    Returns: { 'north': True/False, 'south': True/False, 'east': True/False, 'west': True/False }
    """
    traffic_demand = {}
    for direction in ['north', 'south', 'east', 'west']:
        # Check if prediction exists and its class is 'Traffic'
        # Using .get() with default empty dict to prevent KeyError if a prediction is missing
        traffic_demand[direction] = predictions.get(direction, {}).get('class') == 'Traffic'
    return traffic_demand