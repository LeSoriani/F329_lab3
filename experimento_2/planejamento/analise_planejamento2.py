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
from sys import platform #confere qual sistema operacional é
from math import exp #função exponencial

#a partir do sistema operacional, seta o diretório de trabalho como o diretório do script
if platform == "linux": #linux
    wd = os.path.expanduser('~/MEGA/Unicamp/3° Semestre/F329_lab3/experimento_2/planejamento')
elif platform == "darwin": #OS X
    wd = os.path.expanduser('/Users/LeoBianco/Documents/git/F329_lab3/experimento_2/planejamento')

os.chdir(wd)

#carrega a lablib
import lablib as lab #funções pessoais de lab



#%%
#importa dados
df_termistor_raw = pd.read_csv('dados_coletados/termistor_raw.csv')

#anota valores das resistências (Ohms)
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

#tensão na fonte
fonte_voltagem = unc.ufloat(
        10.0,
        0.1 / (2 * 6**0.5)
        )


#%%
#define funções

#talvez tenha que levar em conta o valor da voltagem na ponte de wheatstone
#calcula resistência do termistor
def calc_resistencia_termistor(R_1, R_2, R_d):
    return R_1/R_2 * R_d

def calc_resistencia_termistor_volt(R_1, R_2, R_d, V_in, V_g):
    return R_d*(-R_1*V_g + R_1*V_in - R_2*V_g)/(R_1*V_g + R_2*V_g + R_2*V_in)

#retorna um vetor string-latex de uncertainties com apenas um algarismo signficativo
alg_sig = np.vectorize(lambda x: '${:.1u}$'.format(x).replace('+/-', ' \pm '))

#retorna o valor nominal de um série contendo objetos uncertainty
def leo_valor(series):
    return series.apply(lambda x: x.nominal_value)

#retorna a incerteza de um série contendo objetos uncertainty
def leo_inc(series):
    return series.apply(lambda x: x.std_dev)

#função do tipo f(x) = a*x + b
def curva_reta(x, a, b):
    return a*x + b

#função do tipo f(x) = a*exp(b * x)
def curva_exp(x, a, b):
    return a*np.exp(b * x)





#%%
###############################################################################
#completando os dados
    
#cria dataframe geral do termistor
#junta os valores com as incertezas em um data frame
df_termistor = pd.DataFrame(
        data = { #colunas
                'Temperatura [°C]' : unp.uarray(
                        df_termistor_raw['Temperatura [°C]'],
                        lab.incerteza_triangular( #calcula incerteza da medida do termometro
                                df_termistor_raw['Temperatura [°C]'],
                                a = 1 #intervalo (medida - 1),5 a medida,5
                                )
                        ),
                'Resistência de decada [Ohms]' : unp.uarray(
                        df_termistor_raw['Resistência de decada [Ohms]'],
                        lab.incerteza_retangular( #calcula incerteza da medida da decada
                                df_termistor_raw['Resistência de decada [Ohms]'],
                                a = 1 #intervalo (medida - 1),5 a medida,5
                                )
                        ),
                'Voltagem [V]' : unp.uarray(
                        df_termistor_raw['Voltagem [V]'],
                        lab.incerteza_voltimetro( #calcula a incerteza do voltimetro
                                df_termistor_raw['Voltagem [V]']
                                )
                        ),
                'Ohmimetro [Ohms]' : unp.uarray(
                        df_termistor_raw['Ohmimetro [Ohms]'],
                        lab.incerteza_ohmimetro( #calcula a incerteza do ohmimetro
                                df_termistor_raw['Ohmimetro [Ohms]']
                                )
                        )
                },
    columns = [ #ordem das colunas
               'Temperatura [°C]',
               'Resistência de decada [Ohms]',
               'Voltagem [V]',
               'Ohmimetro [Ohms]'
               ]
    )               
            
#junta a resistência da década com sua incerteza em um objeto uncertainty
aux_res_decada = unp.uarray(
        df_termistor_raw['Resistência de decada [Ohms]'],
        lab.incerteza_retangular(#incerteza da resistencia de decada
                df_termistor_raw['Resistência de decada [Ohms]'],
                a = 1 #intervalo (medida - 1),5 a medida,5
                )
        )


#cria outra coluna do df_termistor para a resistência do termistor
#calcula a resistencia do termistor e sua incerteza com o pacote uncertainties
df_termistor['Resistência do termistor [Ohms]'] = calc_resistencia_termistor(#valor da resistência do termistor
        R_1_ohmimetro,
        R_2_ohmimetro,
        aux_res_decada
        )


