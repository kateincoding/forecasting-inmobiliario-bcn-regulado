"""
transform/clean.py
Fase LOAD: filtros finales, exclusión de series problemáticas y tipado.
"""

import pandas as pd

from src.config import PipelineConfig


class DataCleaner:
    """
    Aplica los filtros de la fase LOAD y el tipado final de columnas.

    Uso:
        cleaner = DataCleaner(config)
        df_distritos_eda = cleaner.clean_districts(districts_full)
        df_barrios_eda   = cleaner.clean_barrios(barrios_full)
    """

    def __init__(self, config: PipelineConfig):
        self._barrios_excluidos = config.barrios_excluidos

    # ── Tipado compartido ────────────────────────────────────────────────────

    def _cast_types(self, df: pd.DataFrame, geo_col: str) -> pd.DataFrame:
        df = df.copy()
        for col in [geo_col, "quarter"]:
            if col in df.columns:
                df[col] = df[col].astype("category")
        if "neighborhood" in df.columns and geo_col != "neighborhood":
            df["neighborhood"] = df["neighborhood"].astype("category")
        for col in ["post_regulation", "covid_dummy"]:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        return df

    # ── LOAD de distritos ────────────────────────────────────────────────────

    def clean_districts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra filas con nulos en variables Incasol (Q4-2025 incompleto)
        y aplica tipado final.
        Retorna df_distritos_eda (esperado: 1030 × 27).
        """
        core = ["num_contracts", "avg_rent", "avg_rent_m2", "avg_surface"]
        mask = df[core].isnull().any(axis=1)
        return self._cast_types(df[~mask].copy(), "district")

    # ── LOAD de barrios ──────────────────────────────────────────────────────

    def clean_barrios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina Q4-2025 (incompleto en fuente) y los 7 barrios con series
        demasiado escasas, luego aplica tipado final.
        Retorna df_barrios_eda (esperado: 3102 × 28).
        """
        quarter_int = df["quarter"].astype(int)
        df_clean = df[~((df["year"] == 2025) & (quarter_int == 4))].copy()
        df_clean = df_clean[~df_clean["neighborhood"].isin(self._barrios_excluidos)].copy()
        return self._cast_types(df_clean, "neighborhood")
