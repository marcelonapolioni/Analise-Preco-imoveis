import streamlit as st
import pandas as pd

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


def formatar_preco(valor, pos):
    return f'R$ {valor:,.0f}'.replace(",", ".")







