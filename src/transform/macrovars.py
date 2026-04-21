"""
transform/macrovars.py
Carga y merge de variables macroeconómicas: IPC INE, Euribor 12M BDE, IST Idescat.
"""

import unicodedata
from pathlib import Path

import pandas as pd

from src.config import PipelineConfig


class MacroVarLoader:
    """
    Carga IPC, Euribor e IST desde data/data_raw/ y los mergea en un panel.

    Uso:
        loader = MacroVarLoader(config)
        ipc_q     = loader.load_ipc()
        euribor_q = loader.load_euribor()
        ist_df    = loader.load_ist()
        panel_out = loader.merge_into(panel_df, include_ist=True)
    """

    _IST_NAME_MAP = {
        "el poble sec":               "el poble sec - aei parc montjuic",
        "la marina del prat vermell": "la marina del prat vermell - aei zona franca",
        "sant gervasi-galvany":       "sant gervasi - galvany",
        "sant gervasi-la bonanova":   "sant gervasi - la bonanova",
        "sants-badal":                "sants - badal",
    }

    _MONTH_MAP = {
        "ene": "01", "feb": "02", "mar": "03", "abr": "04",
        "may": "05", "jun": "06", "jul": "07", "ago": "08",
        "sep": "09", "oct": "10", "nov": "11", "dic": "12",
    }

    def __init__(self, config: PipelineConfig):
        self.raw_path = config.raw_path

    # ── Utilidades ────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text) -> str:
        if pd.isna(text):
            return text
        text = str(text).strip().lower()
        text = "".join(
            ch for ch in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(ch)
        )
        text = text.replace("\u2019", "'").replace("`", "'")
        return " ".join(text.split())

    @staticmethod
    def _to_quarterly_date(year_s: pd.Series, quarter_s: pd.Series) -> pd.Series:
        month = ((quarter_s - 1) * 3 + 1).astype(str)
        return pd.to_datetime(year_s.astype(str) + "-" + month + "-01")

    # ── Loaders ───────────────────────────────────────────────────────────────

    def load_ipc(self) -> pd.DataFrame:
        """
        Carga IPC mensual del INE (Cataluña, índice general) y agrega a trimestral.
        Retorna: date, year, quarter, ipc_index_q  |  rango 2002Q1-2026Q1.
        NaN en años anteriores (distritos 2000-2001) es estructural.
        """
        raw = pd.read_csv(
            self.raw_path / "ipc_ine.csv",
            sep=";", encoding="latin-1", decimal=",",
        ).rename(columns={
            "Comunidades y Ciudades Autónomas": "region",
            "Grupos COICOP 2011": "group",
            "Tipo de dato": "data_type",
            "Periodo": "period",
            "Total": "ipc_index",
        })
        raw["year"]  = raw["period"].str[:4].astype(int)
        raw["month"] = raw["period"].str[-2:].astype(int)
        raw["date"]  = pd.to_datetime(
            raw["year"].astype(str) + "-" + raw["month"].astype(str) + "-01"
        )
        raw = raw[["date", "ipc_index", "year", "month"]].dropna(subset=["ipc_index"]).sort_values("date")
        raw["quarter"] = raw["date"].dt.quarter

        quarterly = (
            raw.groupby(["year", "quarter"], as_index=False)
            .agg(ipc_index_q=("ipc_index", "mean"))
        )
        quarterly["date"] = self._to_quarterly_date(quarterly["year"], quarterly["quarter"])
        return quarterly[["date", "year", "quarter", "ipc_index_q"]]

    def load_euribor(self) -> pd.DataFrame:
        """
        Carga Euribor 12M mensual del BDE y agrega a trimestral.
        Retorna: date, year, quarter, euribor_12m_q  |  rango 2000Q1-2025Q4.
        """
        raw = pd.read_csv(
            self.raw_path / "SeriesBIE[21].csv",
            sep=",", encoding="latin-1", skiprows=8,
            header=None, names=["period_str", "euribor_12m"],
        )
        raw["period_str"] = raw["period_str"].astype(str).str.strip().str.lower()
        raw = raw[
            raw["period_str"].str.match(
                r"^(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\d{2}$", na=False
            )
        ].copy()
        raw["euribor_12m"] = pd.to_numeric(raw["euribor_12m"], errors="coerce")
        raw = raw.dropna(subset=["euribor_12m"])

        raw["month"] = raw["period_str"].str[:3].map(self._MONTH_MAP)
        raw["year"]  = 2000 + raw["period_str"].str[3:5].astype(int)
        raw["date"]  = pd.to_datetime(raw["year"].astype(str) + "-" + raw["month"] + "-01")
        raw = raw[raw["date"] < "2026-01-01"].sort_values("date")
        raw["quarter"] = raw["date"].dt.quarter

        quarterly = (
            raw.groupby(["year", "quarter"], as_index=False)
            .agg(euribor_12m_q=("euribor_12m", "mean"))
        )
        quarterly["date"] = self._to_quarterly_date(quarterly["year"], quarterly["quarter"])
        return quarterly[["date", "year", "quarter", "euribor_12m_q"]]

    def load_ist(self) -> pd.DataFrame:
        """
        Carga IST Idescat por barrio-año con normalización Unicode y mapeo manual.
        Retorna: year, neighborhood_norm_matched, ist_index  |  rango 2015-2024.
        NaN fuera de rango es estructural.
        """
        raw = pd.read_csv(
            self.raw_path / "ist14058mun.csv",
            sep=";", encoding="utf-8-sig", decimal=",",
        ).rename(columns={
            "año": "year",
            "municipio": "municipality",
            "barrios de Barcelona": "neighborhood_name",
            "concepto": "concept",
            "estado": "status",
            "valor": "ist_index",
        })
        ist = raw[["year", "neighborhood_name", "ist_index"]].copy()
        ist["neighborhood_name_norm"] = ist["neighborhood_name"].apply(self._normalize)
        ist = ist[ist["neighborhood_name_norm"] != "total"]
        ist["neighborhood_norm_matched"] = ist["neighborhood_name_norm"].replace(self._IST_NAME_MAP)
        return ist[["year", "neighborhood_norm_matched", "ist_index"]]

    # ── Merge ────────────────────────────────────────────────────────────────

    def merge_into(self, panel: pd.DataFrame, include_ist: bool = False) -> pd.DataFrame:
        """
        Merge left de IPC y Euribor (e IST opcional) en el panel.
        Para IST requiere columna 'neighborhood' en panel.
        """
        df = panel.merge(self.load_ipc()[["date", "ipc_index_q"]], on="date", how="left")
        df = df.merge(self.load_euribor()[["date", "euribor_12m_q"]], on="date", how="left")

        if include_ist and "neighborhood" in df.columns:
            ist_df = self.load_ist()
            df["neighborhood_norm"] = df["neighborhood"].apply(self._normalize)
            df = df.merge(
                ist_df,
                left_on=["year", "neighborhood_norm"],
                right_on=["year", "neighborhood_norm_matched"],
                how="left",
            ).drop(columns=["neighborhood_norm", "neighborhood_norm_matched"], errors="ignore")

        return df
