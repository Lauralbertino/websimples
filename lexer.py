import ply.lex as lex
from tokens import TOKENS

# Lista de tokens e erros
tokens = [
    'ID',
    'STRING',
    'ATRIBUICAO',
    'ABRE_CHAVES',
    'FECHA_CHAVES',
    'PONTO',
    'COMENTARIO'
] + list(TOKENS.values())

erros = []

# Operadores e delimitadores
t_ATRIBUICAO = r'='
t_ABRE_CHAVES = r'\{'
t_FECHA_CHAVES = r'\}'
t_PONTO = r'\.'

# Ignorar espaços e tabs
t_ignore = ' \t'

# Palavras reservadas e IDs
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'

    if t.value in TOKENS:
        t.type = TOKENS[t.value]
        return t
    
    erros.append(
        f'ERRO LÉXICO: identificador inválido '
        f'"{t.value}" na linha {t.lineno}'
    )

# String
def t_STRING(t):
    r'"[^"]*"'
    return t

# Comentários
def t_COMENTARIO(t):
    r'\#.*'
    return t

# Nova linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Erros
def t_error(t):

    erros.append(
        f'ERRO LÉXICO: símbolo inválido '
        f'"{t.value[0]}" na linha {t.lineno}'
    )

    t.lexer.skip(1)

# Criar lexer
lexer = lex.lex()

# Função principal
def analisar_codigo(codigo):

    lexer.input(codigo)

    resultado = []

    erros.clear()

    while True:

        tok = lexer.token()

        if not tok:
            break

        resultado.append(
            f'Linha: {tok.lineno} - Token:<{tok.type}, {tok.value}>'
        )

    return erros + resultado