
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
MPL_CACHE_DIR = ROOT / ".matplotlib-cache"

MPL_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(MPL_CACHE_DIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns


def load_event_log() -> pd.DataFrame:
    event_files = sorted(DATA_DIR.glob("Procure-to-Pay*.csv"))
    events = []
    for file in event_files:
        df = pd.read_csv(file)
        df["Dataset"] = file.stem
        events.append(df)

    log = pd.concat(events, ignore_index=True)
    log.columns = log.columns.str.strip()
    log["Case"] = log["Dataset"] + " / " + log["Case ID"].astype(str)
    log["Start Timestamp"] = pd.to_datetime(log["Start Timestamp"], dayfirst=True)
    log["Complete Timestamp"] = pd.to_datetime(log["Complete Timestamp"], dayfirst=True)
    log["Activity"] = log["Activity"].str.strip()
    log["Event duration (minutes)"] = (
        log["Complete Timestamp"] - log["Start Timestamp"]
    ).dt.total_seconds() / 60
    return log.sort_values(["Case", "Start Timestamp", "Complete Timestamp"])


def add_case_metrics(log: pd.DataFrame) -> pd.DataFrame:
    log = log.copy()
    log["Next start"] = log.groupby("Case")["Start Timestamp"].shift(-1)
    log["Waiting time (hours)"] = (
        log["Next start"] - log["Complete Timestamp"]
    ).dt.total_seconds() / 3600

    case_metrics = (
        log.groupby("Case")
        .agg(
            Dataset=("Dataset", "first"),
            Country=("Country", "first"),
            Invoice_amount=("Invoice amount", "first"),
            Discount=("Discount", "first"),
            Start=("Start Timestamp", "min"),
            End=("Complete Timestamp", "max"),
            Events=("Activity", "size"),
            Activities=("Activity", "nunique"),
        )
        .reset_index()
    )
    case_metrics["Throughput time (days)"] = (
        case_metrics["End"] - case_metrics["Start"]
    ).dt.total_seconds() / 86400
    case_metrics["Discount rate"] = (
        case_metrics["Discount"] / case_metrics["Invoice_amount"]
    ).replace([float("inf"), -float("inf")], pd.NA)
    return case_metrics


def save_activity_frequency(log: pd.DataFrame, phases: pd.DataFrame) -> None:
    data = log.merge(phases, on="Activity", how="left")
    order = data["Activity"].value_counts().index
    plt.figure(figsize=(12, 8))
    sns.countplot(data=data, y="Activity", order=order, hue="Phase", dodge=False)
    plt.title("Activity frequency by process phase")
    plt.xlabel("Events")
    plt.ylabel("")
    plt.legend(title="Phase", loc="lower right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_activity_frequency_by_phase.png", dpi=200)
    plt.close()


def save_throughput_by_country(case_metrics: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 6))
    sns.boxplot(data=case_metrics, x="Country", y="Throughput time (days)")
    sns.stripplot(
        data=case_metrics,
        x="Country",
        y="Throughput time (days)",
        color="0.25",
        alpha=0.35,
        size=3,
    )
    plt.title("Case throughput time by country")
    plt.xlabel("")
    plt.ylabel("Days from first to last event")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_throughput_by_country.png", dpi=200)
    plt.close()


