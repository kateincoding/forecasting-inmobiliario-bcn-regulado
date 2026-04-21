"""
utils/nulls.py
Validación y reporte de nulos en los paneles del ETL.
"""

import pandas as pd


class NullValidator:
    """
    Valida y reporta nulos en un DataFrame contra umbrales esperados.

    Uso:
        validator = NullValidator()
        validator.report(df_barrios, "barrios")
        validator.assert_within_thresholds(df_barrios, "barrios")
        validator.validate_no_duplicates(df, ["neighborhood_code", "year", "quarter"])
    """

    # Porcentajes de nulos aceptables por columna
    EXPECTED_NULL_PCT: dict = {
        "num_contracts":              0.0,
        "avg_rent":                   0.0,
        "avg_rent_m2":                0.0,
        "avg_surface":                0.0,
        "contract_growth_yoy":       10.0,   # primeros 4 trimestres por unidad
        "rent_growth_yoy":           10.0,
        "rent_m2_growth_yoy":        10.0,
        "contract_growth_qoq":        3.0,
        "rent_m2_lag1":               3.0,
        "rent_m2_lag4":              10.0,
        "ipc_index_q":               10.0,   # distritos pre-2002
        "avg_rent_real_2025base":    10.0,
        "avg_rent_m2_real_2025base": 10.0,
        "rent_real_growth_yoy":      12.0,
        "rent_m2_real_growth_yoy":   12.0,
        "euribor_12m_q":              0.0,
        "ist_index":                 30.0,   # IST solo 2015-2024
        "population_total":           0.0,
        "population_density_ha":      0.0,
    }

    def report(self, df: pd.DataFrame, label: str = "") -> pd.DataFrame:
        """
        Imprime y retorna un DataFrame con:
        columna | n_nulos | pct | esperado_max_% | ok
        """
        n = len(df)
        rows = []
        for col in df.columns:
            n_null   = int(df[col].isna().sum())
            pct      = round(n_null / n * 100, 2) if n > 0 else 0.0
            expected = self.EXPECTED_NULL_PCT.get(col)
            ok       = (pct <= expected) if expected is not None else None
            rows.append({"columna": col, "n_nulos": n_null, "pct": pct,
                         "esperado_max_%": expected, "ok": ok})

        report_df = pd.DataFrame(rows)
        header    = f"  NULL REPORT — {label} ({n} filas)  "
        print(f"\n{'='*len(header)}\n{header}\n{'='*len(header)}")
        print(report_df.to_string(index=False))

        failures = report_df[report_df["ok"] == False]
        if not failures.empty:
            print(f"\n[WARN] {len(failures)} columna(s) superan el umbral esperado:")
            print(failures[["columna", "pct", "esperado_max_%"]].to_string(index=False))

        return report_df

    def assert_within_thresholds(self, df: pd.DataFrame, label: str = "") -> None:
        """Lanza ValueError si alguna columna supera su umbral de nulos esperado."""
        n   = len(df)
        bad = []
        for col, max_pct in self.EXPECTED_NULL_PCT.items():
            if col not in df.columns:
                continue
            pct = df[col].isna().sum() / n * 100
            if pct > max_pct:
                bad.append(f"  {col}: {pct:.1f}% > {max_pct}%")
        if bad:
            tag = f"[{label}] " if label else ""
            raise ValueError(f"{tag}Columnas con demasiados nulos:\n" + "\n".join(bad))
        tag = f"[{label}] " if label else ""
        print(f"{tag}Validación de nulos OK.")

    def validate_no_duplicates(self, df: pd.DataFrame, key_cols: list, label: str = "") -> None:
        """Lanza AssertionError si hay duplicados en key_cols."""
        n_dup = df.duplicated(subset=key_cols).sum()
        tag   = f"[{label}] " if label else ""
        assert n_dup == 0, f"{tag}Se encontraron {n_dup} duplicados en {key_cols}"
        print(f"{tag}Sin duplicados en {key_cols}. OK")
