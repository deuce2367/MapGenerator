# MapGenerator

A stunning, premium Web Application for generating ultra-high resolution custom maps from anywhere in the world and seamlessly downloading them as image files.

## Overview
MapGenerator takes the raw XYZ map tiles normally used to display interactive sliding maps on the web, securely pulls down your desired area simultaneously, and stitches them into a beautiful, static `JPG` using the `Pillow` Python library. It perfectly matches your bounding rectangle, mathematically evaluating the zoom level required for outputs at resolutions of 1080p, 4K, and 8K.

## Map Provider Support
Included public APIs setup:
- **Carto Dark Matter** (Default)
- OpenStreetMap
- ESRI World Imagery (Satellite)
- ESRI World Topo
- Carto Positron (Minimal Light Theme)

## Tech Stack
- Frontend: Vanilla HTML/JS, Leaflet.js, Custom CSS Glassmorphism 
- Backend: FastAPI (Python), Pillow, Mercantile, HTTPX

## Setup Instructions
1. Navigate to the project directory:
   ```bash
   cd MapGenerator
   ```
2. Set up your virtual environment and install packages:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate  
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. Run the Backend:
   ```bash
   uvicorn main:app --reload --port 8001
   ```
4. Access the web app in your browser at `http://localhost:8001`!
