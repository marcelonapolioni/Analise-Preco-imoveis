import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configurando o estilo dos gráficos
sns.set_theme(style="whitegrid")

# Função para carregar os dados
@st.cache_data
def load_data():
    # Substitua pelo caminho correto do arquivo
    df = pd.read_csv("imoveis-sao-paulo.csv")
    return df

# Função para análise automática por distrito
def analise_dos_dados_dos_distritos(df):
    st.title("Análise Automática de Imóveis por Distrito")

    # Seleção do distrito pelo usuário
    distritos = df["Distrito"].unique()
    distrito_selecionado = st.selectbox("Selecione um Distrito:", sorted(distritos))

    # Verificar se o distrito foi selecionado
    if distrito_selecionado:
        # Filtrar os dados para o distrito selecionado
        df_distrito = df[df["Distrito"] == distrito_selecionado]

        if df_distrito.empty:
            st.warning("Não há dados disponíveis para o distrito selecionado.")
            return

        # Exibindo as estatísticas gerais do distrito
        st.subheader(f"Estatísticas Gerais para o Distrito {distrito_selecionado}")
        st.write(df_distrito.describe())

        # Gráfico 1: Distribuição de Preços
        st.subheader("Distribuição de Preços")
        fig, ax = plt.subplots()
        sns.histplot(df_distrito["Preço"], kde=True, ax=ax, color="blue")
        ax.set_title(f"Distribuição de Preços - {distrito_selecionado}")
        ax.set_xlabel("Preço (R$)")
        ax.set_ylabel("Frequência")
        st.pyplot(fig)

        # Gráfico 2: Preço Médio por Número de Banheiros
        st.subheader("Preço Médio por Número de Banheiros")
        media_preco_banheiros = df_distrito.groupby("Banheiros")["Preço"].mean()
        fig, ax = plt.subplots()
        media_preco_banheiros.plot(kind="bar", color="skyblue", ax=ax)
        ax.set_title("Preço Médio por Número de Banheiros")
        ax.set_xlabel("Número de Banheiros")
        ax.set_ylabel("Preço Médio (R$)")
        st.pyplot(fig)

        # Gráfico 3: Preço Médio por Número de Suítes
        st.subheader("Preço Médio por Número de Suítes")
        media_preco_suites = df_distrito.groupby("Suítes")["Preço"].mean()
        fig, ax = plt.subplots()
        media_preco_suites.plot(kind="bar", color="green", ax=ax)
        ax.set_title("Preço Médio por Número de Suítes")
        ax.set_xlabel("Número de Suítes")
        ax.set_ylabel("Preço Médio (R$)")
        st.pyplot(fig)

        # Gráfico 4: Preço Médio por Vagas de Estacionamento
        st.subheader("Preço Médio por Número de Vagas de Estacionamento")
        media_preco_vagas = df_distrito.groupby("Vagas")["Preço"].mean()
        fig, ax = plt.subplots()
        media_preco_vagas.plot(kind="bar", color="orange", ax=ax)
        ax.set_title("Preço Médio por Número de Vagas")
        ax.set_xlabel("Número de Vagas")
        ax.set_ylabel("Preço Médio (R$)")
        st.pyplot(fig)

        # Gráfico 5: Preço Médio por Presença de Piscina
        st.subheader("Preço Médio por Presença de Piscina")
        media_preco_piscina = df_distrito.groupby("Piscina")["Preço"].mean()
        fig, ax = plt.subplots()
        media_preco_piscina.plot(kind="bar", color=["red", "green"], ax=ax)
        ax.set_title("Preço Médio por Presença de Piscina")
        ax.set_xlabel("Piscina (0 = Não, 1 = Sim)")
        ax.set_ylabel("Preço Médio (R$)")
        st.pyplot(fig)




# Função para exibir a média dos preços do condomínio por distrito
def media_de_precos_dos_condominios_por_distrito(df):
    st.title("Análise do Preço Médio do Condomínio por Distrito")

    # Seleção do distrito pelo usuário
    distritos = df["Distrito"].unique()
    distrito_selecionado = st.selectbox("Selecione um Distrito para Análise do Condomínio:", sorted(distritos))

    if distrito_selecionado:
        # Filtrar os dados para o distrito selecionado
        df_distrito = df[df["Distrito"] == distrito_selecionado]

        if df_distrito.empty:
            st.warning("Não há dados disponíveis para o distrito selecionado.")
            return

        # Calcular o preço médio do condomínio
        media_condominio = df_distrito["Condomínio"].mean()

        # Exibir o resultado
        st.subheader(f"Preço Médio do Condomínio no Distrito {distrito_selecionado}")
        st.metric(label=f"Preço Médio do Condomínio em {distrito_selecionado}", value=f"R$ {media_condominio:,.2f}")

        # Gráfico de distribuição do preço do condomínio
        st.subheader(f"Distribuição dos Preços do Condomínio no Distrito {distrito_selecionado}")
        fig, ax = plt.subplots()
        sns.histplot(df_distrito["Condomínio"], kde=True, ax=ax, color="purple")
        ax.set_title(f"Distribuição do Preço do Condomínio - {distrito_selecionado}")
        ax.set_xlabel("Condomínio (R$)")
        ax.set_ylabel("Frequência")
        st.pyplot(fig)


if __name__ == "__main__":
    df = load_data()

    analise_dos_dados_dos_distritos(df)

    media_de_precos_dos_condominios_por_distrito(df)

