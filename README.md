# Self-Reflection Diagram Generator 📊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

An open-source Streamlit app for turning self-reflection data into interactive visuals.

## What It Does

- Build an RPG-style skill profile with a radar chart.
- Track weekly time flow with a Sankey diagram.
- View habit consistency in a heatmap-style chart.
- Export generated visuals as images.

## Current Status

- Step 1: Base app layout and navigation completed.
- Step 2: RPG Skill Tree (Radar) implemented.
- Step 3: Time River (Sankey) implemented.
- Step 4: Consistency Heatmap implemented.

## Tech Stack

- Python
- Streamlit
- Plotly
- Pandas

## Run Locally

1. Clone the repository.

```bash
git clone https://github.com/Martrix987/Self-Reflection-Diagram-Generator.git
cd Self-Reflection-Diagram-Generator
```

2. Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Start the Streamlit app.

```bash
python -m streamlit run app.py
```

The app opens at http://localhost:8501.

## Troubleshooting

- `ModuleNotFoundError` (for example `No module named 'pandas'`):
	- Make sure the virtual environment is active.
	- Re-run `python -m pip install -r requirements.txt`.
- On Windows, avoid `python3` for this project:
	- `python3` can point to a different interpreter (`WindowsApps`) than your venv.
	- Use `python` after activation, or use `.\.venv\Scripts\python.exe` explicitly.
- For Streamlit apps, do not run `python app.py`:
	- Use `python -m streamlit run app.py`.

## Contributing

Issues and pull requests are welcome.

1. Fork the project.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a pull request.

## License

Distributed under the MIT License. See LICENSE for details.