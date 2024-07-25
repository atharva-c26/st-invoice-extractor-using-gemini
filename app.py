import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if api_key is None:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

# Configure genai with the API key
genai.configure(api_key=api_key)

# Function to load Gemini Pro Vision model (updated)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(input_prompt, user_input, image_data):
    """Fetches response from Gemini Pro Vision model based on input prompt and user input."""

    if image_data:
        # Extract the actual image data from the first element
        image_bytes = image_data[0]["data"]
        
        # Create a Content object with the text and image
        content = [
            input_prompt + "\n" + user_input,
            {"mime_type": image_data[0]["mime_type"], "data": image_bytes}
        ]
    else:
        # Handle no image uploaded case
        return "No image uploaded, cannot process invoice."

    # Generate content using the model
    response = model.generate_content(content)
    return response.text

def input_image_details(uploaded_file):
    """Processes uploaded image and returns a list of image parts."""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit app initialization
st.set_page_config(page_title="Multilanguage Invoice Extractor")

st.header("Multi-language Invoice Extractor")

user_input = st.text_input("Input Prompt:", key="input")
uploaded_file = st.file_uploader("Choose an image of the invoice", type=["jpg", "jpeg", "png"])

image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit_button = st.button("Tell me about the invoice")

input_prompt = """
You are an expert in understanding invoices. We will upload an image as invoice
and you will have to answer any questions based on the uploaded invoice image
"""

if submit_button:
    try:
        image_data = input_image_details(uploaded_file)
        if image_data:
            response = get_gemini_response(input_prompt, user_input, image_data)
            st.subheader("The response is:")
            st.write(response)
        else:
            st.error("No image uploaded")
    except (ValueError, FileNotFoundError) as e:
        st.error(f"An error occurred: {e}")