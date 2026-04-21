"""
config.py
Fuente única de verdad para paths, fechas regulatorias y parámetros del ETL.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PipelineConfig:
    # ── Paths ────────────────────────────────────────────────────────────────
    raw_path:     Path = field(default_factory=lambda: Path("data/data_raw"))
    interim_path: Path = field(default_factory=lambda: Path("data/data_interim"))
    cleaned_path: Path = field(default_factory=lambda: Path("data/data_cleaned"))

    # ── Fechas regulatorias ──────────────────────────────────────────────────
    reg_start:   str = "2020-10-01"   # Ley 11/2020 — inicio contención de rentas
    covid_start: str = "2020-03-01"   # Inicio shock COVID
    covid_end:   str = "2021-06-01"   # Fin período COVID
    tc_gap_start: str = "2022-04-01"  # TC anula Ley 11/2020 — inicio vacío regulatorio
    tc_gap_end:  str = "2023-07-01"   # Fin vacío TC
    ley12_start: str = "2023-07-01"   # Ley 12/2023 — nueva regulación estatal

    # ── Barrios excluidos (series demasiado escasas) ─────────────────────────
    barrios_excluidos: list = field(default_factory=lambda: [
        "Baró de Viver",
        "Can Peguera",
        "Canyelles",
        "Torre Baró",
        "Vallbona",
        "la Clota",
        "la Marina del Prat Vermell - AEI Zona Franca",
    ])

    # ── Rango temporal ───────────────────────────────────────────────────────
    barris_start_year:   int = 2014
    barris_end_year:     int = 2025
    district_start_year: int = 2000
    district_end_year:   int = 2025

    def __post_init__(self):
        self.raw_path     = Path(self.raw_path)
        self.interim_path = Path(self.interim_path)
        self.cleaned_path = Path(self.cleaned_path)
        self.interim_path.mkdir(parents=True, exist_ok=True)
        self.cleaned_path.mkdir(parents=True, exist_ok=True)
