import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

from .utils import load_data



def filter_df_by_district_and_negotiation(df: pd.DataFrame, distrito: str, negotiation_type: str) -> pd.DataFrame:
    """
    Filtra o DataFrame pelo distrito e tipo de negociação fornecidos.
    Retorna o DataFrame filtrado.
    """
    return df[(df["Distrito"] == distrito) & (df["Tipo de Negociação"] == negotiation_type)]


def calculate_custo_m2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verifica se é possível calcular a coluna 'Custo por m²'.
    Retorna o DataFrame com a nova coluna ou lança exceção se não for possível.
    """
    if (
        "Tamanho" not in df.columns
        or df["Tamanho"].isnull().any()
        or (df["Tamanho"] <= 0).any()
    ):
        raise ValueError("Coluna 'Tamanho' ausente, nula ou inválida. Impossível calcular Custo por m².")
    
    df["Custo por m²"] = (df["Preço"] / df["Tamanho"]).round(2)
    return df


def apply_additional_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lê filtros (Quartos, Suítes, Piscina, Vagas) do usuário via Streamlit
    e retorna o DataFrame filtrado.
    """
    # Quartos
    quartos = st.selectbox(
        "Quantidade de Quartos",
        options=["Todos"] + sorted(df["Quartos"].unique().tolist()),
        index=0
    )
    if quartos != "Todos":
        df = df[df["Quartos"] == int(quartos)]

    # Suítes
    suites = st.selectbox(
        "Quantidade de Suítes",
        options=["Todos"] + sorted(df["Suítes"].unique().tolist()),
        index=0
    )
    if suites != "Todos":
        df = df[df["Suítes"] == int(suites)]

    # Piscina
    piscina = st.selectbox(
        "Piscina",
        options=["Todos", "Com Piscina", "Sem Piscina"],
        index=0
    )
    if piscina == "Com Piscina":
        df = df[df["Piscina"] == 1]
    elif piscina == "Sem Piscina":
        df = df[df["Piscina"] == 0]

    # Vagas
    vagas = st.selectbox(
        "Quantidade de Vagas",
        options=["Todos"] + sorted(df["Vagas"].unique().tolist()),
        index=0
    )
    if vagas != "Todos":
        df = df[df["Vagas"] == int(vagas)]

    return df




def plot_distribution_prices(df: pd.DataFrame, distrito: str, negotiation_type: str):
    """
    Retorna um histograma de preços (Plotly) filtrado para um distrito específico.
    """
    color_map = "blue" if negotiation_type == "sale" else "green"
    fig_hist = px.histogram(
        df,
        x="Preço",
        nbins=30,
        title=f"Distribuição de Preços no Distrito {distrito}",
        color_discrete_sequence=[color_map],
    )
    fig_hist.update_xaxes(tickprefix="R$", tickformat=",.2f")
    fig_hist.update_layout(
        xaxis_title="Preço (R$)",
        yaxis_title="Frequência",
    )
    return fig_hist


def plot_mean_price_by_rooms(df: pd.DataFrame):
    """
    Retorna um gráfico de barras mostrando o preço médio por número de quartos (Plotly).
    """
    media_preco_quartos = df.groupby("Quartos")["Preço"].mean().reset_index()
    fig_bar = px.bar(
        media_preco_quartos,
        x="Quartos",
        y="Preço",
        color_discrete_sequence=["skyblue"],
        title="Preço Médio por Número de Quartos",
    )
    fig_bar.update_yaxes(tickprefix="R$", tickformat=",.2f")
    fig_bar.update_layout(
        xaxis_title="Número de Quartos",
        yaxis_title="Preço Médio (R$)",
    )
    return fig_bar


def plot_custo_medio_piscina(df: pd.DataFrame):
    """
    Retorna um gráfico de barras mostrando o custo médio (preço) por presença de piscina.
    """
    media_preco_piscina = df.groupby("Piscina")["Preço"].mean().reset_index()
    labels = {0: "Sem Piscina", 1: "Com Piscina"}
    media_preco_piscina["Piscina_Desc"] = media_preco_piscina["Piscina"].map(labels)

    fig_piscina = px.bar(
        media_preco_piscina,
        x="Piscina_Desc",
        y="Preço",
        color="Piscina_Desc",
        color_discrete_sequence=["tomato", "green"],
        title="Custo Médio por Presença de Piscina",
    )
    fig_piscina.update_yaxes(tickprefix="R$", tickformat=",.2f")
    fig_piscina.update_layout(
        xaxis_title="Piscina",
        yaxis_title="Preço Médio (R$)",
        showlegend=False
    )
    return fig_piscina


