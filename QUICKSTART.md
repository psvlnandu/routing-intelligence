# Quick Start Guide

## Setup (First Time Only)

```bash
# 1. Navigate to project directory
cd routing-intelligence

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the Project

### To see the interactive web app:

**Terminal 1:**
```bash
python main.py
```

**Terminal 2 (new terminal):**
```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### To test algorithms from command line:

```bash
cd backend
python test_algorithms.py
```

## What to Try

1. **Buffalo to NYC**
   - Long route
   - Shows A*'s efficiency best
   - Greedy is suboptimal

2. **Rochester to Albany**
   - Medium route
   - Multiple path options
   - Clear algorithm differences

3. **Any neighboring cities**
   - Short routes
   - All algorithms converge
   - But A* still wins on expansions

## What You'll See

### On the map:
- Blue dots = UCS explored cities
- Red dots = A* explored cities
- Green dots = Greedy explored cities
- Lines show the final paths

### In the metrics:
- A* expands 40-50% fewer nodes than UCS
- Greedy is fastest but often suboptimal
- All three paths show in the interface

## Troubleshooting

**"Cannot connect to API"**
- Make sure `python main.py` is running in another terminal
- Check that no other service is using port 8000

**"City not found"**
- Check spelling and capitalization
- Use the dropdown to select cities

**Slow performance**
- This is normal for first run (hashing overhead)
- Subsequent runs are fast

## Key Results to Show Your Classmates

1. **A* vs UCS (Buffalo → NYC)**
   - UCS: 70 nodes expanded
   - A*: 40 nodes expanded
   - **A* saves 42.9%!**

2. **Greedy Weakness**
   - Greedy path: 755 miles
   - A* optimal: 490 miles
   - **Greedy is 55% longer!**

3. **Visual Comparison**
   - Watch how UCS fans out broadly
   - A* stays focused toward goal
   - Greedy takes shortcuts (wrong ones)

---

**Next Steps:**
- Run the algorithms
- Check the visualization
- Read the README.md for detailed explanation
- Review the code comments to understand the implementation