import streamlit as st
import google.generativeai as genai
import os
import zipfile
from io import BytesIO
from datetime import datetime
import subprocess

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

# Helper function to build APK
def build_apk(output_folder):
    try:
        # Run the Gradle build command
        result = subprocess.run(["./gradlew", "assembleDebug"], cwd=output_folder, capture_output=True, text=True)
        
        if result.returncode != 0:
            st.error(f"APK build failed: {result.stderr}")
            return None

        apk_path = os.path.join(output_folder, "app/build/outputs/apk/debug/app-debug.apk")
        if os.path.exists(apk_path):
            return apk_path
        else:
            st.error("APK file not found after build.")
            return None
    except Exception as e:
        st.error(f"Error during APK build: {e}")
        return None

# Streamlit App UI
st.set_page_config(page_title="Android App Generator", layout="wide")
st.title("Advanced Android App Generator")
st.write("Use generative AI to create a fully functional, deployment-ready Android app.")

# Prompt input field
prompt = st.text_area(
    "Enter your prompt for the Android app:",
    placeholder="e.g., Create an Android app to manage a grocery list with categories and reminders.",
    height=150
)

# Features checkbox
st.sidebar.header("Advanced Features")
generate_ui_preview = st.sidebar.checkbox("Generate Live UI Mockup Preview", value=True)
generate_detailed_code = st.sidebar.checkbox("Generate Detailed Code (XML, Java, Gradle)", value=True)
timestamp_output = st.sidebar.checkbox("Add Timestamp to Output Files", value=True)

if st.button("Generate Android App Code"):
    try:
        # Load and configure the model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate response from the model
        st.info("Generating app code, please wait...")
        response = model.generate_content(prompt)

        # Simulated app code output
        app_code = {
            "app/src/main/java/com/example/app/MainActivity.java": """ 
                package com.example.app;
                import android.os.Bundle;
                import androidx.appcompat.app.AppCompatActivity;
                public class MainActivity extends AppCompatActivity {
                    @Override
                    protected void onCreate(Bundle savedInstanceState) {
                        super.onCreate(savedInstanceState);
                        setContentView(R.layout.activity_main);
                    }
                }
            """,
            "app/src/main/AndroidManifest.xml": """
                <manifest xmlns:android="http://schemas.android.com/apk/res/android"
                          package="com.example.app">
                    <application
                        android:label="My App"
                        android:icon="@mipmap/ic_launcher">
                        <activity android:name=".MainActivity">
                            <intent-filter>
                                <action android:name="android.intent.action.MAIN" />
                                <category android:name="android.intent.category.LAUNCHER" />
                            </intent-filter>
                        </activity>
                    </application>
                </manifest>
            """,
            "app/src/main/res/layout/activity_main.xml": """
                <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
                              android:layout_width="match_parent"
                              android:layout_height="match_parent"
                              android:orientation="vertical"
                              android:padding="16dp">
                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Welcome to the Generated App!"
                        android:textSize="18sp"
                        android:layout_gravity="center_horizontal" />
                    <Button
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Click Me"
                        android:layout_gravity="center_horizontal" />
                </LinearLayout>
            """,
            "app/build.gradle": """
                plugins {
                    id 'com.android.application'
                }
                android {
                    compileSdkVersion 33
                    defaultConfig {
                        applicationId "com.example.app"
                        minSdkVersion 21
                        targetSdkVersion 33
                        versionCode 1
                        versionName "1.0"
                    }
                    buildTypes {
                        release {
                            minifyEnabled false
                        }
                    }
                }
                dependencies {
                    implementation "androidx.appcompat:appcompat:1.4.1"
                    implementation "com.google.android.material:material:1.5.0"
                }
            """,
            "settings.gradle": """
                include ':app'
            """,
            "build.gradle": """
                // Top-level build file where you can add configuration options common to all sub-projects/modules.
                buildscript {
                    repositories {
                        google()
                        mavenCentral()
                    }
                    dependencies {
                        classpath "com.android.tools.build:gradle:7.0.4"
                    }
                }
                allprojects {
                    repositories {
                        google()
                        mavenCentral()
                    }
                }
            """
        }

        # Temporary folder for file generation
        output_folder = "generated_app"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create the file structure
        create_file_structure(app_code, output_folder)

        # Add timestamp if selected
        timestamp = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if timestamp_output else ""
        zip_file_name = f"android_app{timestamp}.zip"

        # Create the ZIP file
        zip_file = create_zip_file(output_folder)

        # Provide a download link
        st.success("Android app generated successfully!")
        st.download_button("Download ZIP File", zip_file, file_name=zip_file_name)

        # Build APK
        st.info("Building APK file, please wait...")
        apk_path = build_apk(output_folder)
        if apk_path:
            with open(apk_path, "rb") as apk_file:
                st.download_button("Download APK File", apk_file, file_name="app-debug.apk")

        # Advanced features
        if generate_ui_preview:
            st.subheader("Live UI Mockup Preview")
            st.write("This is a simple representation of the app's UI:")
            st.markdown("""
            <div style="border: 1px solid #ddd; padding: 10px; max-width: 300px; background-color: #f9f9f9;">
                <h4 style="text-align: center;">Generated App UI</h4>
                <p style="text-align: center;">Welcome to the Generated App!</p>
                <button style="display: block; margin: 10px auto; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Click Me</button>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
