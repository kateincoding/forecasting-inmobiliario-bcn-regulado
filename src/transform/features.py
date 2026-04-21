"""
transform/features.py
Feature engineering con interfaz fluent (encadenamiento de métodos).
"""

import numpy as np
import pandas as pd

from src.config import PipelineConfig


class FeatureEngineer:
    """
    Aplica transformaciones secuenciales sobre un panel trimestral.

    Uso:
        df_out = (
            FeatureEngineer(config)
            .fit(df_raw, group_col="neighborhood_code")
            .add_time_index()
            .add_growth_features()
            .add_lag_features()
            .add_regulation_dummies()
            .add_real_prices()
            .add_real_yoy_growth()
            .add_period_labels()
            .transform()
        )
    """

    def __init__(self, config: PipelineConfig):
        self._cfg      = config
        self._df       = None
        self._group    = None

    # ── Inicialización ────────────────────────────────────────────────────────

    def fit(self, df: pd.DataFrame, group_col: str) -> "FeatureEngineer":
        """Carga el DataFrame y define la columna de agrupación."""
        self._df    = df.copy()
        self._group = group_col
        return self

    def transform(self) -> pd.DataFrame:
        """Retorna el DataFrame con todas las transformaciones aplicadas."""
        if self._df is None:
            raise RuntimeError("Llama a .fit() antes de .transform()")
        return self._df.reset_index(drop=True)

    # ── Transformaciones ──────────────────────────────────────────────────────

    def add_time_index(self) -> "FeatureEngineer":
        """Crea columna 'date' desde (year, quarter) y ordena el panel."""
        self._df["date"] = (
            pd.PeriodIndex.from_fields(year=self._df["year"], quarter=self._df["quarter"])
            .to_timestamp()
        )
        self._df = self._df.sort_values([self._group, "date"])
        return self

    def add_growth_features(self) -> "FeatureEngineer":
        """
        Tasas de crecimiento YoY (4 trimestres) y QoQ (1 trimestre).
        NaN en los primeros 4 trimestres de cada unidad son estructurales.
        """
        g = self._df.groupby(self._group)
        self._df["contract_growth_yoy"] = g["num_contracts"].pct_change(4, fill_method=None)
        self._df["rent_growth_yoy"]     = g["avg_rent"].pct_change(4, fill_method=None)
        self._df["rent_m2_growth_yoy"]  = g["avg_rent_m2"].pct_change(4, fill_method=None)
        self._df["contract_growth_qoq"] = g["num_contracts"].pct_change(1, fill_method=None)
        return self

    def add_lag_features(self) -> "FeatureEngineer":
        """
        Rezagos de avg_rent_m2: lag1 (1 trimestre) y lag4 (1 año).
        NaN en los primeros trimestres son estructurales.
        """
        g = self._df.groupby(self._group)
        self._df["rent_m2_lag1"] = g["avg_rent_m2"].shift(1)
        self._df["rent_m2_lag4"] = g["avg_rent_m2"].shift(4)
        return self

    def add_regulation_dummies(self) -> "FeatureEngineer":
        """
        Dummies regulatorias (fechas desde PipelineConfig):
          - post_regulation : 1 desde reg_start (Ley 11/2020)
          - covid_dummy     : 1 entre covid_start y covid_end
          - D_ley11         : Ley 11/2020 activa
          - D_tc_gap        : Vacío TC (TC anula la ley, sin nueva regulación)
          - D_ley12         : Ley 12/2023 / zona tensionada
        """
        d = self._df["date"]
        c = self._cfg
        self._df["post_regulation"] = (d >= c.reg_start).astype(int)
        self._df["covid_dummy"]     = ((d >= c.covid_start) & (d <= c.covid_end)).astype(int)
        self._df["D_ley11"]  = ((d >= c.reg_start)    & (d < c.tc_gap_start)).astype(int)
        self._df["D_tc_gap"] = ((d >= c.tc_gap_start) & (d < c.tc_gap_end)).astype(int)
        self._df["D_ley12"]  = (d >= c.ley12_start).astype(int)
        return self

    def add_real_prices(self) -> "FeatureEngineer":
        """
        Deflacta avg_rent y avg_rent_m2 con ipc_index_q a base 2025.
        Requiere que merge_macrovars haya añadido ipc_index_q.
        NaN donde ipc_index_q es NaN (distritos pre-2002) son estructurales.
        """
        self._df["avg_rent_real_2025base"]    = self._df["avg_rent"]    / (self._df["ipc_index_q"] / 100)
        self._df["avg_rent_m2_real_2025base"] = self._df["avg_rent_m2"] / (self._df["ipc_index_q"] / 100)
        return self

    def add_real_yoy_growth(self) -> "FeatureEngineer":
        """Crecimiento YoY de precios reales (base 2025)."""
        g = self._df.sort_values([self._group, "date"]).groupby(self._group)
        self._df["rent_real_growth_yoy"]    = g["avg_rent_real_2025base"].pct_change(4, fill_method=None)
        self._df["rent_m2_real_growth_yoy"] = g["avg_rent_m2_real_2025base"].pct_change(4, fill_method=None)
        return self

    def add_period_labels(self) -> "FeatureEngineer":
        """
        Etiquetas categóricas de periodo:
          - period_prepost  : Pre-regulation / Post-regulation
          - period_4levels  : Pre-COVID / COVID shock / Regulation+COVID / Post-overlap
        """
        df = self._df
        quarter_num = df["quarter"].astype(int)

        df["period_prepost"] = np.where(
            df["date"] < self._cfg.reg_start, "Pre-regulation", "Post-regulation"
        )
        df["period_prepost"] = pd.Categorical(
            df["period_prepost"],
            categories=["Pre-regulation", "Post-regulation"],
            ordered=True,
        )

        choices = [
            "Pre-COVID / pre-regulation",
            "COVID shock",
            "Regulation + COVID / transition",
            "Post-overlap / new regime",
        ]
        conditions = [
            df["year"] <= 2019,
            (df["year"] == 2020) & quarter_num.isin([1, 2, 3]),
            ((df["year"] == 2020) & (quarter_num == 4)) | (df["year"] == 2021),
            df["year"] >= 2022,
        ]
        df["period_4levels"] = pd.Categorical(
            np.select(conditions, choices, default="Unknown"),
            categories=choices,
            ordered=True,
        )
        self._df = df
        return self
