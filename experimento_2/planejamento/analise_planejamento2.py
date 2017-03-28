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

#cria um data frame completo para o termistor
df_termistor = pd.DataFrame(
    data = { #colunas
        'Temperatura [°C]' : df_termistor_raw['Temperatura [°C]'],
        'Incerteza da temperatura [°C]' : lab.incerteza_triangular(
                df_termistor_raw['Temperatura [°C]'],
                a = 1
                ),
        'Resistência de decada [$\Omega$]' : df_termistor_raw['Resistência de decada [$\Omega$]'],
        'Incerteza da Resistência de decada [$\Omega$]' : lab.incerteza_retangular(
                df_termistor_raw['Resistência de decada [$\Omega$]'],
                a = 1
                ),
        'Voltagem [V]' : df_termistor_raw['Voltagem [V]'],
        'Incerteza da voltagem [V]' : lab.incerteza_voltimetro(
                df_termistor_raw['Voltagem [V]']
                ),
        'Ohmimetro [$\\Omega$]' : df_termistor_raw['Ohmimetro [$\\Omega$]'],
        'Incerteza do ohmimetro [$\\Omega$]' : lab.incerteza_ohmimetro(
                df_termistor_raw['Ohmimetro [$\\Omega$]']
                ),
        'Resistência do termistor [$\\Omega$]' : calc_resistencia_termistor(
                R_1_ohmimetro,
                R_2_ohmimetro,
                df_termistor_raw['Resistência de decada [$\\Omega$]']
                ),
        'Incerteza da resistência do termistor [$\\Omega$]' : inc_resistencia_termistor(
                R_1_ohmimetro,
                R_2_ohmimetro,
                df_termistor_raw['Resistência de decada [$\\Omega$]'],
                dR_1_ohmimetro,
                dR_2_ohmimetro,
                lab.incerteza_retangular(
                        df_termistor_raw['Resistência de decada [$\Omega$]'],
                        a = 1
                        )
                )
    },
    columns = [ #ordem das colunas
        'Temperatura [°C]',
        'Incerteza da temperatura [°C]',
        'Resistência de decada [$\Omega$]',
        'Incerteza da Resistência de decada [$\Omega$]',
        'Voltagem [V]',
        'Incerteza da voltagem [V]',
        'Ohmimetro [$\\Omega$]',
        'Incerteza do ohmimetro [$\\Omega$]',
        'Resistência do termistor [$\\Omega$]',
        'Incerteza da resistência do termistor [$\\Omega$]'
    ]
)
    
#%%
###############################################################################
#calculando valores importantes


#%%
###############################################################################
#plot de gráficos

#grafico R_d X temperatura
#grafico Ohmimetro x R_d

#%%
###############################################################################
#salvando tabelas formato latex

#junta os valores com as incertezas em um data frame
df_termistor_unc = pd.DataFrame(
    data = { #colunas
        'Temperatura [°C]' : unp.uarray(
                df_termistor['Temperatura [°C]'],
                df_termistor['Incerteza da temperatura [°C]']
                ),
        'Resistência de decada [$\Omega$]' : unp.uarray(
                df_termistor['Resistência de decada [$\Omega$]'],
                df_termistor['Incerteza da Resistência de decada [$\Omega$]']
                ),
        'Voltagem [V]' : unp.uarray(
                df_termistor['Voltagem [V]'],
                df_termistor['Incerteza da voltagem [V]']
                ),
        'Ohmimetro [$\\Omega$]' : unp.uarray(
                df_termistor['Ohmimetro [$\\Omega$]'],
                df_termistor['Incerteza do ohmimetro [$\\Omega$]']
                ),
        'Resistência do termistor [$\\Omega$]' : unp.uarray(
                df_termistor['Resistência do termistor [$\\Omega$]'],
                df_termistor['Incerteza da resistência do termistor [$\\Omega$]']
                )
    },
    columns = [ #ordem das colunas
        'Temperatura [°C]',
        'Resistência de decada [$\Omega$]',
        'Voltagem [V]',
        'Ohmimetro [$\\Omega$]',
        'Resistência do termistor [$\\Omega$]'
    ]
)
 
#representa os valalores com as incertezas em string-latex e salva em um data frame
df_termistor_latex = pd.DataFrame(
    data = { #colunas
        'Temperatura [°C]' : alg_sig(df_termistor_unc['Temperatura [°C]']),
        'Resistência de decada [$\Omega$]' : alg_sig(df_termistor_unc['Resistência de decada [$\Omega$]']),
        'Voltagem [V]' : alg_sig(df_termistor_unc['Voltagem [V]']),
        'Ohmimetro [$\\Omega$]' : alg_sig(df_termistor_unc['Ohmimetro [$\\Omega$]']),
        'Resistência do termistor [$\\Omega$]' : alg_sig(df_termistor_unc['Resistência do termistor [$\Omega$]'])
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

