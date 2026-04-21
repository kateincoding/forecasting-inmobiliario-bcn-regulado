"""
pipeline.py
Orquestador del ETL completo: Extract → Transform → Load.

Ejecución:
    python -m src.pipeline
"""

import time
from pathlib import Path

import pandas as pd

from src.config import PipelineConfig
from src.extract.incasol import IncasolExtractor
from src.transform.macrovars import MacroVarLoader
from src.transform.features import FeatureEngineer
from src.transform.clean import DataCleaner
from src.utils.nulls import NullValidator


class ETLPipeline:
    """
    Orquesta las tres fases del ETL y guarda los outputs.

    Uso:
        pipeline = ETLPipeline()                  # config por defecto
        results  = pipeline.run()
        # results["distritos"] → df_distritos_eda (1030 × 27)
        # results["barrios"]   → df_barrios_eda   (3102 × 28)

    Con config personalizada:
        config   = PipelineConfig(raw_path=Path("mi_ruta/data_raw"))
        pipeline = ETLPipeline(config=config)
        results  = pipeline.run()
    """

    def __init__(self, config: PipelineConfig | None = None):
        self.config    = config or PipelineConfig()
        self.extractor = IncasolExtractor(self.config)
        self.loader    = MacroVarLoader(self.config)
        self.cleaner   = DataCleaner(self.config)
        self.validator = NullValidator()

    # ── Fases públicas ────────────────────────────────────────────────────────

    def run(self) -> dict:
        """
        Ejecuta el pipeline completo.
        Retorna {"distritos": pd.DataFrame, "barrios": pd.DataFrame}.
        """
        t0 = time.time()
        print("=" * 50)
        print("ETL Pipeline — Alquiler Barcelona")
        print("=" * 50)

        barris_raw, district_raw = self._extract()
        self._save_interim(barris_raw, district_raw)

        districts_full, barrios_full = self._transform(barris_raw, district_raw)

        df_distritos, df_barrios = self._load(districts_full, barrios_full)
        self._save_cleaned(df_distritos, df_barrios)

        elapsed = round(time.time() - t0, 1)
        print(f"\nPipeline completado en {elapsed}s.")
        print(f"  df_distritos_eda : {df_distritos.shape}")
        print(f"  df_barrios_eda   : {df_barrios.shape}")
        print("=" * 50)

        return {"distritos": df_distritos, "barrios": df_barrios}

    # ── Fases internas ────────────────────────────────────────────────────────

    def _extract(self) -> tuple:
        print("\n[1/3] EXTRACT — leyendo Excel Incasol...")
        barris_raw   = self.extractor.extract_barris()
        district_raw = self.extractor.extract_districts()

        self.validator.validate_no_duplicates(
            barris_raw, ["neighborhood_code", "year", "quarter"], "barris"
        )
        self.validator.validate_no_duplicates(
            district_raw, ["district_code", "year", "quarter"], "districts"
        )
        print(f"  barris_raw:   {barris_raw.shape}")
        print(f"  district_raw: {district_raw.shape}")
        return barris_raw, district_raw

    def _transform(self, barris_raw: pd.DataFrame, district_raw: pd.DataFrame) -> tuple:
        print("\n[2/3] TRANSFORM — macrovariables + features...")

        def _run_pipeline(df_raw: pd.DataFrame, group_col: str, include_ist: bool) -> pd.DataFrame:
            df = self.loader.merge_into(
                FeatureEngineer(self.config)
                .fit(df_raw, group_col)
                .add_time_index()
                .transform(),
                include_ist=include_ist,
            )
            return (
                FeatureEngineer(self.config)
                .fit(df, group_col)
                .add_growth_features()
                .add_lag_features()
                .add_regulation_dummies()
                .add_real_prices()
                .add_real_yoy_growth()
                .add_period_labels()
                .transform()
            )

        districts_full = _run_pipeline(district_raw, "district_code",     include_ist=False)
        barrios_full   = _run_pipeline(barris_raw,   "neighborhood_code", include_ist=True)

        print(f"  districts_full: {districts_full.shape}")
        print(f"  barrios_full:   {barrios_full.shape}")
        return districts_full, barrios_full

    def _load(self, districts_full: pd.DataFrame, barrios_full: pd.DataFrame) -> tuple:
        print("\n[3/3] LOAD — filtros finales y tipado...")
        df_distritos = self.cleaner.clean_districts(districts_full)
        df_barrios   = self.cleaner.clean_barrios(barrios_full)

        self.validator.assert_within_thresholds(df_distritos, "distritos")
        self.validator.assert_within_thresholds(df_barrios,   "barrios")
        return df_distritos, df_barrios

    def _save_interim(self, barris_raw: pd.DataFrame, district_raw: pd.DataFrame) -> None:
        out = self.config.interim_path
        barris_raw.to_parquet(out / "rental_panel_barris.parquet",  index=False)
        district_raw.to_parquet(out / "district_panel.parquet", index=False)
        print(f"  Intermedios guardados en {out}/")

    def _save_cleaned(self, df_dist: pd.DataFrame, df_barrios: pd.DataFrame) -> None:
        out = self.config.cleaned_path
        df_dist.to_parquet(out / "df_distritos_eda.parquet", index=False)
        df_barrios.to_parquet(out / "df_barrios_eda.parquet",   index=False)
        print(f"  Outputs guardados en {out}/")


# ── Punto de entrada CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