def plot_scatter_size_vs_price(df: pd.DataFrame):
    """
    Retorna um scatter plot (Tamanho vs Preço) colorido pelo número de quartos.
    """
    fig_scatter = px.scatter(
        df,
        x="Tamanho",
        y="Preço",
        color="Quartos",
        size="Quartos",
        hover_data=["Custo por m²", "Vagas", "Suítes"],
        title="Preço vs. Tamanho (Colorido por Número de Quartos)"
    )
    fig_scatter.update_xaxes(title="Tamanho (m²)")
    fig_scatter.update_yaxes(tickprefix="R$", tickformat=",.2f", title="Preço (R$)")
    return fig_scatter



def display_district_analysis(df: pd.DataFrame, negotiation_type: str, distrito: str):
    """
    Exibe análises detalhadas sobre os imóveis de um distrito específico, 
    usando Plotly para gráficos interativos.
    
    Funções:
        - Exibe gráficos (distribuição de preços, preço médio por quartos).
        - Calcula e filtra imóveis por custo por m².
        - Exibe custo médio por piscina e scatter (Tamanho vs Preço).

    Retorna:
        None. Exibe diretamente no Streamlit.
    """

    st.title(f"Estatísticas por distrito: {distrito} ({negotiation_type.capitalize()})")

    # Filtrar dados por distrito e tipo de negociação
    df_filtered = filter_df_by_district_and_negotiation(df, distrito, negotiation_type)
    if df_filtered.empty:
        st.warning(f"Não há dados disponíveis para o distrito selecionado ({negotiation_type.capitalize()}).")
        return

    # Plot 1: Distribuição de Preços
    st.subheader("Distribuição de Preços")
    fig_hist = plot_distribution_prices(df_filtered, distrito, negotiation_type)
    st.plotly_chart(fig_hist, use_container_width=True)

    #  Plot 2: Preço Médio por Número de Quartos
    st.subheader("Preço Médio por Número de Quartos")
    fig_bar = plot_mean_price_by_rooms(df_filtered)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Custo por Metro Quadrado
    st.subheader(f"Custo por Metro Quadrado ({negotiation_type.capitalize()}) - Distrito: {distrito}")

    # Tentar calcular custo m2
    try:
        df_filtered = calculate_custo_m2(df_filtered.copy())
    except ValueError as e:
        st.warning(str(e))
        return

    st.write("### Filtre o custo por metro quadrado por categoria")
    df_filtered = apply_additional_filters(df_filtered)

    if df_filtered.empty:
        st.warning("Nenhum imóvel corresponde aos filtros selecionados.")
        return

    st.write("### Resultado Filtrado")
    st.dataframe(
        df_filtered.style.format({
            "Custo por m²": "R$ {:.2f}",
            "Preço": "R$ {:.2f}"
        })
    )

    # 5) Custo Médio por Piscina
    st.subheader("Custo Médio por Presença de Piscina")
    fig_piscina = plot_custo_medio_piscina(df_filtered)
    st.plotly_chart(fig_piscina, use_container_width=True)

    # Scatter Plot (Tamanho vs Preço)
    st.subheader("Relação entre Tamanho e Preço")
    st.write("Este gráfico exemplifica como o tamanho do imóvel (m²) se relaciona com o preço.")

    fig_scatter = plot_scatter_size_vs_price(df_filtered)
    st.plotly_chart(fig_scatter, use_container_width=True)


