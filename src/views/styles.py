"""Streamlit styling for the invoice page."""

from src.config import PRIMARY_COLOR

PAGE_CSS = f"""
    <style>
    .main {{
        padding: 2rem;
    }}
    .stButton>button {{
        width: 100%;
        background-color: {PRIMARY_COLOR};
        color: white;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 5px;
    }}
    .invoice-header {{
        text-align: center;
        color: {PRIMARY_COLOR};
        padding: 1rem;
        border-bottom: 3px solid {PRIMARY_COLOR};
        margin-bottom: 2rem;
    }}
    </style>
"""
