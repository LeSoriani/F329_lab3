###############################################################################
#fazendo preparativos

#importa bibliotecas
#principais
import os #funções do OS
import numpy as np #vetores
import pandas as pd #data frames
import matplotlib.pyplot as plt #plots
import uncertainties as unc
import uncertainties.unumpy as unp #incertezas

#adicionais
from textwrap import dedent #retira identação de string multilinea

#seta o workdirectory como o diretório do script
aux = os.path.expanduser('~/MEGA/Unicamp/3° Semestre/F329_lab3/experimento_2/planejamento')
#aux = os.path.expanduser('/Users/LeoBianco/Documents/git/F329_lab3/experimento_2/planejamento')
os.chdir(aux)

#carrega a lablib
import lablib as lab #funções pessoais de lab

#%%
#importa dados
df_termistor_raw = pd.read_csv('dados_coletados/termistor_raw.csv')

#anota valores (Ohms)
#resitencia avaliada
R_x_nominal = 68
R_x_ohmimetro = unc.ufloat(
        66.8,
        lab.incerteza_ohmimetro(66.8)
        )

#resistência R_1 (vermelha)
R_1_nominal = 100
R_1_ohmimetro = unc.ufloat(
        100.0,
        lab.incerteza_ohmimetro(100.0)
        )

#resistência R_2 (bege)
R_2_nominal = 100
R_2_ohmimetro = unc.ufloat(
        100.7,
        lab.incerteza_ohmimetro(100.7)
        )

#resistência de proteção R_p (amarela)
R_p_nominal = 100
R_p_ohmimetro = unc.ufloat(
        99.0,
        lab.incerteza_ohmimetro(99.0)
        )

#resistência de década R_d
#supondo que a incerteza é apenas a do ohmímetro
R_d_wheatstone = unc.ufloat(
        66.0,
        lab.incerteza_ohmimetro(66.0)
        )

#%%
#define funções

def to_kelvin(temperatura):
    return temperatura + 273.15

#calcula resistência do termistor
def calc_resistencia_termistor(R_1, R_2, R_d):
    return R_1/R_2 * R_d

#calcula incerteza na resitência do termistor
#talvez tenha que levar em conta o valor da voltagem na ponte de wheatstone
def inc_resistencia_termistor(R_1, R_2, R_d, dR_1, dR_2, dR_d):
    return (R_1**2*dR_d**2/R_2**2 + 
            R_1**2*R_d**2*dR_2**2/R_2**4 + 
            R_d**2*dR_1**2/R_2**2)**0.5

#retorna um vetor string-latex de uncertainties com apenas um algarismo signficativo
alg_sig = np.vectorize(lambda x: '${:.1u}$'.format(x).replace('+/-', ' \pm '))

def leo_valor(series):
    return series.apply(lambda x: x.nominal_value)

def leo_inc(series):
    return series.apply(lambda x: x.std_dev)


#%%
###############################################################################
#completando os dados
    
#cria dataframe geral do termistor
#junta os valores com as incertezas em um data frame
df_termistor = pd.DataFrame(
        data = { #colunas
                'Temperatura [°C]' : unp.uarray(
                        df_termistor_raw['Temperatura [°C]'],
                        lab.incerteza_triangular(
                                df_termistor_raw['Temperatura [°C]'],
                                a = 1
                                )
                        ),
                'Resistência de decada [$\Omega$]' : unp.uarray(
                        df_termistor_raw['Resistência de decada [$\Omega$]'],
                        lab.incerteza_retangular(
                                df_termistor_raw['Resistência de decada [$\Omega$]'],
                                a = 1
                                )
                        ),
                'Voltagem [V]' : unp.uarray(
                        df_termistor_raw['Voltagem [V]'],
                        lab.incerteza_voltimetro(
                                df_termistor_raw['Voltagem [V]']
                                )
                        ),
                'Ohmimetro [$\\Omega$]' : unp.uarray(
                        df_termistor_raw['Ohmimetro [$\\Omega$]'],
                        lab.incerteza_ohmimetro(
                                df_termistor_raw['Ohmimetro [$\\Omega$]']
                                )
                        )
                },
    columns = [ #ordem das colunas
               'Temperatura [°C]',
               'Resistência de decada [$\Omega$]',
               'Voltagem [V]',
               'Ohmimetro [$\\Omega$]'
               ]
        )


