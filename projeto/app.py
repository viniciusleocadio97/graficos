# -*- coding: utf-8 -*-
"""
Aplicação Dash - Análise Exploratória de E-commerce (Moda)
Recria, de forma interativa, os gráficos produzidos na análise em notebook:
 1. Histograma de Preços
 2. Dispersão Preço x Nota (por Gênero)
 3. Mapa de Calor de Correlação
 4. Barra - Top 10 Marcas
 5. Pizza - Proporção por Gênero
 6. Densidade (KDE) da Nota
 7. Regressão Preço x Desconto

Para rodar localmente:
    pip install dash pandas plotly statsmodels
    python app.py
Depois acesse o link exibido no terminal (geralmente http://127.0.0.1:8050)
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from dash import Dash, dcc, html, Input, Output

# ---------------------------------------------------------------------------
# 1. Leitura e preparo dos dados
# ---------------------------------------------------------------------------
df = pd.read_csv("ecommerce_estatistica.csv")


def qtd_para_numero(valor):
    valor = str(valor).replace("+", "").strip()
    if "mil" in valor:
        return float(valor.replace("mil", "")) * 1000
    return float(valor)


df["Qtd_Vendidos_Num"] = df["Qtd_Vendidos"].apply(qtd_para_numero)

GENEROS_PRINCIPAIS = ["Masculino", "Feminino", "Sem gênero", "Meninos", "Meninas"]
COLUNAS_NUMERICAS = ["Nota", "N_Avaliações", "Desconto", "Preço", "Qtd_Vendidos_Num"]

CORES = px.colors.qualitative.Set2

# ---------------------------------------------------------------------------
# 2. Funções que constroem cada gráfico (Plotly)
# ---------------------------------------------------------------------------

def fig_histograma(dataframe):
    fig = px.histogram(
        dataframe, x="Preço", nbins=25,
        color_discrete_sequence=["#4C72B0"],
        title="Distribuição de Preços dos Produtos",
        labels={"Preço": "Preço (R$)"},
    )
    fig.update_layout(yaxis_title="Quantidade de Produtos", bargap=0.05)
    return fig


def fig_dispersao(dataframe):
    d = dataframe[dataframe["Gênero"].isin(GENEROS_PRINCIPAIS)]
    fig = px.scatter(
        d, x="Preço", y="Nota", color="Gênero",
        opacity=0.75, color_discrete_sequence=CORES,
        title="Relação entre Preço e Nota dos Produtos",
        labels={"Preço": "Preço (R$)", "Nota": "Nota (0 a 5)"},
        hover_data=["Título", "Marca"],
    )
    return fig


def fig_mapa_calor(dataframe):
    corr = dataframe[COLUNAS_NUMERICAS].corr().round(2)
    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, aspect="auto",
        title="Mapa de Calor - Correlação entre Variáveis Numéricas",
    )
    return fig


def fig_barra(dataframe, top_n=10):
    top_marcas = dataframe["Marca"].value_counts().head(top_n).sort_values()
    fig = px.bar(
        x=top_marcas.values, y=top_marcas.index, orientation="h",
        color=top_marcas.index, color_discrete_sequence=px.colors.sequential.Viridis,
        title=f"Top {top_n} Marcas com Mais Produtos no Catálogo",
        labels={"x": "Quantidade de Produtos", "y": "Marca"},
    )
    fig.update_layout(showlegend=False)
    return fig


def fig_pizza(dataframe):
    genero_counts = dataframe["Gênero"].value_counts()
    top_generos = genero_counts.head(4)
    outros = genero_counts.iloc[4:].sum()
    genero_pizza = pd.concat([top_generos, pd.Series({"Outros": outros})])
    fig = px.pie(
        values=genero_pizza.values, names=genero_pizza.index,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Proporção de Produtos por Gênero",
        hole=0,
    )
    fig.update_traces(textinfo="percent+label")
    return fig


def fig_densidade(dataframe):
    notas = dataframe["Nota"].dropna()
    if len(notas) < 2 or notas.nunique() < 2:
        # dados insuficientes para estimar densidade (evita erro do gaussian_kde)
        fig = px.histogram(notas, x="Nota" if isinstance(notas, pd.DataFrame) else None)
        fig.update_layout(title="Densidade de Distribuição das Notas dos Produtos")
        return fig

    kde = gaussian_kde(notas)
    x_vals = np.linspace(notas.min() - 0.3, notas.max() + 0.3, 200)
    y_vals = kde(x_vals)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_vals, y=y_vals, mode="lines", fill="tozeroy",
            line=dict(color="#DD8452", width=2),
            name="Nota",
        )
    )
    fig.update_layout(
        title="Densidade de Distribuição das Notas dos Produtos",
        xaxis_title="Nota (0 a 5)", yaxis_title="Densidade",
    )
    return fig


def fig_regressao(dataframe):
    fig = px.scatter(
        dataframe, x="Preço", y="Desconto", trendline="ols",
        opacity=0.5, color_discrete_sequence=["#4C72B0"],
        title="Relação entre Preço e Desconto Aplicado (com Linha de Regressão)",
        labels={"Preço": "Preço (R$)", "Desconto": "Desconto (%)"},
    )
    fig.data[1].line.color = "red"
    return fig


# ---------------------------------------------------------------------------
# 3. Layout do aplicativo
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Análise de E-commerce - Dashboard"
server = app.server  # necessário para deploy (ex.: gunicorn / render / heroku)

generos_disponiveis = sorted(df["Gênero"].dropna().unique().tolist())

CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "10px",
    "padding": "16px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
    "marginBottom": "24px",
}

app.layout = html.Div(
    style={"backgroundColor": "#f4f6f9", "fontFamily": "Segoe UI, Arial, sans-serif", "padding": "24px"},
    children=[
        html.Div(
            [
                html.H1("📊 Dashboard de Análise de E-commerce (Moda)", style={"marginBottom": "4px"}),
                html.P(
                    "Explore os gráficos da análise exploratória de forma interativa. "
                    "Use o filtro de gênero abaixo para atualizar os gráficos.",
                    style={"color": "#555"},
                ),
            ],
            style={"marginBottom": "16px"},
        ),

        # Filtro global
        html.Div(
            [
                html.Label("Filtrar por Gênero:", style={"fontWeight": "bold", "marginRight": "12px"}),
                dcc.Dropdown(
                    id="filtro-genero",
                    options=[{"label": g, "value": g} for g in generos_disponiveis],
                    value=generos_disponiveis,
                    multi=True,
                    placeholder="Selecione um ou mais gêneros...",
                    style={"width": "100%"},
                ),
            ],
            style=CARD_STYLE,
        ),

        # Indicadores (KPIs)
        html.Div(id="kpis", style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

        # Linha 1: Histograma + Dispersão
        html.Div(
            [
                html.Div(dcc.Graph(id="grafico-histograma"), style={**CARD_STYLE, "flex": 1}),
                html.Div(dcc.Graph(id="grafico-dispersao"), style={**CARD_STYLE, "flex": 1}),
            ],
            style={"display": "flex", "gap": "16px"},
        ),

        # Linha 2: Mapa de calor + Barra
        html.Div(
            [
                html.Div(dcc.Graph(id="grafico-mapa-calor"), style={**CARD_STYLE, "flex": 1}),
                html.Div(dcc.Graph(id="grafico-barra"), style={**CARD_STYLE, "flex": 1}),
            ],
            style={"display": "flex", "gap": "16px"},
        ),

        # Linha 3: Pizza + Densidade
        html.Div(
            [
                html.Div(dcc.Graph(id="grafico-pizza"), style={**CARD_STYLE, "flex": 1}),
                html.Div(dcc.Graph(id="grafico-densidade"), style={**CARD_STYLE, "flex": 1}),
            ],
            style={"display": "flex", "gap": "16px"},
        ),

        # Linha 4: Regressão
        html.Div(
            [html.Div(dcc.Graph(id="grafico-regressao"), style={**CARD_STYLE, "flex": 1})],
            style={"display": "flex", "gap": "16px"},
        ),

        html.Div(
            "Fonte dos dados: ecommerce_estatistica.csv",
            style={"textAlign": "center", "color": "#999", "marginTop": "12px", "fontSize": "12px"},
        ),
    ],
)


# ---------------------------------------------------------------------------
# 4. Callbacks (interatividade)
# ---------------------------------------------------------------------------
@app.callback(
    Output("kpis", "children"),
    Output("grafico-histograma", "figure"),
    Output("grafico-dispersao", "figure"),
    Output("grafico-mapa-calor", "figure"),
    Output("grafico-barra", "figure"),
    Output("grafico-pizza", "figure"),
    Output("grafico-densidade", "figure"),
    Output("grafico-regressao", "figure"),
    Input("filtro-genero", "value"),
)
def atualizar_dashboard(generos_selecionados):
    if not generos_selecionados:
        d = df.copy()
    else:
        d = df[df["Gênero"].isin(generos_selecionados)]

    if d.empty:
        d = df.copy()

    def kpi(titulo, valor):
        return html.Div(
            [
                html.Div(titulo, style={"fontSize": "13px", "color": "#777"}),
                html.Div(valor, style={"fontSize": "24px", "fontWeight": "bold", "color": "#2c3e50"}),
            ],
            style={**CARD_STYLE, "flex": 1, "textAlign": "center", "marginBottom": 0},
        )

    kpis = [
        kpi("Produtos", f"{len(d)}"),
        kpi("Preço Médio", f"R$ {d['Preço'].mean():.2f}"),
        kpi("Nota Média", f"{d['Nota'].mean():.2f} ⭐"),
        kpi("Desconto Médio", f"{d['Desconto'].mean():.1f}%"),
    ]

    return (
        kpis,
        fig_histograma(d),
        fig_dispersao(d),
        fig_mapa_calor(d),
        fig_barra(d),
        fig_pizza(d),
        fig_densidade(d),
        fig_regressao(d),
    )


# ---------------------------------------------------------------------------
# 5. Execução
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
