import pandas as pd
def ler_estados(banco):
    return banco.collection_names()

def ler_cidades(banco, estado):
    colecao = list(banco[estado].find())[0]
    return list(filter(lambda key: key != '_id', colecao.keys()))

def converte_inteiro(lista, chave):
    for dicionario in lista:
        dicionario[chave] = int(dicionario[chave])

    return lista


def ler_info(banco, cidade, estado):
    lista = list(banco[estado].find())[0][cidade]
    lista['quantidade_vacinas_total'] = list(map(int, lista['quantidade_vacinas_total']))
    lista['quantidade_vacinas'] = list(map(int, lista['quantidade_vacinas']))
    lista['vacinas_aplicadas'] = converte_inteiro(lista['vacinas_aplicadas'], 'quantidade_vacina')
    lista['raca_aplicada_cidade'] = converte_inteiro(lista['raca_aplicada_cidade'], 'quantidade_vacina')
    lista['sexo_aplicada_cidade'] = converte_inteiro(lista['sexo_aplicada_cidade'], 'quantidade_vacina')
    lista['idade_aplicada_cidade'] = converte_inteiro(lista['idade_aplicada_cidade'], 'quantidade_vacina')
    lista['idade_aplicada_cidade'] = converte_inteiro(lista['idade_aplicada_cidade'], 'paciente_idade')
    lista['descricao_dose_cidade'] = converte_inteiro(lista['descricao_dose_cidade'], 'quantidade_vacina')
    lista['idade'] = [x['paciente_idade'] for x in lista['idade_aplicada_cidade']]
    lista['quantidade_idade'] = [x['quantidade_vacina'] for x in lista['idade_aplicada_cidade']]

    return lista

def estados_cidades(banco):
    estados = ler_estados(banco)
    estados.sort()
    estados_cidades = dict()
    for estado in estados:
        cidades = ler_cidades(banco, estado)
        cidades.sort()
        estados_cidades.update({
            estado:cidades
        })

    return estados, estados_cidades