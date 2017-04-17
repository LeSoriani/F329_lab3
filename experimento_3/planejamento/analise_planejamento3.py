###############################################################################
#fazendo preparativos

#importa bibliotecas

#principais
import os #funções do OS
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

def calc_campo(X, Y, V):
    dV_x = V - V[:, 0:1] #diferença de potencial entre um ponto (x,y) e (0,y)
    dx = X - X[:, 0:1] #distancia em x entre (x,y) e (0,y)
    
    dV_y = V - V[0:1, :] #diferença de potencial entre um ponto (x,y) e (x,0)
    dy = Y - Y[0:1, :] #distancia em y entre (x,y) e (x,0)
    
    E_x = - dV_x / dx #componente x
    E_y = - dV_y / dy #componente y

    return (E_x, E_y)





#%%
###############################################################################
#carregando dados experimentais

#monta a grade de pontos
x = np.arange(0, 0.28, 0.03)
x = np.arange(0, 0.28, 0.03)
y = np.arange(0, 0.19, 0.03)
X, Y = np.meshgrid(x, y)

#valores de potencial
V = np.array(
        object = [
                [-1.859, -1.886, -1.918, -1.929, -1.933, -1.927, -1.925, -1.91, -1.902, -1.881],
                [-1.757, -1.778, -1.784, -1.803, -1.816, -1.824, -1.816, -1.811, -1.79, -1.758],
                [-1.655, -1.664, -1.676, -1.712, -1.709, -1.713, -1.698, -1.678, -1.658, -1.627],
                [-1.47, -1.486, -1.516, -1.55, -1.549, -1.539, -1.531, -1.512, -1.5, -1.467 ],
                [-1.258, -1.27, -1.298, -1.403, -1.357, -1.375, -1.379, -1.376, -1.239, -1.235],
                [-1.046, -1.175, -1.191, -1.169, -1.065, -1.063, -1.067, -1.013, -1.002, -1.027],
                [-0.733, -0.623, -0.62, -0.642, -0.636, -0.607, -0.564, -0.54, -0.519, -0.546]
                ]
        )





#%%
###############################################################################
#completando os dados

#calculo do campo elétrico
E_x, E_y = calc_campo(X, Y, V)



#%%
###############################################################################
#plots

#plot das linhas equipotenciais
CS = plt.contour(X, Y, V, 5, colors = 'black')
plt.clabel(CS, fontsize = 10, inline = True)

plt.title('Linhas equipotenciais das placas paralelas')
plt.xlabel('x [m]')
plt.ylabel('y [m]')

plt.savefig('latex/figuras/paralela_equipotencial.png')
plt.show()



#plot do campo com as linhas de campo
CS = plt.contour(X, Y, V, 5, colors = 'black')
plt.clabel(CS, fontsize = 10, inline = True)

plt.quiver(X, Y, E_x, E_y)

plt.title('Campo elétrico das placas paralelas com as linhas equipotenciais')
plt.xlabel('x [m]')
plt.ylabel('y [m]')

plt.savefig('latex/figuras/paralela_campo.png')
plt.show()





#%%
###############################################################################
#salvando tabelas em arquivo tex

#transforma os dados das placas paralelas em um data frame
df_latex_paralela = pd.DataFrame(V)
df_latex_paralela.index = np.arange(7) * 0.03
df_latex_paralela.columns = np.arange(10) * 0.03



#%%
###############################################################################
#calculando valores importantes





#%%
###############################################################################
#salvando dados importantes em latex





#%%
###############################################################################
#salvando formulas de incertezas propagadas em latex

