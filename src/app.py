import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from matplotlib.ticker import FuncFormatter
from .utils import *

# Configurando o estilo dos gráficos
sns.set_theme(style="whitegrid")


def display_district_analysis(df, negotiation_type, distrito):

    """
    Exibe análises detalhadas sobre os imóveis de um distrito específico.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados dos imóveis.
        negotiation_type (str): Tipo de negociação ('sale' ou 'rent').
        distrito (str): Nome do distrito a ser analisado.

    Funções:
        - Exibe gráficos de distribuição de preços e preço médio por número de quartos.
        - Calcula e filtra os imóveis por custo por metro quadrado.
        - Fornece análises detalhadas, como custo médio por presença de piscina.

    Retorna:
        None. As análises e gráficos são exibidos diretamente na interface Streamlit.
    """

    st.title(f"Estatísticas por distrito: {distrito} ({negotiation_type.capitalize()})")

    # Filtrar os dados pelo distrito e tipo de negociação
    df_filtered = df[(df["Distrito"] == distrito) & (df["Tipo de Negociação"] == negotiation_type)]

    if df_filtered.empty:
        st.warning(f"Não há dados disponíveis para o distrito selecionado ({negotiation_type.capitalize()}).")
        return

    # Gráfico 1: Distribuição de Preços
    st.subheader("Distribuição de Preços")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_filtered["Preço"], kde=True, ax=ax, color="blue" if negotiation_type == "sale" else "green")
    ax.set_title(f"Distribuição de Preços no Distrito {distrito}")
    ax.set_xlabel("Preço (R$)")
    ax.set_ylabel("Frequência")
    st.pyplot(fig)

    # Gráfico 2: Preço Médio por Número de Quartos
    st.subheader("Preço Médio por Número de Quartos")
    media_preco_quartos = df_filtered.groupby("Quartos")["Preço"].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    media_preco_quartos.plot(kind="bar", color="skyblue", ax=ax)
    ax.set_title("Preço Médio por Número de Quartos")
    ax.set_xlabel("Número de Quartos")
    ax.set_ylabel("Preço Médio (R$)")
    ax.yaxis.set_major_formatter(FuncFormatter(format_price))
    st.pyplot(fig)


    # Custo por metro quadrado
    st.subheader(f"Custo por Metro Quadrado ({negotiation_type.capitalize()}) - Distrito: {distrito}")
    # Filtrar os dados pelo tipo de negociação e distrito
    df_filtered = df[(df["Tipo de Negociação"] == negotiation_type) & (df["Distrito"] == distrito)]

    if df_filtered.empty:
        st.warning("Não há dados disponíveis para o tipo de negociação e distrito selecionados.")
        return
    # Cálculo de custo por metro quadrado
    if "Tamanho" in df_filtered.columns and df_filtered["Tamanho"].notnull().all() and (df_filtered["Tamanho"] > 0).all():
        df_filtered["Custo por m²"] = (df_filtered["Preço"] / df_filtered["Tamanho"]).round(2)
    else:
        st.warning("A coluna 'Tamanho' está ausente, possui valores nulos ou contém valores inválidos. Não é possível calcular o custo por metro quadrado.")
        return
    # Filtros adicionais
    st.write("### Filtre o custo por metro quadrado por categoria")

    quartos = st.selectbox(
        "Quantidade de Quartos",
        options=["Todos"] + sorted(df_filtered["Quartos"].unique().tolist()),
        index=0
    )

    suites = st.selectbox(
        "Quantidade de Suítes",
        options=["Todos"] + sorted(df_filtered["Suítes"].unique().tolist()),
        index=0
    )

    piscina = st.selectbox(
        "Piscina",
        options=["Todos", "Com Piscina", "Sem Piscina"],
        index=0
    )

    vagas = st.selectbox(
        "Quantidade de Vagas",
        options=["Todos"] + sorted(df_filtered["Vagas"].unique().tolist()),
        index=0
    )
    # Aplicando os filtros adicionais
    if quartos != "Todos":
        df_filtered = df_filtered[df_filtered["Quartos"] == int(quartos)]
    if suites != "Todos":
        df_filtered = df_filtered[df_filtered["Suítes"] == int(suites)]
    if vagas != "Todos":
        df_filtered = df_filtered[df_filtered["Vagas"] == int(vagas)]

    if piscina == "Com Piscina":
        df_filtered = df_filtered[df_filtered["Piscina"] == 1]
    elif piscina == "Sem Piscina":
        df_filtered = df_filtered[df_filtered["Piscina"] == 0]
    # Exibindo os dados filtrados
    if not df_filtered.empty:
        st.write("### Resultado Filtrado")
        st.dataframe(df_filtered.style.format({"Custo por m²": "R$ {:.2f}", "Preço": "R$ {:.2f}"}))
    else:
        st.warning("Nenhum imóvel corresponde aos filtros selecionados.")


     # Custo médio por piscina
    st.subheader("Custo Médio por Presença de Piscina")
    # Calcular os valores médios para cada categoria
    media_preco_piscina = df_filtered.groupby("Piscina")["Preço"].mean()
    # Mapear os valores de 0 e 1 para uma descrição textual
    labels = {0: "Sem Piscina", 1: "Com Piscina"}
    # Exibir os resultados textualmente
    for piscina, preco_medio in media_preco_piscina.items():
        descricao = labels.get(piscina, "Desconhecido")
        st.write(f"**{descricao}:** R$ {preco_medio:,.2f}".replace(",", "."))



    

