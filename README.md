# Weekly Schedule Planner

An interactive weekly schedule planner built with [Streamlit](https://streamlit.io) and [Matplotlib](https://matplotlib.org/).  
You can add, edit, and delete tasks for each day of the week, and visualize them on a timeline.

## Features
- Add tasks with name, start time, duration, and color
- Edit or delete existing tasks
- Choose between 12-hour and 24-hour view
- Visualize your schedule in a horizontal timeline (like a Gantt chart)
- Reset schedule with one click

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/d-beloved/weekly-schedule.git
   cd weekly-schedule
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the app with Streamlit:

```bash
streamlit run weekly_schedule.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

## Example Screenshot

_Add a screenshot of your app output here for clarity._

## Project Structure
```
.
├── weekly_schedule.py   # Main Streamlit app
├── requirements.txt     # Dependencies
└── README.md            # Project documentation
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

## License
[MIT](LICENSE)