import io

import pandas as pd


def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def _strip_tz(df: pd.DataFrame) -> pd.DataFrame:
    """Strip timezone from all datetime columns — Excel doesn't support tz-aware datetimes."""
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_convert(None)
    return df


def to_excel(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            _strip_tz(df).to_excel(writer, sheet_name=safe_name, index=False)
            ws = writer.sheets[safe_name]
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max() if not df.empty else 0,
                    len(str(col))
                ) + 2
                ws.set_column(i, i, min(max_len, 60))
    return buf.getvalue()


def download_csv_button(st_obj, df: pd.DataFrame, filename: str, label: str = "⬇️ CSV"):
    st_obj.download_button(
        label=label,
        data=to_csv(df),
        file_name=filename,
        mime="text/csv",
        width="stretch",
    )


def download_excel_button(st_obj, sheets: dict[str, pd.DataFrame], filename: str, label: str = "⬇️ Excel"):
    st_obj.download_button(
        label=label,
        data=to_excel(sheets),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