#dataframe necessario para a linearização
df_termistor_linearizado = pd.DataFrame(
        data = {#colunas
                '1/T [K^-1]' : 1 / (df_termistor['Temperatura [°C]'] + 273.15), #transforma em kelvin antes de inverter
                'R_NTC [Ohms]' : df_termistor['Resistência do termistor [Ohms]'],#resistência do termistor ou da decada?
                'ln(R_NTC) [ln(Ohms)]' : unp.log(df_termistor['Resistência do termistor [Ohms]'])
                },
        columns = [ #ordem das colunas
                '1/T [K^-1]',
                'R_NTC [Ohms]',
                'ln(R_NTC) [ln(Ohms)]'
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

# Obtendo os coeficientes da linearização ln(RNTC) x 1/T
df_coeficientes_linearizado = lab.odr_linear( 
        x = leo_valor(df_termistor_linearizado['1/T [K^-1]']),
        y = leo_valor(df_termistor_linearizado['ln(R_NTC) [ln(Ohms)]']),
        dx = leo_inc(df_termistor_linearizado['1/T [K^-1]']),
        dy = leo_inc(df_termistor_linearizado['ln(R_NTC) [ln(Ohms)]'])
        )
    
# gráfico do ln(RNTC) x 1 / T
plt.errorbar(       
        x = leo_valor(df_termistor_linearizado['1/T [K^-1]']),
        y = leo_valor(df_termistor_linearizado['ln(R_NTC) [ln(Ohms)]']),
        xerr = leo_inc(df_termistor_linearizado['1/T [K^-1]']),
        yerr = leo_inc(df_termistor_linearizado['ln(R_NTC) [ln(Ohms)]']),
        fmt = 'k.',
        label = 'Dados experimentais',
        capsize = 0
        )

#Plotando em cima do gráfico linearizado a reta esperada.
plt.plot(
        leo_valor(df_termistor_linearizado['1/T [K^-1]']),
        curva_reta(
                leo_valor(df_termistor_linearizado['1/T [K^-1]']),
                df_coeficientes_linearizado['Valor'][0],
                df_coeficientes_linearizado['Valor'][1]
                ),
        label = 'Dados previstos'
        )
        
plt.title('Gráfico $\ln(R_{NTC})\ [\ln(\Omega)] \\times 1/T\ [K^{-1}]$')
plt.xlabel('$1/T\ [K^-1]$') #Kelvins
plt.ylabel('$\ln(R_{NTC})\ [\ln(\Omega)]$') #Sem unidade.
plt.legend()
plt.savefig('latex/figuras/fig_termistor_linearizado.png')

plt.show()



# Gráfico sem linearização de temperatura e resistência. Não ficou parecendo exponencial.
plt.errorbar(
        x = leo_valor(df_termistor['Temperatura [°C]']) + 273.5, #Transforma em kelvins.
        y = leo_valor(df_termistor['Resistência do termistor [Ohms]']),
        xerr = leo_inc(df_termistor['Temperatura [°C]']),
        yerr = leo_inc(df_termistor['Resistência do termistor [Ohms]']),
        label = 'Dados experimentais',
        fmt = 'k.',
        capsize = 0
        )


#Gráfico da exponencial por cima:
plt.plot(
        leo_valor(df_termistor['Temperatura [°C]']) + 273.15, #Transforma em kelvins.
        curva_exp(
                1 / (leo_valor(df_termistor['Temperatura [°C]']) + 273.15),
                exp(df_coeficientes_linearizado.loc['b', 'Valor']),
                df_coeficientes_linearizado.loc['a', 'Valor']
                ),
        label = 'Dados previstos'
        )
 
plt.title('Gráfico $R_{NTC}\ [\Omega] \\times T\ [K]$')
plt.xlabel('$T\ [K]$') #Kelvins
plt.ylabel('$R_{NTC}\ [\Omega]$')
plt.legend() 
plt.savefig('latex/figuras/fig_termistor.png')
            
plt.show()





#%%
###############################################################################
#salvando tabelas formato latex
 
#representa os valalores com as incertezas em string-latex e salva em um data frame
df_termistor_latex = pd.DataFrame(
        data = { #colunas
                '$1/T [K^-1]$' : alg_sig(df_termistor_linearizado['1/T [K^-1]']),
                '$R_{NTC} [\Omega]$' : alg_sig(df_termistor_linearizado['R_NTC [Ohms]']),
                '$\ln(R_{NTC}) [\ln(\Omega)]$' : alg_sig(df_termistor_linearizado['ln(R_NTC) [ln(Ohms)]'])
                },
        columns = [ #ordem das colunas
                   '$1/T [K^-1]$',
                   '$R_{NTC} [\Omega]$',
                   '$\ln(R_{NTC}) [\ln(\Omega)]$'
                   ]
        )

#salva a tabela em arquivo .tex
arq_termistor_latex = open('latex/tabelas/tab_termistor_linearizado.tex', 'w')
arq_termistor_latex.write(lab.tabela_latex(df_termistor_latex))
arq_termistor_latex.close()





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


#coeficientes linearizados do termistor
coef_lin_a = unc.ufloat(
        df_coeficientes_linearizado.loc['a', 'Valor'],
        df_coeficientes_linearizado.loc['a', 'Incerteza']
        )
coef_lin_b = unc.ufloat(
        df_coeficientes_linearizado.loc['b', 'Valor'],
        df_coeficientes_linearizado.loc['b', 'Incerteza']
        )

#escreve em arquivo tex
arq_coefLin_termistor = open('latex/outros/coefLin_termistor.tex', 'w')
arq_coefLin_termistor.write(dedent(
        '''
        Coeficientes a e b de $\ln(R_{{NTC}}) = a + b t^-1$ determidados pela linearização:
        a = ${:.1u}\ [\ln(\Omega) K]$
        b = ${:.1u}\ [\ln(\Omega)]$
        '''.format(coef_lin_a, coef_lin_b).replace('+/-', ' \pm ').replace('e+0', '10^')
        )
    )
arq_coefLin_termistor.close()



#coeficientes da exponencial
coef_A = unc.ufloat(
        exp(df_coeficientes_linearizado.loc['b', 'Valor']),
        exp(df_coeficientes_linearizado.loc['b', 'Incerteza'])
        )
coef_B = coef_lin_a

arq_coef_termistor = open('latex/outros/coef_termistor.tex', 'w')
arq_coef_termistor.write(dedent(
        '''
        Coeficientes A, B de $R_{{NTC}} = A \exp(\\frac{{B}}{{T}})$:
        $A = {:.1u}\ [\Omega]$
        $B = {:.1u}\ [K]$
        '''.format(coef_A, coef_B).replace('+/-', ' \pm ').replace('e+0', '10^')
        )
    )
arq_coef_termistor.close()


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