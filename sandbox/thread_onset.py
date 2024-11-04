
import plotly.express as px
import pandas as pd

def process(case, features):
    df = pd.DataFrame({feature: [getattr(case.metrics, feature)[n-1][n] for n in range(1, len(case.messages))] for feature in features})
    fig = px.line(df)
    for n, label in enumerate(case.labels):
        fig.add_hrect(x0=n, x1=n + 1, line_width=0, fillcolor=nth_color[label], opacity=0.2)
    fig.show()

    df['label'] = case.labels
    df['next_label'] = df['label'].shifted(1)
    true = df.loc[df['label'] != df['next_label']]
    false = df.loc[df['label'] == df['next_label']]

    fig = px.histogram(true)
    fig.show()

    fig = px.histogram(false)
    fig.show()