def save_bottlenecks(log: pd.DataFrame) -> None:
    waits = log.dropna(subset=["Waiting time (hours)"])
    waits = waits[waits["Waiting time (hours)"] >= 0]
    data = (
        waits.groupby("Activity")["Waiting time (hours)"]
        .median()
        .nlargest(12)
        .reset_index()
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(data=data, y="Activity", x="Waiting time (hours)", color="#4C78A8")
    plt.title("Likely bottlenecks: median waiting time after activity")
    plt.xlabel("Median waiting time until next event (hours)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "03_bottlenecks_waiting_time.png", dpi=200)
    plt.close()


def save_invoice_vs_throughput(case_metrics: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=case_metrics,
        x="Invoice_amount",
        y="Throughput time (days)",
        hue="Country",
        size="Discount rate",
        sizes=(25, 180),
        alpha=0.75,
    )
    plt.title("Case value, discount rate, and throughput time")
    plt.xlabel("Invoice amount")
    plt.ylabel("Throughput time (days)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "04_invoice_amount_vs_throughput.png", dpi=200)
    plt.close()


def save_top_variants(log: pd.DataFrame) -> None:
    variants = (
        log.groupby("Case")["Activity"]
        .agg(lambda activities: " -> ".join(activities))
        .value_counts()
        .head(10)
        .rename_axis("Variant")
        .reset_index(name="Cases")
    )
    variants["Variant label"] = [f"Variant {i}" for i in range(1, len(variants) + 1)]
    variants.to_csv(FIG_DIR / "top_variants.csv", index=False)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=variants, x="Cases", y="Variant label", color="#59A14F")
    plt.title("Top 10 process variants")
    plt.xlabel("Cases")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "05_top_variants.png", dpi=200)
    plt.close()


def save_directly_follows_graph(log: pd.DataFrame) -> None:
    transitions = log[["Case", "Activity"]].copy()
    transitions["Next activity"] = transitions.groupby("Case")["Activity"].shift(-1)
    transitions = transitions.dropna()
    top_edges = (
        transitions.groupby(["Activity", "Next activity"])
        .size()
        .nlargest(24)
        .reset_index(name="Frequency")
    )

    graph = nx.from_pandas_edgelist(
        top_edges,
        source="Activity",
        target="Next activity",
        edge_attr="Frequency",
        create_using=nx.DiGraph,
    )
    pos = nx.spring_layout(graph, seed=7, k=1.2)
    widths = [1 + graph[u][v]["Frequency"] / top_edges["Frequency"].max() * 5 for u, v in graph.edges]

    plt.figure(figsize=(14, 9))
    nx.draw_networkx_nodes(graph, pos, node_size=1800, node_color="#F2CF5B", edgecolors="#333333")
    nx.draw_networkx_edges(
        graph,
        pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=15,
        width=widths,
        edge_color="#666666",
        connectionstyle="arc3,rad=0.08",
    )
    nx.draw_networkx_labels(graph, pos, font_size=8)
    edge_labels = {(u, v): d["Frequency"] for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Directly-follows graph: most frequent transitions")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "06_directly_follows_graph.png", dpi=200)
    plt.close()


def write_summary(log: pd.DataFrame, case_metrics: pd.DataFrame) -> None:
    summary = pd.DataFrame(
        {
            "metric": [
                "events",
                "cases",
                "activities",
                "resources",
                "countries",
                "median_throughput_days",
                "mean_throughput_days",
            ],
            "value": [
                len(log),
                case_metrics["Case"].nunique(),
                log["Activity"].nunique(),
                log["Resource"].nunique(),
                log["Country"].nunique(),
                case_metrics["Throughput time (days)"].median(),
                case_metrics["Throughput time (days)"].mean(),
            ],
        }
    )
    summary.to_csv(FIG_DIR / "summary_metrics.csv", index=False)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    sns.set_theme(style="whitegrid", context="talk")

    phases = pd.read_csv(DATA_DIR / "Phases_of_activities.csv", sep=";", encoding="utf-8-sig")
    phases["Activity"] = phases["Activity"].str.strip()

    log = load_event_log()
    log["Next start"] = log.groupby("Case")["Start Timestamp"].shift(-1)
    log["Waiting time (hours)"] = (
        log["Next start"] - log["Complete Timestamp"]
    ).dt.total_seconds() / 3600
    case_metrics = add_case_metrics(log)

    save_activity_frequency(log, phases)
    save_throughput_by_country(case_metrics)
    save_bottlenecks(log)
    save_invoice_vs_throughput(case_metrics)
    save_top_variants(log)
    save_directly_follows_graph(log)
    write_summary(log, case_metrics)

    print(f"Wrote figures and CSV summaries to {FIG_DIR}")


if __name__ == "__main__":
    main()
