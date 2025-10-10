
import plotly.graph_objects as go
def plot_data(df, key: str, title: str, rating_key:str, 
              complementary_key=None, title_comp_key=None):
    """
    Plota uma métrica do DataFrame consolidado com cores por rating.
    
    df: DataFrame consolidado com colunas <key> e <key>_rating
    key: métrica que será plotada
    title: título do gráfico
    """
    # Preparar dados
    df_plot = df[[key, rating_key]].copy()
    if complementary_key:
        df_plot = df[[key, rating_key, complementary_key]].copy()
    df_plot['color'] = df_plot[rating_key].map({
        'Extreme Fear': 'darkred',
        'Fear': 'red',
        'Neutral': 'gold',
        'Greed': 'green',
        'Extreme Greed': 'darkgreen'
    })

    # Criar figura
    fig = go.Figure()

    # Linha contínua conectando os pontos
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot[key],
        name=title,
        mode='lines+markers',
        line=dict(color='lightgray', width=2),
        marker=dict(color=df_plot['color'], size=8),
        text=[f"{y:.2f} ({r})" for y, r in zip(df_plot[key], df_plot[rating_key])],
        hoverinfo='text+x'
    ))
    if complementary_key:
        fig.add_trace(go.Scatter(
            x=df_plot.index,
            y=df_plot[complementary_key],
            name=title_comp_key,
            mode='lines',
            line=dict(color='orange', width=4)
        ))

    # Layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Score',
        yaxis=dict(range=[df_plot[key].min() * 0.95, df_plot[key].max() * 1.05]),
        template='plotly_white'
    )

    fig.show()