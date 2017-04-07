###############################################################################
#fazendo preparativos

#importa bibliotecas

#principais
import os #funções do OS
import numpy as np #vetores
import pandas as pd #data frames
import matplotlib.pyplot as plt #plots
import uncertainties as unc #incertezas
import uncertainties.umath #funções matemáticas para objetos com incerteza
import uncertainties.unumpy as unp #incertezas em vetores

#adicionais
from math import exp #função exponencial
from textwrap import dedent #retira identação de string multilinea
from sys import platform #confere qual sistema operacional é



#a partir do sistema operacional, seta o diretório de trabalho como o diretório do script
if platform == "linux": #linux
    wd = os.path.expanduser('~/MEGA/Unicamp/3° Semestre/F329_lab3/experimento_2/relatorio')
elif platform == "darwin": #OS X
    wd = os.path.expanduser('/Users/LeoBianco/Documents/git/F329_lab3/experimento_2/relatorio')

os.chdir(wd) #seta diretório

#carrega a lablib
import lablib as lab #funções pessoais de lab





#%%
###############################################################################
#carregando dados experimentais

#importa dados em um data frame
df_termistor_raw = pd.read_csv('dados_coletados/termistor_raw.csv')



#anota valores das resistências (Ohms)
#supondo que a incerteza é apenas a do ohmímetro

#resitencia avaliada R_x (68 Ohms)
R_x = unc.ufloat(
        67.7,
        lab.incerteza_ohmimetro(67.7)
        )

#resistência R_1 (100 Ohms)
R_1 = unc.ufloat(
        101.1,
        lab.incerteza_ohmimetro(101.1)
        )

#resistência R_2 (100 Ohms)
R_2 = unc.ufloat(
        100.4,
        lab.incerteza_ohmimetro(100.4)
        )

#resistência de proteção R_p (100 Ohms)
R_p = unc.ufloat(
        100.4,
        lab.incerteza_ohmimetro(100.4)
        )

#resistência de década R_d
#valor não nominal, obtido com o ohmimetro
R_d = unc.ufloat(
        67.1,
        lab.incerteza_ohmimetro(67.1)
        )

#voltagem do voltímetro na ponte de wheatstone quando avaliando R_x
V_g = unc.ufloat(
        0.002,
        lab.incerteza_voltimetro(0.002)
        )

#tensão na fonte
V_in = unc.ufloat(
        10.0,
        0.1 / (2 * 3**0.5) #incerteza retangular
        )

#temperatura ambiente
T_ambiente = unc.ufloat(
        28,
        1 / (2 * 6**0.5) #incerteza triangular (a = resolução)
        )

#resistência do termistor quando a temperatura ambiente
R_ambiente = unc.ufloat(
        200,
        lab.incerteza_ohmimetro(200)
        )


#resistência do termistor quando na mão
R_mao = unc.ufloat(
        130.0,
        lab.incerteza_ohmimetro(130.0)
        )



#%%
###############################################################################
#define funções

#calcula resistência do termistor em uma ponte de wheatstone
#formula derivada de V_g = V_in * (R_1*R_3 - R_2*R_4)/((R_1 + R_2)(R_3 + R_4))
def resistencia_termistor(R_1, R_2, R_d, V_in, V_g):
    return R_d*(-R_1*V_g + R_1*V_in - R_2*V_g)/(R_1*V_g + R_2*V_g + R_2*V_in)

#calcula a temperatura usando o termistor
#deduzido a partir de R_NTC = A * exp(B / T)
def calcula_temperatura(A, B, R):
    return B / unc.umath_core.log(R/A)

#retorna um vetor string-latex de uncertainties com apenas um algarismo signficativo
alg_sig = np.vectorize(lambda x: '${:.1u}$'.format(x).replace('+/-', ' \pm '))

#plota função do tipo f(x) = a*x + b
def curva_reta(x, a, b, legenda):
    return plt.plot(
            x,
            a*x + b,
            label = legenda
            )

