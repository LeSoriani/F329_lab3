#importa bibliotecas
import numpy as np #vetores e matrizes
import pandas as pd #data frames (tabelas)
import scipy as sci #operações numéricas
import scipy.odr #"mmq" melhorado
import sympy as sym #operação com expressões
import sympy.parsing.sympy_parser #parse string para objeto sympy'
from math import log10, floor #importante para calcular a incerteza com apenas um algarismo significativo
from os import linesep #pula linha

###############################################################################
#calculo de grandezas físicas

'''
Desciçao:
- calcula a resistencia usando R = U/i

parametros:
- voltagem: valor da voltagem (volts)
- corrente: valor da corrente (amperes)

retorna:
- resistência (ohms)
'''
def _calc_resistencia(voltagem, corrente):
    if(corrente == 0.0):
        return np.nan
    else:
        return abs(voltagem / corrente)

#vetoriza as funções (aplica a função elemento a elemento nos paremetros vetores)
vCalc_resistencia = np.vectorize(_calc_resistencia)



###############################################################################
#calculo de incertezas

'''
Desciçao:
- calcula a incerteza da voltagem medida

parametros:
- medida: valor da voltagem medida (volts)

retorna:
- incerteza da voltagem medida (volts)
'''
def _calcInc_voltagem(medida):
    #dados retirados do manual do multimetro
    #supõe corrente contínua

    #a partir da escala determina a resolução e calibração
    if(medida <= 600e-3): #escala 600mV
        resolucao = 0.1e-3
        calibracao = 0.6/100 * medida + 2*resolucao
    elif(medida <= 6): #escala 6V
        resolucao = 0.001
        calibracao = 0.3/100 * medida + 2*resolucao
    elif(medida <= 60): #escala 60V
        resolucao = 0.01
        calibracao = 0.3/100 * medida + 2*resolucao
    elif(medida <= 600): #escala 600V
        resolucao = 0.1
        calibracao = 0.3/100 * medida + 2*resolucao
    elif(medida <= 1000): #escala 1000V
        resolucao = 1
        calibracao = 0.5/100 * medida + 3*resolucao

    #supondo f.d.p retangular
    #calcula a incerteza da resolução e calibração
    inc_resolucao = resolucao / (2 * 3**0.5)
    inc_calibracao = 2 * calibracao / (2 * 3**0.5)

    #calcula a incerteza total a partir da soma dos quadrados das incertezas
    return (inc_resolucao**2 + inc_calibracao**2)**0.5


'''
Desciçao:
- calcula a incerteza da corrente medida

parametros:
- medida: valor da corrente medida (amperes)

retorna:
- incerteza da corrente medida (amperes)
'''
def _calcInc_corrente(medida):
    #dados retirados do manual do multimetro
    #supõe corrente contínua

    #a partir da escala determina a resolução e calibração
    if(medida <= 600e-6): #escala 600microA
        resolucao = 0.1e-6
        calibracao = 0.5/100 * medida + 3*resolucao
    elif(medida <= 6000e-6): #escala 6000microA
        resolucao = 1e-6
        calibracao = 0.5/100 * medida + 3*resolucao
    elif(medida <= 60e-3): #escala 60mA
        resolucao = 0.01e-3
        calibracao = 0.5/100 * medida + 3*resolucao
    elif(medida <= 600e-3): #escala 600mA
        resolucao = 0.1e-3
        calibracao = 0.8/100 * medida + 3*resolucao
    elif(medida <= 10): #escala 10A
        resolucao = 10e-3
        calibracao = 1.2/100 * medida + 3*resolucao

    #supondo f.d.p retangular
    #calcula a incerteza da resolução e calibração
    inc_resolucao = resolucao / (2 * 3**0.5)
    inc_calibracao = 2 * calibracao / (2 * 3**0.5)

    #calcula a incerteza total a partir da soma dos quadrados das incertezas
    return (inc_resolucao**2 + inc_calibracao**2)**0.5


