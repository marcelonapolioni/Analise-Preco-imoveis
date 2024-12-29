import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# Configurando o estilo dos gráficos
sns.set_theme(style="whitegrid")

# Função para carregar os dados
@st.cache_data
def load_data():
    # Substitua pelo caminho correto do arquivo
    df = pd.read_csv("imoveis-sao-paulo.csv")
    return df

def average_price_by_negotiation_and_district(df, negotiation_type, selected_district):
    st.subheader(f"Média de Preços por Distrito - {negotiation_type.capitalize()}")

    # Filtrar dados pelo tipo de negociação
    df_filtered = df[df["Tipo de Negociação"] == negotiation_type]

    # Se um distrito específico foi selecionado, filtrar por distrito
    if selected_district:
        df_filtered = df_filtered[df_filtered["Distrito"] == selected_district]

    # Calcular a média de preços por distrito
    avg_prices = df_filtered.groupby("Distrito")["Preço"].mean()

    # Verificar se há dados para exibir
    if avg_prices.empty:
        st.warning(f"Não há dados disponíveis para {negotiation_type} no distrito selecionado.")
        return

    # Gráfico de barras
    fig, ax = plt.subplots(figsize=(12, 8))
    avg_prices.plot(kind="bar", color="skyblue" if negotiation_type == "sale" else "orange", ax=ax)
    ax.set_title(f"Média de Preços - {negotiation_type.capitalize()} ({'Todos os Distritos' if not selected_district else selected_district})", fontsize=14)
    ax.set_xlabel("Distrito", fontsize=12)
    ax.set_ylabel("Preço Médio (R$)", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    st.pyplot(fig)


# Função para exibir análise por distrito
def display_district_analysis(df, negotiation_type, distrito):
    st.title(f"Análise de Imóveis no Distrito: {distrito} ({negotiation_type.capitalize()})")

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
    st.pyplot(fig)

    # Gráfico 3: Preço Médio por Presença de Piscina
    st.subheader("Preço Médio por Presença de Piscina")
    media_preco_piscina = df_filtered.groupby("Piscina")["Preço"].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    media_preco_piscina.plot(kind="bar", color=["red", "green"], ax=ax)
    ax.set_title("Preço Médio por Presença de Piscina")
    ax.set_xlabel("Piscina (0 = Não, 1 = Sim)")
    ax.set_ylabel("Preço Médio (R$)")
    st.pyplot(fig)



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



def bar_plot_correlation(df, negotiation_type):
    st.subheader(f"Principais Correlações - {negotiation_type.capitalize()}")
    
    df_filtered = df[df["Tipo de Negociação"] == negotiation_type]
    if df_filtered.empty:
        st.warning(f"Não há dados disponíveis para {negotiation_type}.")
        return
    
    # Selecionar apenas colunas numéricas
    numeric_columns = df_filtered.select_dtypes(include=["float64", "int64"])
    correlation_matrix = numeric_columns.corr()["Preço"].drop("Preço").sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    correlation_matrix.plot(kind="bar", color="skyblue", ax=ax)
    ax.set_title(f"Correlação com o Preço - {negotiation_type.capitalize()}")
    ax.set_ylabel("Correlação")
    st.pyplot(fig)


def main():
    st.sidebar.title("Filtros")
    st.sidebar.write("Selecione o tipo de negociação e o distrito para análise.")

    # Carregar os dados
    df = load_data()

    # Selecionar o tipo de negociação
    negotiation_type = st.sidebar.radio("Selecione o Tipo de Negociação:", ["sale", "rent"])

    # Selecionar o distrito
    district_options = sorted(df["Distrito"].unique())
    selected_district = st.sidebar.selectbox("Selecione o Distrito:", district_options)

    # Criar as abas
    tab1, tab2, tab3, tab4 = st.tabs(["Estatísticas Gerais", "Análises por Distrito", "Visualização no Mapa", "display_correlation_matrix_by_negotiation"])

    with tab1:
        st.header("Estatísticas Gerais")
        # Código para exibir estatísticas gerais (Ex: média de preços, variância, etc.)
        #display_advanced_statistics(df)

    with tab2:
        st.header(f"Análise de Imóveis no Distrito: {selected_district}")
        # Código para exibir análises específicas para o distrito escolhido
        display_district_analysis(df, negotiation_type, selected_district)

    with tab3:
        st.header("Visualização no Mapa")
        # Código para exibir o mapa interativo
        display_map_by_district(df, negotiation_type, selected_district)
    
    with tab4:
        st.header("Média de Preço por Distrito")
        # Código para exibir a matriz de correlação
        average_price_by_negotiation_and_district(df, negotiation_type, selected_district)


if __name__ == "__main__":
    main()