def display_map_by_district(df, negotiation_type, selected_district):
    """
    Exibe análises detalhadas sobre os imóveis de um distrito específico.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados dos imóveis.
        negotiation_type (str): Tipo de negociação ('sale' ou 'rent').
        distrito (str): Nome do distrito a ser analisado.

    Funções:
        - Exibe gráficos de distribuição de preços e preço médio por número de quartos.
        - Calcula e filtra os imóveis por custo por metro quadrado.
        - Fornece análises detalhadas, como custo médio por presença de piscina.

    Retorna:
        None. As análises e gráficos são exibidos diretamente na interface Streamlit.
    """

    st.subheader(f"Mapa de Imóveis no Distrito: {selected_district}")
    
    # Filtrar dados pelo distrito e tipo de negociação
    filtered_data = df[(df["Tipo de Negociação"] == negotiation_type) & (df["Distrito"] == selected_district)]
    
    if filtered_data.empty:
        st.warning("Não há imóveis disponíveis para o distrito selecionado.")
        return
    
    # Criar o mapa centrado no primeiro imóvel do distrito (ou coordenada padrão)
    default_lat, default_lon = filtered_data.iloc[0][["Latitude", "Longitude"]] if not filtered_data.empty else [-23.5505, -46.6333]
    m = folium.Map(location=[default_lat, default_lon], zoom_start=13)
    
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"R$ {row['Preço']:,.2f} - {row['Quartos']} Quartos",
        ).add_to(m)
    
    st_folium(m, width=800)




def main():
    """
        Função principal para execução do aplicativo Streamlit.

        Funções:
            - Configura o sidebar com filtros de tipo de negociação e distrito.
            - Divide o aplicativo em abas:
                - Aba 1: Análises estatísticas do distrito.
                - Aba 2: Mapa interativo dos imóveis.

        Retorna:
            None. O aplicativo é renderizado na interface do Streamlit.
        """
    
    st.sidebar.title("Filtre")
    st.sidebar.write("Selecione o tipo de negociação e o distrito para análise.")

    # Carregar os dados
    csv_path = "./imoveis-sao-paulo.csv"
    df = load_data(csv_path)

    # Selecionar o tipo de negociação
    negotiation_type = st.sidebar.radio("Selecione o Tipo de Negociação:", ["sale", "rent"])

    # Selecionar o distrito
    district_options = sorted(df["Distrito"].unique())
    selected_district = st.sidebar.selectbox("Selecione o Distrito:", district_options)

    # Criar as abas
    tab1, tab2 = st.tabs(["Estatísticas por Distrito", "Visualização do distrito no Mapa"])


    with tab1:
        # Código para exibir análises específicas para o distrito escolhido
        display_district_analysis(df, negotiation_type, selected_district)

    with tab2:
        # Código para exibir o mapa interativo
        display_map_by_district(df, negotiation_type, selected_district)
        