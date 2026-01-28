"""
Configuration centralisée pour le dashboard E-commerce.
"""

from pathlib import Path
from typing import Final

# Paths
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
DATA_RAW_DIR: Final[Path] = DATA_DIR / "raw"
DATA_CLEAN_DIR: Final[Path] = DATA_DIR / "clean"

EVENTS_CLEAN_PATH: Final[Path] = DATA_CLEAN_DIR / "events_clean.csv"
CATEGORY_TREE_PATH: Final[Path] = DATA_RAW_DIR / "category_tree.csv"
ITEM_PROPERTIES_PART1_PATH: Final[Path] = DATA_RAW_DIR / "item_properties_part1.csv"
ITEM_PROPERTIES_PART2_PATH: Final[Path] = DATA_RAW_DIR / "item_properties_part2.csv"

# Streamlit Config
STREAMLIT_PAGE_TITLE: Final[str] = "E-Commerce Dashboard"
STREAMLIT_PAGE_ICON: Final[str] = ":chart_with_upwards_trend:"
STREAMLIT_LAYOUT: Final[str] = "wide"
STREAMLIT_INITIAL_SIDEBAR_STATE: Final[str] = "expanded"

# Data Processing
TIMESTAMP_UNIT: Final[str] = "ms"  # RetailRocket uses milliseconds
CACHE_TTL: Final[int] = 3600  # seconds

# Funnel Events
EVENT_VIEW: Final[str] = "view"
EVENT_ADDTOCART: Final[str] = "addtocart"
EVENT_TRANSACTION: Final[str] = "transaction"
FUNNEL_EVENTS: Final[list[str]] = [EVENT_VIEW, EVENT_ADDTOCART, EVENT_TRANSACTION]

# A/B Test
AB_TEST_DEFAULT_UPLIFT: Final[float] = 0.10  # 10% uplift
AB_TEST_SEED: Final[int] = 42
SIGNIFICANCE_LEVEL: Final[float] = 0.05

# Cohort Analysis
COHORT_DEFAULT_FREQ: Final[str] = "W"  # "W" for weekly, "M" for monthly
