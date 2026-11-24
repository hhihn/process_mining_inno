from typing import Any

import pandas as pd
from pandas import DataFrame


def prepare_data(df: pd.DataFrame) -> tuple[DataFrame, Any]:
    users = df.set_index("user_id")
    return users.drop(columns="churned"), users["churned"]

def flag_excessive_listening(users: pd.DataFrame) -> list[str]:
    """Return the user IDs whose avg_daily_minutes exceeds 1,440."""
    raise NotImplementedError