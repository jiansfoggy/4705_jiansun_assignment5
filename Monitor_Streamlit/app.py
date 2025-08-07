import json,os
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import accuracy_score, precision_score

# 1. Load Logs
def load_logs(log_path):
    """
    Input:  UTF-8 encoded prediction_logs.json
    Output: 2 lists, request_texts and predicted_sentiments
    """
    texts, preds, true_sent = [], [], []
    try:
        with open(log_path, 'r') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    texts.append(obj.get("request_text", ""))
                    preds.append(obj.get("predicted_sentiment", ""))
                    true_sent.append(obj.get("true_sentiment", "").capitalize())
                except json.JSONDecodeError:
                    continue
        return texts, preds, true_sent
    except FileNotFoundError:
        st.error(f"Log file not found at {log_path}")
        st.stop()

# 2. Load IMDB movie data
def log_imdb(path):
    if path.exists():
        imdb = pd.read_csv(path)
        st.write(f"Loaded {len(imdb)} IMDB reviews")
    else:
        st.error(f"IMDB dataset not found at {path}")
        st.stop()
    
    return imdb

def main():
    st.set_page_config(layout="wide")
    st.title("Monitor Dashboard -- Objective Movie Review Sentiment Analyzer")
    st.text("This app monitors the running status of Objective Movie Review Sentiment Analyzer, a FastAPI.")

    imdb_path = Path("./IMDB_Dataset.csv")
    log_path = Path("./logs/prediction_logs.json")

    # 3. Load the Log and IMDB data
    st.header("1. Loading Log and IMDB Data")
    texts, preds, true_sent = load_logs(log_path)
    st.write(f"Loaded {len(texts)} log entries")
    text_len = [len(t) for t in texts]
    text_len = sorted(text_len)
    st.write(f"Sample lengths from logs:\n{text_len[:5]}")
    st.write(f"Sample predictions from logs:\n{preds[:5]}")

    imdb = log_imdb(imdb_path)
    imdb_len = [len(str(t)) for t in imdb["review"]]
    gts  = imdb["sentiment"].tolist()
    st.write(f"Sample lengths from IMDB:\n{imdb_len[:5]}")
    st.write(f"Sample predictions from IMDB:\n{gts[:5]}")
    
    # 4. Compare the distribution of sentence lengths from both Log and IMDB data
    st.header("2. Data Drift Analysis -- Review Lengths: IMDB vs. Log Requests")
    len_im = pd.DataFrame({
        "imdb_length": imdb_len
        })
    len_te = pd.DataFrame({
        "test_length": text_len
        })

    fig_imdb = px.histogram(
        len_im,
        x="imdb_length",
        nbins=25,
        histnorm="density",
        opacity=0.75,
        labels={"imdb_length": "Sentence Length"},
        title="IMDB Review Length"
        )
    
    lo = len_te['test_length'].min()
    hi = len_te['test_length'].max()
    bin_size = (hi - lo) / 25
    fig_test = px.histogram(
        len_te,
        x="test_length",
        # nbins=10,
        histnorm="density",
        opacity=0.75,
        labels={"test_length": "Sentence Length"},
        title="Logged Request Text Length"
        )

    fig_test.update_traces(xbins=dict(
        start=lo,
        end=hi,
        size=bin_size
    ))

    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("IMDB Review Length", "Request Text Length"),
        shared_yaxes=False
        )

    for trace in fig_imdb.data:
        fig1.add_trace(trace, row=1, col=1)

    for trace in fig_test.data:
        fig1.add_trace(trace, row=1, col=2)

    fig1.update_layout(height=450, width=800, showlegend=False,
        title_text="Histograms of Sentence Lengths: IMDB Review vs Logged Request Text",
        template="plotly_white"
        )

    st.plotly_chart(fig1, use_container_width=True)
   
    # 5. Bar chart of sentiment distributions
    st.header("3. Target Drift Analysis -- Sentiment Distribution: IMDB vs. Log Requests")
    # IMDB dataset has a 'sentiment' column with values 'positive'/'negative'
    imdb_counts = imdb["sentiment"].value_counts().reset_index()
    imdb_counts.columns = ["sentiment", "count"]
    imdb_counts["source"] = "IMDB"

    log_counts = pd.Series(preds).value_counts().reset_index()
    log_counts.columns = ["sentiment", "count"]
    log_counts["source"] = "Logs"

    fig2 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("IMDB Sentiment Counts", "Logged Sentiment Counts"),
        shared_yaxes=False
        )

    # Add IMDB bar chart in column 1
    fig2.add_trace(
        go.Bar(
            x=imdb_counts["sentiment"],
            y=imdb_counts["count"],
            name="IMDB"
            ),
        row=1, col=1
        )

    # Add Logs bar chart in column 2
    fig2.add_trace(
        go.Bar(
            x=log_counts["sentiment"],
            y=log_counts["count"],
            name="Logs",
            marker_color='orange'
            ),
        row=1, col=2
        )
    
    fig2.update_layout(
        title="IMDB vs. Logs Sentiment Counts",
        showlegend=True, width=800, height=400,
        template="plotly_white"
        )

    fig2.update_yaxes(title_text="Count", row=1, col=1)
    fig2.update_yaxes(title_text="Count", row=1, col=2)

    # bar_df = pd.concat([imdb_counts, log_counts], ignore_index=True)
    # fig2 = px.bar(
    #     bar_df,
    #     x="sentiment",
    #     y="count",
    #     color="source",
    #     barmode="group",
    #     title="IMDB vs. Logs Sentiment Counts"
    #     )
    # # disable shared y-axis so each subplot scales independently
    # fig2.update_yaxes(matches=None)
    st.plotly_chart(fig2, use_container_width=True)

    # 6. Model Accuracy & User Feedback:
    st.header("4. Model Accuracy & User Feedback -- Compute the Accuracy and Precision for Log Requests")
    preds, true_sent
    accuracy = accuracy_score(true_sent, preds)
    precision = precision_score(true_sent, preds, average="macro", zero_division=0)
    
    if accuracy < 0.80:
        st.error(f"Model accuracy {accuracy:.2%} already drops below 80%: ")

    st.metric("Accuracy", f"{accuracy:.2%}")
    st.metric("Precision (macro)", f"{precision:.2%}")

if __name__ == "__main__":
    main()