#plota função do tipo f(x) = a*exp(b * x)
def curva_termistor(x, a, b, legenda):
    return plt.plot(
            x,
            a*np.exp(b/x),
            label = legenda
            )





#%%
###############################################################################
#completando os dados

#cria dataframe geral do termistor
#junta os valores com as incertezas em cada série
df_termistor = pd.DataFrame(
        data = { #colunas
                'T [K]' : unp.uarray( #temperatura do termistor em kelvin
                        df_termistor_raw['T [°C]'] + 273.15, #transforma em kelvin
                        lab.incerteza_triangular( #calcula incerteza
                                df_termistor_raw['T [°C]'] + 273.15, #transforma em kelvin
                                a = 1 #resulução, intervalo <medida - 1>,5 a <medida>,5
                                )
                        ),
                'R_d (nominal) [Ohm]' : unp.uarray( #resistência nominal da decada
                        df_termistor_raw['R_d (nominal) [Ohm]'],
                        lab.incerteza_retangular( #calcula incerteza
                                df_termistor_raw['R_d (nominal) [Ohm]'],
                                a = 1 #resulução, intervalo <medida - 1>,5 a <medida>,5
                                )
                        ),
                'R_d (ohmimetro) [Ohm]' : unp.uarray( #resistência medida (ohmímetro) da decada
                        df_termistor_raw['R_d (ohmimetro) [Ohm]'],
                        lab.incerteza_ohmimetro( #calcula a incerteza
                                df_termistor_raw['R_d (ohmimetro) [Ohm]']
                                )
                        ),
                'V_g [V]' : unp.uarray( #voltagem do voltímetro na ponte de Wheatstone
                        df_termistor_raw['V_g [V]'],
                        lab.incerteza_voltimetro( #calcula a incerteza
                                df_termistor_raw['V_g [V]']
                                )
                        )
                },
    columns = [ #ordem das colunas
               'T [K]',
                'R_d (nominal) [Ohm]',
                'R_d (ohmimetro) [Ohm]',
                'V_g [V]'
               ]
    )



#cria outra coluna do df_termistor para a resistência do termistor
df_termistor['R_t [Ohm]'] = resistencia_termistor(
        R_1,
        R_2,
        df_termistor['R_d (ohmimetro) [Ohm]'],
        V_in,
        df_termistor['V_g [V]']
        )



#dataframe necessario para a linearização
df_termistor_linearizado = pd.DataFrame(
        data = {#colunas
                '1/T [K^-1]' : 1 / df_termistor['T [K]'],
                'R_NTC [Ohm]' : df_termistor['R_t [Ohm]'],
                'ln(R_NTC)' : unp.log(df_termistor['R_t [Ohm]'])
                },
        columns = [ #ordem das colunas
                '1/T [K^-1]',
                'R_NTC [Ohm]',
                'ln(R_NTC)'
                ]
        )





#%%
###############################################################################
#plot de gráficos

#calcula os coeficientes da equação linearizada
#ln(R_NTC) = ln(A) + B*(1/T)
#y = a + b*t
coeficientes_linearizado = lab.odr_linear(
        x = unp.nominal_values(df_termistor_linearizado['1/T [K^-1]']),
        y = unp.nominal_values(df_termistor_linearizado['ln(R_NTC)']),
        dx = unp.std_devs(df_termistor_linearizado['1/T [K^-1]']),
        dy = unp.std_devs(df_termistor_linearizado['ln(R_NTC)'])
        )

# gráfico ln(R_NTC) x 1/T
plt.errorbar(
        x = unp.nominal_values(df_termistor_linearizado['1/T [K^-1]']),
        y = unp.nominal_values(df_termistor_linearizado['ln(R_NTC)']),
        xerr = unp.std_devs(df_termistor_linearizado['1/T [K^-1]']),
        yerr = unp.std_devs(df_termistor_linearizado['ln(R_NTC)']),
        fmt = 'k.', #pontos pretos
        label = 'Dados experimentais',
        capsize = 0 #retira as linhas de limite das incertezas
        )

