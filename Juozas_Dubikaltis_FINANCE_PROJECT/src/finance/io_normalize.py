from __future__ import annotations
import pandas as pd

# Unified schema for the rest of the pipeline
UNIFIED_COLS = [
    "date",
    "amount",
    "currency",
    "description",
    "merchant",
    "iban",
    "balance",
    "type",
    "bank",
]


def _ensure_schema(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    """
    Take a partially-normalized frame and return a frame with the exact columns we need.
    """
    out = pd.DataFrame(index=df.index)

    out["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    out["amount"] = pd.to_numeric(df.get("amount"), errors="coerce")
    out["currency"] = df.get("currency", "EUR").astype(str)
    out["description"] = df.get("description", "").astype(str)
    out["merchant"] = df.get("merchant", "").astype(str)
    out["iban"] = df.get("iban", "").astype(str)
    out["balance"] = pd.to_numeric(df.get("balance"), errors="coerce")
    out["type"] = df.get("type", "").astype(str)
    out["bank"] = bank_name

    return out[UNIFIED_COLS]


# ---------------- Revolut ----------------

def _normalize_revolut(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize Revolut CSV exported from app/web.
    Expected columns (case-insensitive): Type, Product, Started Date,
    Completed Date, Description, Amount, Fee, Currency, State, Balance.
    """
    cols = {c: c.lower().strip() for c in raw.columns}
    df = raw.rename(columns=cols).copy()

    # Date: prefer completed date, fall back to started date
    if "completed date" in df.columns:
        date_series = df["completed date"]
    else:
        date_series = df.get("started date")

    df_norm = pd.DataFrame(index=df.index)
    df_norm["date"] = date_series

    df_norm["amount"] = df.get("amount")
    df_norm["currency"] = df.get("currency", "EUR")
    df_norm["description"] = df.get("description", "")
    # No separate merchant field, so use description as merchant too
    df_norm["merchant"] = df_norm["description"]
    df_norm["iban"] = ""  # Revolut CSV here has no IBAN per row
    df_norm["balance"] = df.get("balance")
    df_norm["type"] = df.get("type", "")

    return _ensure_schema(df_norm, bank_name="Revolut")


# ---------------- Swedbank ----------------

def _normalize_swedbank(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize Swedbank CSV.
    Example columns: 'Sąskaitos Nr.', 'Data', 'Gavėjas', 'Paaiškinimai',
    'Suma', 'Valiuta', 'D/K', 'Likutis' etc.
    """
    cmap: dict[str, str] = {}
    for c in raw.columns:
        lc = c.lower().strip()
        if lc == "data":
            cmap[c] = "date"
        elif lc == "suma":
            cmap[c] = "amount"
        elif lc == "valiuta":
            cmap[c] = "currency"
        elif lc in ("paaiškinimai", "paaiskinimai"):
            cmap[c] = "description"
        elif lc in ("gavėjas", "gavejas"):
            cmap[c] = "merchant"
        elif lc in ("d/k", "dk"):
            cmap[c] = "dk"
        elif lc in ("likutis", "balance"):
            cmap[c] = "balance"
        elif lc in ("sąskaitos nr.", "saskaitos nr.", "account number"):
            cmap[c] = "iban"

    df = raw.rename(columns=cmap).copy()

    # Parse amount, handle NBSP and comma decimal
    if "amount" in df.columns:
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace("\u00a0", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Apply D/K sign convention if present
    if "dk" in df.columns and "amount" in df.columns:
        sign = (
            df["dk"]
            .astype(str)
            .str.upper()
            .str.strip()
            .map(
                {
                    "D": -1,
                    "DEBETAS": -1,
                    "DEBIT": -1,
                    "K": 1,
                    "KREDITAS": 1,
                    "CREDIT": 1,
                }
            )
            .fillna(1)
        )
        df["amount"] = df["amount"] * sign

    df_norm = pd.DataFrame(index=df.index)
    df_norm["date"] = df.get("date")
    df_norm["amount"] = df.get("amount")
    df_norm["currency"] = df.get("currency", "EUR")
    df_norm["description"] = df.get("description", "")
    df_norm["merchant"] = df.get("merchant", df.get("description", ""))
    df_norm["iban"] = df.get("iban", "")
    df_norm["balance"] = df.get("balance")
    # crude type: credit if amount > 0, else debit
    df_norm["type"] = pd.Series(
        pd.NA, index=df.index, dtype="object"
    )
    if "amount" in df_norm.columns:
        df_norm.loc[df_norm["amount"] > 0, "type"] = "credit"
        df_norm.loc[df_norm["amount"] < 0, "type"] = "debit"

    return _ensure_schema(df_norm, bank_name="Swedbank")


# ---------------- bank detector + dispatcher ----------------

def _score(part: pd.DataFrame, alias_groups: list[list[str]]) -> int:
    """
    Score a chunk of rows by how many non-null entries it has for aliases.
    """
    lower_map = {c.lower(): c for c in part.columns}
    total = 0
    for aliases in alias_groups:
        for a in aliases:
            col = lower_map.get(a)
            if col is not None:
                total += part[col].notna().sum()
                break
    return total


def _decide_bank(part: pd.DataFrame) -> str:
    """
    Decide if this chunk looks like Revolut or Swedbank by column content.
    """
    revolut_aliases = [
        ["completed date", "started date"],
        ["type"],
        ["description"],
        ["amount"],
        ["currency"],
    ]
    swedbank_aliases = [
        ["data", "date"],
        ["suma"],
        ["valiuta", "currency"],
        ["d/k", "dk"],
        ["paaiškinimai", "paaiskinimai"],
    ]

    rev_score = _score(part, revolut_aliases)
    swe_score = _score(part, swedbank_aliases)
    return "revolut" if rev_score >= swe_score else "swedbank"


def normalize_any_bank(raw_all: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a concatenated DataFrame that may contain rows from multiple CSVs
    (Swedbank + Revolut). CsvSource has already added `_source_path`.
    """
    if raw_all.empty:
        return pd.DataFrame(columns=UNIFIED_COLS)

    frames: list[pd.DataFrame] = []

    if "_source_path" in raw_all.columns:
        for _, part in raw_all.groupby("_source_path"):
            bank = _decide_bank(part)
            if bank == "revolut":
                frames.append(_normalize_revolut(part))
            else:
                frames.append(_normalize_swedbank(part))
    else:
        bank = _decide_bank(raw_all)
        if bank == "revolut":
            frames.append(_normalize_revolut(raw_all))
        else:
            frames.append(_normalize_swedbank(raw_all))

    return pd.concat(frames, ignore_index=True)