'''
Desciçao:
- calcula a incerteza da resistencia usando R = U/i

parametros:
- voltagem: valor da voltagem (volts)
- corrente: valor da corrente (amperes)
- d_voltagem: incerteza da voltagem (volts)
- d_corrente: incerteza da corrente (amperes)

retorna:
- incerteza da resistência (ohms)
'''
def _calcInc_resistencia(voltagem, corrente, d_voltagem, d_corrente):
    if(corrente == 0.0):
        return np.nan
    else:
        return ((1/corrente**2 * d_voltagem**2) + (voltagem**2/corrente**4 * d_corrente**2))**0.5


#vetoriza as funções
vCalcInc_voltagem = np.vectorize(_calcInc_voltagem)
vCalcInc_corrente = np.vectorize(_calcInc_corrente)
vCalcInc_resistencia = np.vectorize(_calcInc_resistencia)



###############################################################################
#regressão linear com incerteza em x e y

'''
Desciçao:
- função linear genérica.
- calcula y usando y = a*x + b
- importante para a criação do modelo no odr

parametros:
- P: vetor contendo os parametros a e b
- x: valor de x

retorna:
- valor de t
'''
def _funcao_linear(P, x):
    return P[0]*x + P[1]

'''
Desciçao:
- aplica modelo linear usando ODR nos dados
- aceita incertezas em x e y
- retorna os coeficientes a, b de y = a*x + b

parametros:
- x: vetor contendo os valores de x
- y: vetor contendo os valores de y
- dx: vetor contendo as incertezas de x
- dy: vetor contendo as incertezas de x

retorna:
- dataframe contendo os coeficientes da reta e suas incertezas
'''
#define função que encaixa uma reta com odr nos dados
def odr_linear(x, y, dx, dy):
    #cria um modelo linear
    #e.i supõe que os dados seguem a lei y = a*x + b
    odr_modelo_linear = sci.odr.Model(_funcao_linear)

    #salva os dados a serem modelados em um objeto seguindo a estrutura interna do scipy.odr
    #as incertezas são passadas como pesos na forma 1/incerteza^2
    odr_dados = sci.odr.Data(
        x = x,
        y = y,
        wd = 1./dx**2,
        we = 1./dy**2
    )

    #cria um objeto do tipo ODR contendo os dados bem estruturados e o modelo linear
    odr_objeto_linear = sci.odr.ODR(
        data = odr_dados,
        model = odr_modelo_linear,
        beta0 = [1., 2.] #valores iniciais para os parametros (necessário para o algorítmo)
    )

    #aplica o metodo ODR e salva os resultados
    odr_resultados = odr_objeto_linear.run()

    #salva os coeficientes e suas incertezas em um data frame
    df_coeficientes = pd.DataFrame(
        data = { #colunas
            'Valor' : odr_resultados.beta,
            'Incerteza' : odr_resultados.sd_beta
        },
        columns = [ #ordem das colunas
            'Valor',
            'Incerteza'
        ],
        index = [ #nome dos indices
            'a',
            'b'
        ]
    )

    #renomeia a coluna dos indices
    df_coeficientes.index.name = 'Coeficiente'

    #retorna o data frame dos coeficientes
    return df_coeficientes

###############################################################################
#funções especiais

def _calc_resistencia_minima(voltagem, d_corrente):
    return abs(voltagem / d_corrente)

vCalc_resistencia_minima = np.vectorize(_calc_resistencia_minima)

###############################################################################
#representação de valores

def notacao_cientifica(x):
    aux = x
    expoente = 0
    while aux >= 10:
        aux = aux / 10
        expoente = expoente + 1
    while aux < 1:
        aux = aux * 10
        expoente = expoente - 1

    return (aux, expoente)

def algarismo_significativo(valor, incerteza):
    #casa decimal do algarismo significativo do erro
    #e.g. sig(0.001) = -3, sig(16) = 1, sig (7) = 0
    sig = int(floor(log10(abs(incerteza))))

    #arredonda para um algarismo significativo
    #round conta casas decimais como numeros positivos, por isso o "-"
    valor_sig = round(valor, -sig)
    incerteza_sig = round(incerteza, -sig)

    incerteza_cientifica = notacao_cientifica(incerteza_sig)

    representacao = str(int(valor_sig * 10**-incerteza_cientifica[1]))

    representacao = representacao + ' \pm '

    representacao = representacao + str(int(incerteza_cientifica[0]))

    representacao = '$(' + representacao + ') \cdot 10^{' + str(int(incerteza_cientifica[1])) + '}$'

    return representacao

