import pandas as pd
from typing import Dict, Any


def analyze_engagement_csv(file_path: str) -> Dict[str, Any]:
    """
    Analyze engagement data from social media posts.

    Expected CSV format:
    platform,time,likes,comments,shares

    Example row:
    twitter,18:00,120,15,9
    """

    df = pd.read_csv(file_path)

    required = ["platform", "time", "likes", "comments", "shares"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Total engagement score
    df["engagement"] = df["likes"] + df["comments"] + df["shares"]

    # Best posting time
    best_time = (
        df.groupby("time")["engagement"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    # Best platform
    best_platform = (
        df.groupby("platform")["engagement"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    # Platform stats
    platform_stats = (
        df.groupby("platform")["engagement"]
        .mean()
        .sort_values(ascending=False)
        .to_dict()
    )

    return {
        "total_posts": int(len(df)),
        "average_engagement": float(df["engagement"].mean()),
        "best_posting_time": best_time,
        "best_platform": best_platform,
        "platform_performance": platform_stats,
    }