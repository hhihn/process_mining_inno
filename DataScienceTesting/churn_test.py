# test_churn.py
import pandas as pd

from churn import prepare_data, flag_excessive_listening


def test_prepare_data_keeps_churn_labels_matched_to_users():
    # Arrange
    users = pd.DataFrame({
        "user_id": ["user_2", "user_1"],
        "subscription_type": ["Free", "Premium"],
        "country": ["DE", "CA"],
        "avg_daily_minutes": [15.0, 90.0],
        "number_of_playlists": [1, 5],
        "top_genre": ["Pop", "Jazz"],
        "skips_per_day": [6, 2],
        "support_tickets": [2, 0],
        "days_since_last_login": [30, 1],
        "churned": [1, 0],
    })

    # Act
    X, y = prepare_data(users)

    # Assert
    assert y.to_dict() == {"user_2": 1, "user_1": 0}
    assert X.index.equals(y.index)

# Test just below, exactly at, and just above the 1,440-minute daily limit.
# The exact-limit case catches an off-by-one-style error: using >= would
# flag a user whose listening time is still valid.
def test_flags_users_only_when_listening_exceeds_24_hours():
    users = pd.DataFrame({
        "user_id": ["just_below", "at_limit", "just_above"],
        "avg_daily_minutes": [1439.9, 1440.0, 1440.1],
    })

    flagged_ids = flag_excessive_listening(users)

    assert set(flagged_ids) == {"just_above"}