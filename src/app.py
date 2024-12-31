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
    ax.yaxis.set_major_formatter(FuncFormatter(format_price))  # Aplica o formatador ao eixo Y
    st.pyplot(fig)


    # Custo por metro quadrado
    st.subheader("Análise de Custo por Metro Quadrado")
    # Filtrar dados pelo tipo de negociação
    if negotiation_type:
        df = df[df["Tipo de Negociação"] == negotiation_type]
    # Filtrar dados pelo distrito
    if distrito:
        df = df[df["Distrito"] == distrito]
    # Verificar se há dados após os filtros
    if df.empty:
        st.warning("Não há dados disponíveis para os filtros selecionados.")
        return
    # Adicionar coluna de custo por metro quadrado
    if "Tamanho" in df.columns and df["Tamanho"].notnull().all() and (df["Tamanho"] > 0).all():
        df["Custo por m²"] = (df["Preço"] / df["Tamanho"]).round(2)  # Arredondar para 2 casas decimais
    else:
        st.warning("A coluna 'Tamanho' está ausente, possui valores nulos ou contém valores inválidos. Não é possível calcular o custo por metro quadrado.")
        return
    # Ordenar os imóveis pelo custo por metro quadrado de forma ascendente
    df_sorted = df.sort_values(by="Custo por m²", ascending=True)
    st.dataframe(df_sorted.style.format({"Custo por m²": "R$ {:.2f}", "Preço": "R$ {:.2f}"}))
    
   
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
    st.sidebar.title("Filtros")
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
        