def display_district_ranking(df: pd.DataFrame, negotiation_type: str):
    """
    Exibe um ranking geral dos distritos (para o tipo de negociação selecionado) por:
     - Custo médio por m²
     - Quantidade de imóveis com piscina
    """
    st.title(f"Ranking dos Distritos - Visão Geral ({negotiation_type.capitalize()})")

    # Filtrar dados pelo tipo de negociação
    filtered_df = df[df["Tipo de Negociação"] == negotiation_type].copy()
    if filtered_df.empty:
        st.warning(f"Não há dados para o tipo de negociação selecionado ({negotiation_type}).")
        return

    # Filtrar para remover imóveis sem tamanho válido
    filtered_df = filtered_df[filtered_df["Tamanho"] > 0].copy()
    if filtered_df.empty:
        st.warning("Não há dados válidos (Tamanho > 0) para calcular o Ranking.")
        return

    # Calcular Custo por m²
    filtered_df["Custo por m²"] = filtered_df["Preço"] / filtered_df["Tamanho"]

    # 4) Agrupar pelo distrito
    group = filtered_df.groupby("Distrito")

    # Ranking de custo médio por m²
    ranking_custo = (
        group["Custo por m²"]
        .mean()
        .reset_index(name="Custo médio por m²")
        .sort_values("Custo médio por m²", ascending=False)
    )

    st.subheader("Ranking de Distritos por Custo Médio (R$/m²) - Mais caros")
    st.dataframe(ranking_custo.head(5).style.format({"Custo médio por m²": "R$ {:.2f}"}))

    st.subheader("Ranking de Distritos por Custo Médio (R$/m²) - Mais baratos")
    st.dataframe(ranking_custo.tail(5).style.format({"Custo médio por m²": "R$ {:.2f}"}))

    st.markdown("---")

    # Ranking por quantidade de imóveis com piscina
    ranking_piscina = (
        group["Piscina"]
        .sum()
        .reset_index(name="Total de imóveis com piscina")
        .sort_values("Total de imóveis com piscina", ascending=False)
    )

    st.subheader("Distritos com Maior Número de Imóveis com Piscina")
    st.dataframe(ranking_piscina.head(5))

    st.subheader("Distritos com Menor Número de Imóveis com Piscina")
    st.dataframe(ranking_piscina.tail(5))



def display_map_by_district(df: pd.DataFrame, negotiation_type: str, selected_district: str):
    """
    Exibe um mapa com os imóveis de determinado distrito, usando Folium.
    """
    st.subheader(f"Mapa de Imóveis no Distrito: {selected_district}")
    
    filtered_data = filter_df_by_district_and_negotiation(df, selected_district, negotiation_type)
    
    if filtered_data.empty:
        st.warning("Não há imóveis disponíveis para o distrito selecionado.")
        return

    # Criar o mapa centrado no primeiro imóvel (ou coordenada padrão)
    default_lat, default_lon = filtered_data.iloc[0][["Latitude", "Longitude"]] if not filtered_data.empty else [-23.5505, -46.6333]
    m = folium.Map(location=[default_lat, default_lon], zoom_start=13)

    # Se quiser agrupar marcadores, descomente:
    # marker_cluster = MarkerCluster().add_to(m)

    for _, row in filtered_data.iterrows():
        # Ícone condicional para cada imóvel
        if row["Piscina"] == 1:
            icon = folium.Icon(color="orange", icon="swimmer", prefix="fa")
        elif row["Vagas"] > 1:
            icon = folium.Icon(color="purple", icon="car", prefix="fa")
        elif row["Suítes"] > 0:
            icon = folium.Icon(color="blue", icon="bed", prefix="fa")
        else:
            icon = folium.Icon(color="gray", icon="info-circle", prefix="fa")

        # Marcador com popup
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(
                f"R$ {row['Preço']:,.2f}<br>"
                f"{row['Quartos']} Quartos<br>"
                f"{'Com piscina' if row['Piscina'] == 1 else 'Sem Piscina'}<br>"
                f"Suítes: {row['Suítes']}<br>"
                f"Vagas: {row['Vagas']}"
            ),
            icon=icon
        ).add_to(m)

    st_folium(m, width=800)



def main():
    """
    Função principal para execução do aplicativo Streamlit.

    - Configura o sidebar com filtros de tipo de negociação e distrito.
    - Cria abas para:
        1) Análises estatísticas por distrito.
        2) Mapa interativo dos imóveis.

    Retorna:
        None (o aplicativo é renderizado via Streamlit).
    """
    st.sidebar.title("Filtre")
    st.sidebar.write("Selecione o tipo de negociação e o distrito para análise.")

    # Carregar os dados (ajuste o caminho conforme sua estrutura)
    csv_path = "./imoveis-sao-paulo.csv"
    df = load_data(csv_path)  # Supondo que você tenha essa função em algum lugar

    # Selecionar o tipo de negociação
    negotiation_type = st.sidebar.radio("Selecione o Tipo de Negociação:", ["sale", "rent"])

    # Selecionar o distrito
    district_options = sorted(df["Distrito"].unique())
    selected_district = st.sidebar.selectbox("Selecione o Distrito:", district_options)

    # Criar as abas
    tab1, tab2, tab3 = st.tabs(["Estatísticas por Distrito", "Visualização do distrito no Mapa", "Ranking dos Distritos"])

    with tab1:
        display_district_analysis(df, negotiation_type, selected_district)

    with tab2:
        display_map_by_district(df, negotiation_type, selected_district)

    with tab3:
        display_district_ranking(df, negotiation_type)

    