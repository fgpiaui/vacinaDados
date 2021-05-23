from flask import Flask, render_template
from pymongo import MongoClient

from dados import ler_estados, ler_cidades, ler_info, estados_cidades
from main2 import ler_dados, salva_dados, lista_urls, trata_municipios

app = Flask(__name__)

#cliente = MongoClient("mongodb://localhost:27017/")

cliente = MongoClient("mongodb+srv://fgpiaui:11229966@vacinadados.2aa3q.mongodb.net/vacinaDados?retryWrites=true&w=majority")
banco = cliente['vacina_dados']

@app.template_filter('separador')
def separador(valor):
    return format(int(valor), ',d').replace(',','.')

@app.template_filter('decimal')
def decimal(valor):
    return str(valor).replace('.',',')

@app.route('/')
def home():
    #estados = ler_estados(banco)
    estados, cidades = estados_cidades(banco)

    dados = {
        'estados':estados,
        'cidades':cidades
    }
    return render_template("estado.html", data=dados)

@app.route('/estado/cidade/<estado>/<cidade>')
def cidade(estado, cidade):
    info = ler_info(banco, cidade, estado)
    dados = {'cidade': cidade, 'info': info}


    return render_template("info.html", data=dados)


@app.route('/salvar')
def salva():
    url_principal = 'https://opendatasus.saude.gov.br/en/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8'
    csv_municipios = './csv/Municipios.csv'
    urls, estado = lista_urls(url_principal)
    municipios = trata_municipios(csv_municipios)
    erros = dict()
    for url, estado in zip(urls, estado):
        try:
            dados = ler_dados(url, estado, municipios)
            salva_dados(dados, banco, estado)
            print(f'estado salvo: {estado}')
        except Exception as e:
            print (f'Erro: {e}, estado: {estado}')
            erros[estado] = str(e)

    return {'msg':'Finalizou', 'erros':erros}

if __name__ == '__main__':
    app.run()
