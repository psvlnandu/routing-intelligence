# routing-intelligence

---
title: Route Optimization Algorithm Comparison
colorFrom: blue
colorTo: purple
sdk: docker
app_file: frontend/app.py
pinned: false
---

# Route Optimization: Algorithm Comparison

An interactive tool to visualize how UCS, A*, and Greedy Best-First search algorithms explore different paths between any two locations using real Google Maps data.

## Features

- **Real Geographic Data** - Uses Google Maps API for actual coordinates and distances
- **Dynamic Network Building** - Automatically finds intermediate cities along routes
- **Three Algorithm Comparison** - See UCS, A*, and Greedy in action
- **Live Metrics** - Compare nodes expanded, distances, and execution times
- **Visual Exploration** - Watch how each algorithm explores different paths

## How It Works

1. Enter any two locations (cities, towns, villages)
2. Backend automatically builds a network of intermediate cities using Google Places API
3. All three pathfinding algorithms run on this dynamic network
4. Visualize the results with colored lines showing exploration patterns

## Algorithms

- **UCS (Dijkstra)**: Guarantees optimal path, explores methodically
- **A* Search**: Uses heuristic to guide search, optimal AND efficient
- **Greedy Best-First**: Fastest but may find suboptimal paths

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Streamlit + Folium
- **APIs**: Google Maps (Geocoding, Places, Distance Matrix)
- **Algorithms**: Course-provided search framework

## Project By

Poorna | Clarkson University | AI Course Project