'''
analyze_current_data.py
Analyze current data from LabView CSV files for Y-PENG research.

Goal of script:
find maximum, minimum, mean, and peak current
peak = max - min

OUTLINE:

1. Imports and Input file (UI .csv file selector in data folder instead of manually hardcoding in code)
2. Load PENG data (exception handling with tkinter)
3. Plot results (make sure to convert to readable units) - add labels and title
4. Find max, min, mean current value and find peak (max - min) & display results in tkinter window 
5. In tkinter output window have option to save results in a file 
'''