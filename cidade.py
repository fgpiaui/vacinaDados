from colunas import *

class Cidade:
    def __init__(self, df, municipios):
        self.df = df
        self.municipios = municipios
        self.municipios['doses'] = self.municipios['populacao']*2
        self.dicionario_cidade = dict.fromkeys(list(self.df['estabelecimento_municipio_nome']
                                                    .unique()), dict())


    def taxa_doses_por_cidade(self, df):
        df_doses_por_populacao = df.set_index('estabelecimento_municipio_nome') \
            .join(self.municipios.set_index('nome'))
        
        df_doses_por_populacao.index.name = 'cidade'
        df_doses_por_populacao['quantidade_vacina'] = df_doses_por_populacao['quantidade_vacina'].astype('int64')
        df_doses_por_populacao['populacao'] = df_doses_por_populacao['populacao'].astype('int64')


        df_doses_por_populacao['taxa'] = df_doses_por_populacao['quantidade_vacina'] / df_doses_por_populacao['populacao']
        df_doses_por_populacao['taxa'] = (df_doses_por_populacao['taxa'] * 100).round(2)

        df_doses_por_populacao = df_doses_por_populacao.reset_index()[['cidade', 'vacina_descricao_dose','taxa']]

        self.dicionario_cidade={
            'top_2_dose':
                list(df_doses_por_populacao[df_doses_por_populacao['vacina_descricao_dose']=='    2ª Dose'].sort_values(
                'taxa', ascending=False).head().T.to_dict().values()),
            'top_1_dose':
                list(df_doses_por_populacao[df_doses_por_populacao['vacina_descricao_dose'] == '    1ª Dose'].sort_values(
                    'taxa', ascending=False).head().T.to_dict().values()),
        }


        return df_doses_por_populacao
    
    def vacinas_aplicadas(self, coluna):
        colunas = ['estabelecimento_municipio_nome', coluna]
        df_vacinas_nome_quantidade = self.df.groupby(colunas)['estabelecimento_municipio_nome']\
            .count()\
            .reset_index(name='quantidade_vacina')

        df_vacinas_nome_quantidade['percentual'] = \
            df_vacinas_nome_quantidade['quantidade_vacina']/ df_vacinas_nome_quantidade\
                .groupby('estabelecimento_municipio_nome').transform('sum')['quantidade_vacina']

        if coluna == 'paciente_idade':
            df_vacinas_nome_quantidade = df_vacinas_nome_quantidade.sort_values(by=['paciente_idade'])
        else:
            df_vacinas_nome_quantidade = df_vacinas_nome_quantidade.sort_values(by=['quantidade_vacina'])

        if coluna == 'paciente_enumsexobiologico':
            df_vacinas_nome_quantidade[coluna] = df_vacinas_nome_quantidade[coluna]\
                .replace({'F':'Feminino', 'M':'Masculino'})

        return df_vacinas_nome_quantidade

    def vacinacao_por_data(self):

        df_data_vacinacao = self.df.groupby(vacina_endereco)['estabelecimento_municipio_nome'].count()\
            .reset_index(name='quantidade_vacina')

        df_data_vacinacao['vacinacao_total_diaria'] = \
            df_data_vacinacao.groupby(['estabelecimento_municipio_nome'])['quantidade_vacina'].cumsum()

        df_data_vacinacao['media_movel'] = \
            df_data_vacinacao.groupby(['estabelecimento_municipio_nome']) \
            .rolling(7)['quantidade_vacina'].mean().fillna(0).round(2).reset_index()['quantidade_vacina']


        return df_data_vacinacao


    def taxa_vacinacao_por_cidade(self):
        contagem = self.df.groupby(cidade_estado)['estabelecimento_municipio_nome'].count() \
            .reset_index(name='quantidade_vacina') \
            .sort_values(['estabelecimento_uf', 'quantidade_vacina'], ascending=[True, False])


        df_taxa_vacinacao = contagem.set_index('estabelecimento_municipio_nome') \
            .join(self.municipios.set_index('nome'))
        df_taxa_vacinacao.index.name = 'cidade'


        df_taxa_vacinacao = df_taxa_vacinacao[['quantidade_vacina', 'populacao', 'doses']]
        df_taxa_vacinacao = df_taxa_vacinacao.astype('int64')
        # print(df_taxa_vacinacao.dtypes)

        df_taxa_vacinacao['taxa_vacinacao'] = df_taxa_vacinacao['quantidade_vacina'] / df_taxa_vacinacao['doses']
        df_taxa_vacinacao['taxa_vacinacao'] = (df_taxa_vacinacao['taxa_vacinacao']*100).round(2)


        return df_taxa_vacinacao

    def cria_dicionario(self, vacinas, df_taxa_vacinacao, vacinas_aplicadas,
                        raca_aplicada, sexo_aplicada, idade_aplicada, descricao_dose):
        for c in df_taxa_vacinacao.index.values:
            populacao = df_taxa_vacinacao.at[c, 'populacao']
            quantidade_vacina = df_taxa_vacinacao.at[c, 'quantidade_vacina']
            taxa_vacinacao = df_taxa_vacinacao.at[c, 'taxa_vacinacao']
            doses = df_taxa_vacinacao.at[c, 'doses']

            vacina_cidade = self.trata_dataframe_cidade(vacinas, c)
            vacinas_aplicadas_cidade = self.trata_dataframe_cidade(vacinas_aplicadas, c)
            raca_aplicada_cidade = self.trata_dataframe_cidade(raca_aplicada, c)
            sexo_aplicada_cidade = self.trata_dataframe_cidade(sexo_aplicada, c)
            idade_aplicada_cidade = self.trata_dataframe_cidade(idade_aplicada, c)
            descricao_dose_cidade = self.trata_dataframe_cidade(descricao_dose, c, doses=True)
            descricao_dose_cidade['per_populacao'] = (100*(descricao_dose_cidade['quantidade_vacina']/populacao)).round(2)

            vacinas_aplicadas_cidade = self.type_string(self.trata_dataframe_campo(vacinas_aplicadas_cidade, ['vacina_nome']))
            raca_aplicada_cidade = self.type_string(self.trata_dataframe_campo(raca_aplicada_cidade, ['paciente_racacor_valor']))
            sexo_aplicada_cidade = self.type_string(self.trata_dataframe_campo(sexo_aplicada_cidade, ['paciente_enumsexobiologico']))
            idade_aplicada_cidade = self.type_string(self.trata_dataframe_campo(idade_aplicada_cidade, ['paciente_idade']))
            descricao_dose_cidade = self.type_string(self.trata_dataframe_campo(descricao_dose_cidade, ['vacina_descricao_dose','per_populacao']))


            datas = list(vacina_cidade['vacina_dataaplicacao'])
            quantidade_vacinas = list(vacina_cidade['quantidade_vacina'])
            quantidade_vacinas_total = list(vacina_cidade['vacinacao_total_diaria'])
            media_movel = list(vacina_cidade['media_movel'])



            self.dicionario_cidade[c] = {
                'taxa_vacinacao': taxa_vacinacao,
                'quantidade_vacina': str(quantidade_vacina),
                'populacao': str(populacao),
                'doses':str(doses),
                'datas': datas,
                'quantidade_vacinas': quantidade_vacinas,
                'quantidade_vacinas_total':quantidade_vacinas_total,
                'media_movel':media_movel,
                'vacinas_aplicadas':list(vacinas_aplicadas_cidade.T.to_dict().values()),
                'raca_aplicada_cidade':list(raca_aplicada_cidade.T.to_dict().values()),
                'sexo_aplicada_cidade':list(sexo_aplicada_cidade.T.to_dict().values()),
                'idade_aplicada_cidade':list(idade_aplicada_cidade.T.to_dict().values()),
                'descricao_dose_cidade':list(descricao_dose_cidade.T.to_dict().values()),
            }

    @staticmethod
    def type_string(df):
        df['quantidade_vacina'] = df['quantidade_vacina'].astype('str')
        return df

    @staticmethod
    def trata_dataframe_cidade(df, c, doses=False):
        df = df[df['estabelecimento_municipio_nome'] == c]
        return df


    @staticmethod
    def trata_dataframe_campo(df, campo):
        campo.extend(['quantidade_vacina', 'percentual'])
        df = df[campo]
        return df

