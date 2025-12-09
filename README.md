---
title: Route Optimization Algorithm Comparison
sdk: docker
app_file: frontend/app.py
pinned: false
---

# Route Optimization: Algorithm Comparison

An interactive tool to visualize how UCS, A*, and Greedy Best-First search algorithms explore different paths between any two locations using real Google Maps data.

## Features

- 🗺️ Real Geographic Data - Uses Google Maps API
- 🔍 Dynamic Network Building - Finds intermediate cities automatically
- ⚙️ Three Algorithm Comparison - UCS, A*, and Greedy
- 📊 Live Metrics - Nodes expanded, distances, execution times
- 🎨 Visual Exploration - Watch algorithms work in real-time

## Tech Stack

- Backend: FastAPI + Python
- Frontend: Streamlit + Folium
- APIs: Google Maps

  ## How to run?

  - Launch <a href ="https://routing-intelligence-backend.onrender.com/">backend</a>
  
  - 
    ```
    # clone the repo
    git clone repo_name
    
    # change directory
    cd frontend

    # run streamlit app
    streamlit run app.py
    ```
    
