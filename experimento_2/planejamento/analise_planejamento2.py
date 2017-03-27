###############################################################################
#fazendo preparativos

#importa bibliotecas
import os #funções do OS
import numpy as np #vetores
import pandas as pd #data frames
import matplotlib.pyplot as plt #plots

#seta o workdirectory como o diretório do script
aux = os.path.expanduser('~/MEGA/Unicamp/3° Semestre/F329_lab3/experimento_2/planejamento')
#aux = os.path.expanduser('/Users/LeoBianco/Documents/git/F329_lab3/experimento_2/planejamento')
os.chdir(aux)

#carrega a lablib
import lablib as lab #funções pessoais de lab


#importa dados
df_termistor_raw = pd.read_csv('dados_coletados/termistor_raw.csv')

#anota valores (Ohms)
#resitencia avaliada
R_x_nominal = 68
R_x_ohmimetro = 66.8

#resistência R_1 (vermelha)
R_1_nominal = 100
R_1_ohmimetro = 100.0

#resistência R_2 (bege)
R_1_nominal = 100
R_1_ohmimetro = 100.7

#resistência de proteção R_p (amarela)
R_p_nominal = 100
R_p_ohmimetro = 99.0

#resistência de década R_d
R_d_wheatstone = 66.0



#define funções


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
        'R_d [$\\Omega$]' : df_termistor_raw['R_d [$\\Omega$]'],
        'Incerteza do R_d [$\\Omega$]' : lab.incerteza_retangular(
            df_termistor_raw['R_d [$\\Omega$]'],
            a = 1
            ),
        'Voltagem [V]' : df_termistor_raw['Voltagem [V]'],
        'Incerteza da voltagem [V]' : lab.incerteza_voltimetro(
            df_termistor_raw['Voltagem [V]']
            ),
        'Ohmimetro [$\\Omega$]' : df_termistor_raw['Ohmimetro [$\\Omega$]'],
        'Incerteza do ohmimetro [$\\Omega$]' : lab.incerteza_ohmimetro(
            df_termistor_raw['Ohmimetro [$\\Omega$]']
            )
    },
    columns = [ #ordem das colunas
        'Temperatura [°C]',
        'Incerteza da temperatura [°C]',
        'R_d [$\\Omega$]',
        'Incerteza do R_d [$\\Omega$]',
        'Voltagem [V]',
        'Incerteza da voltagem [V]',
        'Ohmimetro [$\\Omega$]',
        'Incerteza do ohmimetro [$\\Omega$]'
    ]
)

###############################################################################
#calculando valores importantes


###############################################################################
#plot de gráficos


###############################################################################
#salvando tabelas formato latex


###############################################################################
#salvando dados importantes em latex


###############################################################################
#salvando formulas de incertezas propagadas em latex
