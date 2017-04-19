###############################################################################
#fazendo preparativos

#importa bibliotecas

#principais
import numpy as np #vetores
import pandas as pd #data frames
import matplotlib.pyplot as plt #plots
import seaborn as sns #plots bonitos
import uncertainties as unc #incertezas
import uncertainties.umath #funções matemáticas para objetos com incerteza
import uncertainties.unumpy as unp #incertezas em vetores

#adicionais
import lablib as lab #funções pessoais de lab
from textwrap import dedent #retira identação de string multilinea



plt.style.use('seaborn-white') #estilo de plot





#%%
###############################################################################
#define funções

#voltagem da fonte
V_fonte = unc.ufloat(
        1.9,
        0.1 / (2 * 6**0.5)
        )



def gera_matrizes(path):
    '''
    Gera as matrizes para posição no eixo x, y e voltagem ponto a ponto
    '''
    
    #le o arquivo csv dos dados
    V_raw = np.loadtxt(
        open(path, 'rb'),
        delimiter = ','
        )
    
    #retira os index de linha e coluna
    V = V_raw[1:, 1:].copy()
    
    #cria grade de pontos
    x = V_raw[0, 1:].copy()
    y = V_raw[1:, 0].copy()
    X, Y = np.meshgrid(x, y)
    
    return (X, Y, V)



def calc_campo(X, Y, V):
    '''
    Calcula o campo para cada ponto
    '''
    
    #ddp
    dV_x = np.diff(V, axis = 1) #ddp entre um ponto (x,y) e (0,y)
    dV_y = np.diff(V, axis = 0) #ddp entre um ponto (x,y) e (x,0). 0V é o potencial do anodo

    #distância aos eixos
    dx = np.diff(X, axis = 1) #distancia em x entre (x,y) e (0,y)
    dy = np.diff(Y, axis = 0) #distancia em y entre (x,y) e (x,0). 0 é a posição y do anodo
    
    #campo
    E_x = - dV_x / dx #componente x
    E_y = - dV_y / dy #componente y

    return (E_x, E_y)



def plota_campo(X, Y, V, E_x, E_y, n_linhas, titulo, path):
    #plota linhas equipotenciais
    CS = plt.contour(X, Y, V, n_linhas, colors = 'black')
    plt.clabel(CS, fontsize = 10, inline = True) #legenda das linhas
    
    #plota o campo ponto a ponto
    plt.quiver(X[:-1, :-1], Y[:-1, :-1], E_x[:-1, :], E_y[:, :-1])
    
    #meta dados do plot
    plt.title(titulo)
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    
    plt.savefig(path) #salva a a figura
    plt.show()


#%%
###############################################################################
#carregando dados experimentais

#configuração de placas paralelas (sem nada)
X_paralela, Y_paralela, V_paralela = gera_matrizes('dados_coletados/paralela_raw.csv')

#configuração de ponta
X_ponta, Y_ponta, V_ponta = gera_matrizes('dados_coletados/ponta_raw.csv')

#configuração de gaiola
X_gaiola, Y_gaiola, V_gaiola = gera_matrizes('dados_coletados/gaiola_raw.csv')

#configuração de gaiola conectada
X_conectada, Y_conectada, V_conectada = gera_matrizes('dados_coletados/conectada_raw.csv')



#modifica os pontos ocupados pela ponta de metal
#-1 é o valor associado a ponta de metal
masc = (V_ponta == -1) #mascara

V_ponta[masc] = np.nan
X_ponta[masc] = np.nan
Y_ponta[masc] = np.nan





#%%
###############################################################################
#completando os dados

#calcula do campo elétrico
E_x_paralela, E_y_paralela = calc_campo(X_paralela, Y_paralela, V_paralela)
E_x_ponta, E_y_ponta = calc_campo(X_ponta, Y_ponta, V_ponta)
E_x_gaiola, E_y_gaiola = calc_campo(X_gaiola, Y_gaiola, V_gaiola)
E_x_conectada, E_y_conectada = calc_campo(X_conectada, Y_conectada, V_conectada)





#%%
###############################################################################
#plots

#plot do campo com as linhas equipotenciais
plota_campo(
        X_paralela,
        Y_paralela,
        V_paralela,
        E_x_paralela,
        E_y_paralela,
        20,
        'Campo e linhas equipotenciais em placas paralelas',
        'latex/figuras/paralelas.png')

plota_campo(
        X_ponta,
        Y_ponta,
        V_ponta,
        E_x_ponta,
        E_y_ponta,
        20,
        'Campo e linhas equipotenciais em placas paralelas com uma ponta',
        'latex/figuras/ponta.png')

plota_campo(
        X_gaiola,
        Y_gaiola,
        V_gaiola,
        E_x_gaiola,
        E_y_gaiola,
        20,
        'Campo e linhas equipotenciais em placas paralelas com uma gaiola de Faraday',
        'latex/figuras/gaiola.png')

plota_campo(
        X_conectada,
        Y_conectada,
        V_conectada,
        E_x_conectada,
        E_y_conectada,
        17,
        'Campo e linhas equipotenciais em placas paralelas com uma gaiola de mesmo potencial que o catodo',
        'latex/figuras/conectada.png')


#%%
###############################################################################
#salvando tabelas em arquivo tex



#%%
###############################################################################
#calculando valores importantes





#%%
###############################################################################
#salvando dados importantes em latex


#%%
###############################################################################
#salvando formulas de incertezas propagadas em latex

