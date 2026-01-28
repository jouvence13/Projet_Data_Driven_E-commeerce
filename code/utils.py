"""
Fonctions utilitaires et helpers pour le dashboard.
"""

import pandas as pd
import numpy as np
from typing import Union


def format_int(value: Union[float, int]) -> str:
    """
    Formate un nombre entier avec séparateurs de milliers (espaces).
    
    Args:
        value: Nombre à formater
        
    Returns:
        Nombre formaté avec espaces
        
    Example:
        >>> format_int(1234567)
        '1 234 567'
    """
    return f"{int(value):,}".replace(",", " ")


def fmt_pct(value: float, decimals: int = 2) -> str:
    """
    Formate un pourcentage.
    
    Args:
        value: Valeur décimale (0-1)
        decimals: Nombre de décimales
        
    Returns:
        Pourcentage formaté (ex: "25.50%")
        
    Example:
        >>> fmt_pct(0.2550)
        '25.50%'
    """
    if pd.isna(value):
        return "—"
    return f"{value * 100:.{decimals}f}%"


def fmt_num(value: float, decimals: int = 2) -> str:
    """
    Formate un nombre décimal.
    
    Args:
        value: Nombre à formater
        decimals: Nombre de décimales
        
    Returns:
        Nombre formaté
        
    Example:
        >>> fmt_num(3.14159, 2)
        '3.14'
    """
    if pd.isna(value):
        return "—"
    return f"{value:.{decimals}f}"


def safe_divide(numerator: Union[pd.Series, np.ndarray, float],
                denominator: Union[pd.Series, np.ndarray, float],
                fill_value: float = np.nan) -> Union[pd.Series, np.ndarray, float]:
    """
    Division sûre (évite les divisions par zéro).
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        fill_value: Valeur par défaut en cas de division par zéro
        
    Returns:
        Résultat de la division
        
    Example:
        >>> safe_divide(10, 0)
        nan
    """
    if isinstance(denominator, (pd.Series, np.ndarray)):
        return np.where(denominator != 0, numerator / denominator, fill_value)
    else:
        return numerator / denominator if denominator != 0 else fill_value


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Valide qu'un DataFrame contient les colonnes requises.
    
    Args:
        df: DataFrame à valider
        required_columns: Liste des colonnes requises
        
    Raises:
        ValueError: Si des colonnes manquent
    """
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")


def handle_missing_values(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
    """
    Gère les valeurs manquantes.
    
    Args:
        df: DataFrame
        strategy: "drop" ou "fill"
        
    Returns:
        DataFrame nettoyé
    """
    if strategy == "drop":
        return df.dropna()
    elif strategy == "fill":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return df.fillna(df[numeric_cols].median())
    else:
        raise ValueError(f"Stratégie inconnue: {strategy}")
