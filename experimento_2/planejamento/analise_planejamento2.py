###############################################################################
#fazendo preparativos

#importa bibliotecas
import os #funções do OS
import numpy as np #vetores
import pandas as pd #data frames
import matplotlib.pyplot as plt #plots
import uncertainties.unumpy as unp #incertezas

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
R_x_ohmimetro = 66.8
dR_x_ohmimetro = lab.incerteza_ohmimetro(66.8)

#resistência R_1 (vermelha)
R_1_nominal = 100
R_1_ohmimetro = 100.0
dR_1_ohmimetro = lab.incerteza_ohmimetro(100.0)

#resistência R_2 (bege)
R_2_nominal = 100
R_2_ohmimetro = 100.7
dR_2_ohmimetro = lab.incerteza_ohmimetro(100.7)

#resistência de proteção R_p (amarela)
R_p_nominal = 100
R_p_ohmimetro = 99.0
dR_p_ohmimetro = lab.incerteza_ohmimetro(99.0)

#resistência de década R_d
R_d_wheatstone = 66.0
dR_d_wheatstone = lab.incerteza_ohmimetro(66.0)
#calcular a incerteza dessa porra, nem sei como

#%%
#define funções

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

#calcula a resistencia do termistor e sua incerteza
df_termistor['Resistência do termistor [$\\Omega$]'] = pd.Series(
        unp.uarray(
                calc_resistencia_termistor(#valor da resistência do termistor
                        R_1_ohmimetro,
                        R_2_ohmimetro,
                        df_termistor_raw['Resistência de decada [$\\Omega$]']
                        ),
                inc_resistencia_termistor(#incerteza da resistencia do termistor
                        R_1_ohmimetro,
                        R_2_ohmimetro,
                        df_termistor_raw['Resistência de decada [$\\Omega$]'],
                        dR_1_ohmimetro,
                        dR_2_ohmimetro,
                        lab.incerteza_retangular(#incerteza da resistencia de decada
                                                 #necessário para a propagação de incerteza
                                df_termistor_raw['Resistência de decada [$\Omega$]'],
                                a = 1
                                )
                        )
                )
        )


#dataframe necessario para a linearização
df_termistor_linearizado = pd.DataFrame(
        data = {#colunas
                '1/T [°C]' : 1 / df_termistor['Temperatura [°C]'],
                'RTNC [$\\Omega$]' : df_termistor['Resistência do termistor [$\\Omega$]'],#resistência do termistor ou da decada?
                'ln(RTNC) [$\\Omega$]' : unp.log(df_termistor['Resistência do termistor [$\\Omega$]'])
                },
        columns = [ #ordem das colunas
                '1/T [°C]',
                'RTNC [$\\Omega$]',
                'ln(RTNC) [$\\Omega$]'
                ]
        )
#%%
###############################################################################
#calculando valores importantes

#calcula resistência desconhecida R_x
R_x = calc_resistencia_termistor(
        R_1_ohmimetro,
        R_2_ohmimetro,
        R_d_wheatstone
        )

#calcula incerteza da resistência desconhecida R_x
#talvez tenha que levar em conta o valor da voltagem na ponte de wheatstone
dR_x =  inc_resistencia_termistor(
        R_1_ohmimetro,
        R_2_ohmimetro,
        R_d_wheatstone,
        dR_1_ohmimetro,
        dR_2_ohmimetro,
        dR_d_wheatstone        
        )

#%%
###############################################################################
#plot de gráficos

#grafico R_d X temperatura
#grafico Ohmimetro x R_d

#%%
###############################################################################
#salvando tabelas formato latex
 
#representa os valalores com as incertezas em string-latex e salva em um data frame
df_termistor_latex = pd.DataFrame(
    data = { #colunas
        'Temperatura [°C]' : alg_sig(df_termistor['Temperatura [°C]']),
        'Resistência de decada [$\Omega$]' : alg_sig(df_termistor['Resistência de decada [$\Omega$]']),
        'Voltagem [V]' : alg_sig(df_termistor['Voltagem [V]']),
        'Ohmimetro [$\\Omega$]' : alg_sig(df_termistor['Ohmimetro [$\\Omega$]']),
        'Resistência do termistor [$\\Omega$]' : alg_sig(df_termistor['Resistência do termistor [$\Omega$]'])
    },
    columns = [ #ordem das colunas
        'Temperatura [°C]',
        'Resistência de decada [$\Omega$]',
        'Voltagem [V]',
        'Ohmimetro [$\\Omega$]',
        'Resistência do termistor [$\\Omega$]'
    ]
)

#salva a tabela em formato latex em um arquivo
arq_termistor_latex = open('latex/tabelas/termistor.tex', 'w')
arq_termistor_latex.write(lab.tabela_latex(df_termistor_latex))
arq_termistor_latex.close()

#%%
###############################################################################
#salvando dados importantes em latex

#%%
###############################################################################
#salvando formulas de incertezas propagadas em latex

#propaga incerteza no calculo da resistencia do termistor
incProp_res_termistor = lab.propaga_incerteza(
        'R_x',
        'R_1/R_2 * R_d',
        ['R_1', 'R_2', 'R_d']
        )

incProp_res_termistor.to_file('latex/outros/incProp_resistencia_termistor.tex')

