import streamlit as st
import pandas as pd

st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """
    Carrega os dados de um arquivo CSV

    Parâmetros:
        filepath (str): Caminho para o arquivo CSV.

    Retorna:
        pd.DataFrame: DataFrame com os dados validados.
    """
    data = pd.read_csv(filepath)

    return data


def format_price(valor, pos):
    """
    Formata um valor numérico para o formato monetário brasileiro.

    Parâmetros:
        valor (float): O valor numérico a ser formatado.

    Retorno:
        str: O valor formatado no formato 'R$ X.XXX,00', substituindo a vírgula pelo ponto para conformidade com o padrão brasileiro.
    """
    return f'R$ {valor:,.0f}'.replace(",", ".")