res_decada = unp.uarray(
        df_termistor_raw['Resistência de decada [$\\Omega$]'],
        lab.incerteza_retangular(#incerteza da resistencia de decada
                                 #necessário para a propagação de incerteza
                                 df_termistor_raw['Resistência de decada [$\Omega$]'],
                                 a = 1
                                 )
        )


#calcula a resistencia do termistor e sua incerteza com o pacote uncertainties
df_termistor['Resistência do termistor [$\\Omega$]'] = calc_resistencia_termistor(#valor da resistência do termistor
            R_1_ohmimetro,
            R_2_ohmimetro,
            res_decada
            )


#dataframe necessario para a linearização
df_termistor_linearizado = pd.DataFrame(
        data = {#colunas
                '1/T [K]' : 1 / (df_termistor['Temperatura [°C]'] + 273.15), #transforma em kelvin antes de inverter
                'RNTC [$\\Omega$]' : df_termistor['Resistência do termistor [$\\Omega$]'],#resistência do termistor ou da decada?
                'ln(RNTC) [$\\Omega$]' : unp.log(df_termistor['Resistência do termistor [$\\Omega$]'])
                },
        columns = [ #ordem das colunas
                '1/T [K]',
                'RNTC [$\\Omega$]',
                'ln(RNTC) [$\\Omega$]'
                ]
        )
#%%
###############################################################################
#calculando valores importantes

#calcula resistência e sua incerteza de R_x
#talvez tenha que levar em conta o valor da voltagem na ponte de wheatstone
R_x = calc_resistencia_termistor(
        R_1_ohmimetro,
        R_2_ohmimetro,
        R_d_wheatstone
        )

#%%
###############################################################################
#plot de gráficos

#calcular coeficientes da reta
#grafico ln(RNTC) x 1/T
#grafico RNTC x 1/T com curva exponencial

#%%
###############################################################################
#salvando tabelas formato latex
 
#representa os valalores com as incertezas em string-latex e salva em um data frame
df_termistor_latex = pd.DataFrame(
        data = { #colunas
                '1/T [K]' : alg_sig(df_termistor_linearizado['1/T [K]']),
                'RNTC [$\\Omega$]' : alg_sig(df_termistor_linearizado['RNTC [$\\Omega$]']),
                'ln(RNTC) [$\\Omega$]' : alg_sig(df_termistor_linearizado['ln(RNTC) [$\\Omega$]'])
                },
        columns = [ #ordem das colunas
                   '1/T [K]',
                   'RNTC [$\\Omega$]',
                   'ln(RNTC) [$\\Omega$]'
                   ]
        )

#salva a tabela em arquivo .tex
arq_termistor_latex = open('latex/tabelas/termistor_linearizado.tex', 'w')
arq_termistor_latex.write(lab.tabela_latex(df_termistor_latex))
arq_termistor_latex.close()

#%%
###############################################################################
#salvando dados importantes em latex

arq_R_x = open('latex/outros/resistencia_R_x', 'w')
arq_R_x.write(dedent(
        '''
        Resistência de R_x determinada usando o método da ponto de Wheatstone:
        ${:.1u} \Omega$
        '''.format(R_x).replace('+/-', ' \pm ')
        )
    )
arq_R_x.close()


#%%
###############################################################################
#salvando formulas de incertezas propagadas em latex

#propaga incerteza no calculo da resistência de R_x
propInc_res_R_x = lab.propaga_incerteza(
        'R_x',
        'R_1/R_2 * R_d',
        ['R_1', 'R_2', 'R_d']
        )

propInc_res_R_x.to_file('latex/outros/propInc_resistencia_R_x.tex')

