import streamlit as st
import google.generativeai as genai
import os
import zipfile
from io import BytesIO

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Helper function to write files
def create_file_structure(app_code, output_folder):
    for file_name, file_content in app_code.items():
        file_path = os.path.join(output_folder, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

# Helper function to create a zip file
def create_zip_file(output_folder):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_folder)
                zipf.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit App UI
st.title("Android App Generator")
st.write("Use generative AI to create a deployment-ready Android app.")

# Prompt input field
prompt = st.text_area(
    "Enter your prompt for the Android app:", 
    "Create an Android app that tracks daily habits."
)

if st.button("Generate Android App Code"):
    try:
        # Load and configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate response from the model
        st.info("Generating app code...")
        response = model.generate_content(prompt)

        # Simulated app code output
        app_code = {
            "src/main/java/com/example/app/MainActivity.java": "public class MainActivity { /* ... */ }",
            "src/main/AndroidManifest.xml": "<manifest>...</manifest>",
            "src/main/res/layout/activity_main.xml": "<LinearLayout>...</LinearLayout>",
            "build.gradle": "apply plugin: 'com.android.application' // ...",
        }

        # Temporary folder for file generation
        output_folder = "generated_app"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create the file structure
        create_file_structure(app_code, output_folder)

        # Create the ZIP file
        zip_file = create_zip_file(output_folder)

        # Provide a download link
        st.success("Android app generated successfully!")
        st.download_button("Download ZIP File", zip_file, file_name="android_app.zip")

        # Visual Demo of the App
        st.subheader("Live Preview (Mockup)")
        st.write("This is a simple representation of the app's UI:")
        st.markdown("""
        <div style="border: 1px solid #ddd; padding: 10px; max-width: 300px; background-color: #f9f9f9;">
            <h4 style="text-align: center;">Daily Habits Tracker</h4>
            <p style="text-align: center;">Track your habits with ease!</p>
            <button style="display: block; margin: 10px auto; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Start Tracking</button>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")