vAlgarismo_significativo = np.vectorize(algarismo_significativo)

###############################################################################
#dedução de formulas de propagação de erro

def propaga_incerteza(equacao, grandeza, variaveis):
    #transforma as variaveis em simbolos do sympy
    var = []
    for i in variaveis:
        var.append(sym.symbols(i))

    #transforma equacao de string em formato sympy
    equacao = sym.parsing.sympy_parser.parse_expr(equacao)

    #acha as derivadas parciais da grandeza em relacao as variaveis
    derivadas_parciais = []
    for i in var:
        derivadas_parciais.append(equacao.diff(i))

    #cria os simbolos para as incertezas das variaveis
    incerteza_variaveis = []
    for i in variaveis:
        incerteza_variaveis.append(sym.symbols('\\sigma' + i))

    #multiplica a derivadas parciais pela incerteza e eleva ao quadrado
    rep = []
    for i, j in zip(incerteza_variaveis, derivadas_parciais):
        rep.append((i * j)**2)

    #junta as representacoes quadraticas com soma e tira a raiz
    incerteza_propagada = (sum(rep))**0.5

    #escreve em um arquivo as derivadas parciais
    arquivo_latex = open('incertezas_propagadas/incerteza_propagada_' + grandeza, 'w')
    for i, j in zip(variaveis, derivadas_parciais):
        arquivo_latex.write(sym.latex(sym.Eq(
            sym.symbols('\\frac{\\partial}{\\partial\ ' + i + '}' + grandeza), j)
        ) + '\n')

    #escreve no mesmo arquivo a incerteza propagada
    arquivo_latex.write(sym.latex(sym.Eq(sym.symbols('\\sigma_' + grandeza), incerteza_propagada)))
    arquivo_latex.close()

    return incerteza_propagada

def tabela_latex_quadriculada(df):
    #cabeçalho
    tabela = '\def\arraystretch{1.2}' + linesep + '\\begin{tabular}{|' + 'r|' * df.shape[1] + '}' + linesep + '\\hline' + linesep + '\midrule' + linesep
    #nome das colunas
    for nome_coluna in df.columns:
        tabela = tabela + nome_coluna + ' & '
    aux_list = list(tabela)
    aux_list[-2] = '\\\\\\hline' + linesep
    tabela = ''.join(aux_list)

    #linhas
    for i in range(df.shape[0]):
        linha_latex = ''
        for j in df.columns:
            linha_latex = linha_latex + str(df.loc[i, j]) + ' & '
        aux_list = list(linha_latex)
        aux_list[-2] = '\\\\\\hline' + linesep
        linha_latex = ''.join(aux_list)
        tabela = tabela + linha_latex

    #final da tabela
    tabela = tabela + '\\bottomrule' + linesep
    tabela = tabela + '\\end{tabular}'

    return tabela

def tabela_latex_aberta(df):
    #cabeçalho
    tabela = '\\def\\arraystretch{1.2}' + linesep + '\\begin{tabular}{' + 'r|' * (df.shape[1]-1) + 'r' + '}' + linesep + '\\toprule' + linesep + '\midrule' + linesep
    #nome das colunas
    for nome_coluna in df.columns:
        tabela = tabela + nome_coluna + ' & '
    aux_list = list(tabela)
    aux_list[-2] = '\\\\\\hline' + linesep
    tabela = ''.join(aux_list)

    #linhas
    for i in range(df.shape[0]):
        linha_latex = ''
        for j in df.columns:
            linha_latex = linha_latex + str(df.loc[i, j]) + ' & '
        aux_list = list(linha_latex)
        aux_list[-2] = '\\\\' + linesep
        linha_latex = ''.join(aux_list)
        tabela = tabela + linha_latex

    tabela = tabela + '\\bottomrule' + linesep
    tabela = tabela + '\\end{tabular}'

    return tabela
