"""Sairow Solutions Invoice Generator.

Streamlit entry point. Run with::

    streamlit run app.py

All application logic lives in the ``src`` package (see ``src/README`` layout
in the project README).
"""

from src.views import render

if __name__ == "__main__":
    render()
else:
    # Streamlit executes this module as a script rather than importing it.
    render()