#reta modelo
curva_reta(
        unp.nominal_values(df_termistor_linearizado['1/T [K^-1]']),
        coeficientes_linearizado[0].nominal_value, #coeficiente a
        coeficientes_linearizado[1].nominal_value, #coeficiente b
        'Dados previstos'
        )

plt.title('Gráfico $\ln(R_{NTC}) \\times 1/T\ [K^{-1}]$')
plt.xlabel('$1/T\ [K^-1]$')
plt.ylabel('$\ln(R_{NTC})$')
plt.legend(loc = 'upper left') #bota a legenda no canto superior esquerdo

plt.savefig('latex/figuras/fig_termistor_linearizado.png')
plt.show()



#calcula os coeficientes da equação normal
#R_NTC = A * exp(B/T)
#Y = A * exp(B/T)
coeficientes = [
        unc.umath_core.exp(coeficientes_linearizado[1]),
        coeficientes_linearizado[0]
        ]

# gráfico R_NTC x T
plt.errorbar(
        x = unp.nominal_values(df_termistor['T [K]']),
        y = unp.nominal_values(df_termistor['R_t [Ohm]']),
        xerr = unp.std_devs(df_termistor['T [K]']),
        yerr = unp.std_devs(df_termistor['R_t [Ohm]']),
        label = 'Dados experimentais',
        fmt = 'k.', #pontos pretos
        capsize = 0
        )

#curva modelo
curva_termistor(
        unp.nominal_values(df_termistor['T [K]']),
        coeficientes[0].nominal_value,
        coeficientes[1].nominal_value,
        'Dados previstos'
        )

plt.title('Gráfico $R_{NTC}\ [\Omega] \\times T\ [K]$')
plt.xlabel('$T\ [K]$')
plt.ylabel('$R_{NTC}\ [\Omega]$')
plt.legend()

plt.savefig('latex/figuras/fig_termistor.png')
plt.show()





#%%
###############################################################################
#salvando tabelas em arquivo tex

#representa os valores com as incertezas em string-latex e salva em um data frame
df_termistor_linearizado_latex = pd.DataFrame(
        data = { #colunas
                '$1/T [mK^-1]$' : alg_sig(1e-3 * df_termistor_linearizado['1/T [K^-1]']),
                '$R_{NTC} [\Omega]$' : alg_sig(df_termistor_linearizado['R_NTC [Ohm]']),
                '$\ln(R_{NTC})$' : alg_sig(df_termistor_linearizado['ln(R_NTC)'])
                },
        columns = [ #ordem das colunas
                   '$1/T [mK^-1]$',
                   '$R_{NTC} [\Omega]$',
                   '$\ln(R_{NTC})$'
                   ]
        )

#salva a tabela em arquivo .tex
arq_termistor_linearizado_latex = open('latex/tabelas/tab_termistor_linearizado.tex', 'w')
arq_termistor_linearizado_latex.write(lab.tabela_latex(df_termistor_linearizado_latex))
arq_termistor_linearizado_latex.close()





#%%
###############################################################################
#calculando valores importantes

#calcula resistência de R_x através da ponte de Wheatstone
R_x = resistencia_termistor(
        R_1,
        R_2,
        R_d,
        V_in,
        V_g
        )



#calcula a temperatura ambiente a partir do termistor
T_termistor_ambiente = calcula_temperatura(coeficientes[0], coeficientes[1], R_ambiente) - 273.15 #converte pra celcius


#calcula a temperatura corporal a partir do termistor
T_mao = calcula_temperatura(coeficientes[0], coeficientes[1], R_mao) - 273.15 #converte pra celcius





#%%
###############################################################################
#salvando dados importantes em latex

#salva o valor de R_x determiando pela ponte de wheatstone
arq_R_x = open('latex/outros/R_x.tex', 'w')
arq_R_x.write(dedent(
        '''
        Resistência de R_x determinada usando o método da ponte de Wheatstone:
        $R_x = {:.1u} \Omega$
        '''.format(R_x).replace('+/-', ' \pm ')
        )
    )
