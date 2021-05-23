from datetime import date

from pymongo import MongoClient

from cidade import Cidade
from colunas import *
import dask
from bs4 import BeautifulSoup
from pip._vendor import requests
import dask.dataframe as dd
import pandas as pd
from unidecode import unidecode


def lista_urls(url):
    pagina = requests.get(url)
    soup = BeautifulSoup(pagina.content, 'html.parser')
    urls = list()
    estado = list()
    for tag in soup.find_all('a'):
        if 'Dados MT' in str(tag.contents[0]) and 'Dados Completo' not in str(tag.contents[0]):
            estado.append(str(tag.contents[0]).split()[1])
            urls.append(tag.attrs['href'])
            print(str(tag.contents[0]).split()[1])
    return urls, estado

def trata_municipios(csv):
    municipios = pd.read_csv(csv, sep=';')
    municipios.columns = ['uf', 'cod_uf', 'cod_municipio', 'nome', 'populacao']
    municipios = municipios[['uf', 'nome', 'populacao']]
    municipios['nome'] = municipios['nome'] \
        .apply(lambda x: x.replace(x, unidecode(x).upper()))

    return municipios

def ler_dados(url, estado, municipios):
    df = dd.read_csv(url, sep=';', assume_missing=True, usecols=coluna, na_values='0').compute()
    print(f'criou dataframe {estado}')
    cidade = Cidade(df, municipios[municipios['uf']==estado])
    vacinas = cidade.vacinacao_por_data()
    df_taxa_vacinacao = cidade.taxa_vacinacao_por_cidade()
    vacinas_aplicadas = cidade.vacinas_aplicadas('vacina_nome')
    raca_aplicada = cidade.vacinas_aplicadas('paciente_racacor_valor')
    sexo_aplicada = cidade.vacinas_aplicadas('paciente_enumsexobiologico')
    idade_aplicada = cidade.vacinas_aplicadas('paciente_idade')
    descricao_dose = cidade.vacinas_aplicadas('vacina_descricao_dose')
    cidade.cria_dicionario(vacinas, df_taxa_vacinacao, vacinas_aplicadas, raca_aplicada,
                           sexo_aplicada, idade_aplicada, descricao_dose)

    return cidade.dicionario_cidade



def salva_dados(dados, banco, estado):
    print(f"salvando {estado}")
    colecao = banco[estado]
    colecao.delete_many({})
    colecao.insert(dados)
