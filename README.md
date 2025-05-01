# city
No `requirements.txt` yet... To run this you will need to install Dash, Dash Bootstrap Components and Panda into your environment. Then, run app.py via `python3 app.py` from the repository folder.
Proposed project structure
```
src/
│
├── app.py                 # Main application initialization
├── index.py               # Entry point with server setup
├── layouts/
│   ├── __init__.py
│   ├── main_layout.py     # Main app layout
│   └── components.py      # Reusable layout components
├── callbacks/
│   ├── __init__.py
│   ├── chart_callbacks.py # Chart-related callbacks
│   ├── table_callbacks.py # Table-related callbacks
│   └── selection_callbacks.py # Selection-related callbacks
├── data/
│   ├── __init__.py
│   ├── cta-ridership-clean.csv
│   └── data_processing.py # Data processing functions
├── utils/
│   ├── __init__.py
│   └── utils.py           # Utility functions (already exists)
└── assets/
    └── custom.css         # Custom CSS if needed
```