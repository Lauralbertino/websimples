========================================================================
             PROJETO WEBSIMPLES - ANALISADOR LÉXICO
========================================================================

GRUPO:
- Alice
- Ayane
- Fabíola
- Laura

Linguagem: Python 3.12 (ou superior)
IDE Recomendada: Visual Studio Code (VS Code)
Bibliotecas Utilizadas: 
- PLY (Python Lex-Yacc) - para análise léxica
- Tkinter - para a interface gráfica (inclusa no Python padrão)

------------------------------------------------------------------------
1. ESTRUTURA DO PROJETO
------------------------------------------------------------------------
O projeto possui a seguinte estrutura de arquivos:
Websimples/
│
├── main.py            # Ponto de entrada que inicia a interface gráfica
├── lexer.py           # Definição dos tokens, autômatos e tratamento de erros (PLY)
├── interface.py       # Código da interface gráfica dark-mode (Tkinter)
├── tokens.py          # Mapeamento das palavras reservadas da linguagem
├── requirements.txt   # Dependências do projeto (PLY)
└── README.txt         # Este arquivo explicativo com passo a passo

------------------------------------------------------------------------
2. REQUISITOS E INSTALAÇÃO
------------------------------------------------------------------------
Siga as etapas abaixo para configurar o ambiente de desenvolvimento:

Passo 1: Instalação do Python
- Certifique-se de ter o Python 3 instalado no sistema.
- Caso não tenha, faça o download no site oficial: https://www.python.org/
- Certifique-se de marcar a opção "Add Python to PATH" durante a instalação.

Passo 2: Abrir o projeto no VS Code
- Abra o Visual Studio Code.
- Clique em File -> Open Folder... (Arquivo -> Abrir Pasta...) e selecione a pasta "websimples".

Passo 3: Abrir o terminal no VS Code
- Abra o terminal integrado do VS Code pressionando `Ctrl + '` ou indo no menu superior em Terminal -> New Terminal.

Passo 4: Instalar as dependências
- Instale a biblioteca PLY executando o seguinte comando no terminal:
  
  pip install -r requirements.txt
  
  (ou diretamente via: pip install ply)

------------------------------------------------------------------------
3. COMO EXECUTAR O PROJETO
------------------------------------------------------------------------
Após a instalação das dependências, execute o programa através do terminal com o seguinte comando:

  python main.py

Uma interface gráfica escura e moderna contendo dois painéis principais (Código Fonte à esquerda e Resultados da Análise à direita) será exibida.

------------------------------------------------------------------------
4. FUNCIONALIDADES DA INTERFACE GRÁFICA
------------------------------------------------------------------------
Desenvolvemos uma IDE personalizada de alta qualidade com as seguintes opções:
- Numeração de Linhas Lateral: Atualizada dinamicamente em tempo real ao digitar ou rolar o código.
- Abrir Arquivo: Permite carregar qualquer arquivo `.ws` ou de texto para o editor.
- Salvar Arquivo: Salva o código fonte atualmente no editor em um arquivo no disco.
- Limpar Código: Limpa tanto a área de entrada de código quanto os resultados.
- Modelo Válido: Carrega instantaneamente um template de código websimples sem erros léxicos.
- Modelo com Erros: Carrega um template de código contendo todos os erros léxicos especificados pelo professor para facilitar a avaliação do corretor.
- Colorização por Tags: Tokens válidos são exibidos em verde pastel, enquanto mensagens de erros são mostradas em vermelho pastel destacado.
- Barra de Status com Estatísticas: Exibe a linha/coluna atual do cursor, a contagem de tokens identificados e o número de erros detectados.

------------------------------------------------------------------------
5. TIPOS DE ERROS LÉXICOS DETECTADOS
------------------------------------------------------------------------
O analisador léxico detecta e aponta erros relacionando-os diretamente à linha e à coluna do arquivo fonte. Os erros tratados são:

1. Símbolo não pertencente ao alfabeto da linguagem:
   - Exemplo: @ por si só.
   - Mensagem: "ERRO LÉXICO: Símbolo não pertencente ao conjunto de símbolos terminais da linguagem: @"

2. Identificador/variável mal formado:
   - Exemplo: j@ (identificador seguido de símbolo inválido), 1a (iniciado com dígito).
   - Mensagem: "ERRO LÉXICO: Identificador/variável mal formado: 1a"

3. Tamanho excessivo do identificador/variável:
   - Exemplo: minha_variavel_longa_para_identificar_a_cor (limite de 30 caracteres).
   - Mensagem: "ERRO LÉXICO: Tamanho do identificador/variável excessivo (máximo 30 caracteres): ..."

4. Número mal formado:
   - Exemplo: 2.a3 (float com caractere alfabético).
   - Mensagem: "ERRO LÉXICO: Número mal formado: 2.a3"

5. Tamanho excessivo do número:
   - Exemplo: 5555555555555555 (limite de 10 dígitos).
   - Mensagem: "ERRO LÉXICO: Tamanho excessivo do número (máximo de 10 dígitos): 5555555555555555"

6. Fim de arquivo inesperado (comentário de bloco não fechado):
   - Exemplo: /* comentário aberto sem fechar com */ antes do fim do arquivo.
   - Mensagem: "ERRO LÉXICO: Fim de arquivo inesperado (comentário não fechado): Estado final do autômato de comentários não é atingido."

7. Char ou string mal formados (não fechados):
   - Exemplo: "Minha Loja Virtual (aspas abertas e não fechadas ao fim da linha). Suporta aspas duplas, simples e suas variantes curvas (Word).
   - Mensagem: "ERRO LÉXICO: Char ou string mal formados: abrir aspas e não fechar: ..."

========================================================================