arq_R_x.close()



#salva o valor de temperatura ambiente e da mão determiando pela termistor
arq_R_x = open('latex/outros/temperatura_resistor.tex', 'w')
arq_R_x.write(dedent(
        '''
        Temperatura ambiente e da mão determiando pela termistor:
        $T_{{ambiente}} = {:.1u} °C$
        $T_{{mao}} = {:.1u} °C$
        '''.format(T_ambiente, T_mao).replace('+/-', ' \pm ')
        )
    )
arq_R_x.close()



#salva os valores dos coeficientes da linearização em arquivo tex
arq_coefLin_termistor = open('latex/outros/coef_linearizado_termistor.tex', 'w')
arq_coefLin_termistor.write(dedent(
        '''
        Coeficientes a e b de $\ln(R_{{NTC}}) = a + b t^-1$ determidados pela linearização:
        a = ${:.1u}\ [K]$
        b = ${:.1u}$
        '''.format(coeficientes_linearizado[0] , coeficientes_linearizado[1]).replace('+/-', ' \pm ').replace('e+0', '10^')
        )
    )
arq_coefLin_termistor.close()



#salva os valores dos coeficientes do termistor em arquivo tex
arq_coef_termistor = open('latex/outros/coef_termistor.tex', 'w')
arq_coef_termistor.write(dedent(
        '''
        Coeficientes A, B de $R_{{NTC}} = A \exp(\\frac{{B}}{{T}})$:
        $A = {:.1u}\ [\Omega]$
        $B = {:.1u}\ [K]$
        '''.format(coeficientes[0], coeficientes[1]).replace('+/-', ' \pm ').replace('e+0', '10^')
        )
    )
arq_coef_termistor.close()





#%%
###############################################################################
#salvando formulas de incertezas propagadas em latex

#propaga incerteza no calculo da resistência de R_x
propInc_res_R_x = lab.propaga_incerteza(
        'R_x',
        'R_d*(-R_1*V_g + R_1*V_in - R_2*V_g)/(R_1*V_g + R_2*V_g + R_2*V_in)',
        ['R_1', 'R_2', 'R_d', 'V_in', 'V_g']
        )

propInc_res_R_x.to_file('latex/outros/propagacaoIncerteza_R_x.tex')



#propaga incerteza no cálculo do inverso da temperatura em kelvin
#importante para a linearização e retirada de coeficientes
propInc_temp = lab.propaga_incerteza(
        't',
        '1 / (T)',
        ['T']
        )

propInc_temp.to_file('latex/outros/propagacaoIncerteza_temperatura_invertida.tex')



#propaga incerteza no cálculo do lagaritmo de R_NTC
propInc_Y = lab.propaga_incerteza(
        'Y',
        'ln(R_NTC)',
        ['R_NTC']
        )

propInc_Y.to_file('latex/outros/propagacaoIncerteza_Y.tex')



#propaga a incerteza no cálculo do coeficiente A da exponencial a partir de exp(b) (reta)
propInc_A = lab.propaga_incerteza(
        'A',
        'exp(b)',
        ['b']
        )

propInc_A.to_file('latex/outros/propagacaoIncerteza_A.tex')



#propaga incerteza no R_x usando a formula coxa
propInc_R_x_coxa = lab.propaga_incerteza(
        'R_x',
        'R_d * R_1 / R_2',
        ['R_d', 'R_1', 'R_2']
        )

propInc_R_x_coxa.to_file('latex/outros/propagacaoIncerteza_R_x_coxa')



#propaga incerteza no calculo da temperatura a partir da reistência do termistor
propInc_tempertura_termistor = lab.propaga_incerteza(
        'T',
        'B / log(R/A)',
        ['A', 'B', 'R']
        )

propInc_tempertura_termistor.to_file('latex/outros/propagacaoIncerteza_temperatura_termistor')