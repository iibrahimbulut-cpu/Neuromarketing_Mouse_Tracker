GuPie v4: AI-Powered Image Analysis Tool
GuPie is a desktop application built with Tkinter that leverages the power of Google Gemini Pro Vision (Gemini Flash) to perform intelligent analysis on images. It features a robust "Smart Wait" system to handle API rate limits and a clean, user-friendly interface for batch processing.

Key Features
Multi-Image Analysis: Upload and process multiple images (JPG, PNG, WEBP) simultaneously.
Gemini AI Integration: Powered by gemini-flash-latest for high-speed, accurate visual understanding.
Smart Rate-Limit Handling: Automatically detects "429 Too Many Requests" errors and pauses execution to prevent API crashes.
Safety Bypass: Configured with BLOCK_NONE thresholds to ensure the AI provides unfiltered technical or descriptive analysis when needed.
Live Preview: View selected images directly within the application before starting the analysis.
Detailed Reporting: Generates a comprehensive text report of all findings in a dedicated scrollable window.

Technical Setup
Prerequisites
Python 3.10+
A Google Gemini API Key (get it from Google AI Studio)

Installation
Clone the repo:
Bash
git clone https://github.com/yourusername/gupie-v4.git
cd gupie-v4
Install dependencies:

Bash
pip install google-generativeai pillow numpy opencv-python matplotlib
Configuration
Open GuPie_v4.py and replace the API_KEY variable with your own key:

Python
API_KEY = "YOUR_ACTUAL_API_KEY_HERE"

How to Use
Run the app:

Bash
python GuPie_v4.py
Select Images: Click the "Resim Seç" (Select Image) button to load your files.

Process: Click "Analiz Et" (Analyze).
Wait & Review: The app will cycle through each image. If the API hits a limit, it will count down (20 seconds) and retry automatically.
View Report: Once finished, a new window will pop up with the AI's detailed descriptions for every image.

Technologies

Tkinter: For the native Windows/Linux/macOS GUI.
Google Generative AI SDK: The core engine for image interpretation.
OpenCV & PIL: For image handling and processing.
Custom DPI Fix: Includes ctypes support for high-resolution (4K) displays to prevent blurry UI.

⚠️ Disclaimer
This tool uses a specific API key configuration. Ensure you keep your API_KEY private and do not commit it directly to public repositories.
