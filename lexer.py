import ply.lex as lex
from tokens import TOKENS

# Lista de tokens
tokens = [
    'ID',
    'STRING',
    'NUMERO',
    'ATRIBUICAO',
    'ABRE_CHAVES',
    'FECHA_CHAVES',
    'PONTO',
    'VIRGULA',
    'ABRE_PARENTESES',
    'FECHA_PARENTESES',
    'COMENTARIO'
] + list(TOKENS.values())

# Lista global para coletar erros durante a análise
# Cada erro será uma tupla: (lexpos, mensagem_formatada, tipo_erro)
erros = []

# Operadores e delimitadores básicos
t_ATRIBUICAO = r'='
t_ABRE_CHAVES = r'\{'
t_FECHA_CHAVES = r'\}'
t_PONTO = r'\.'
t_VIRGULA = r','
t_ABRE_PARENTESES = r'\('
t_FECHA_PARENTESES = r'\)'

# Ignorar espaços em branco e tabulações (nova linha tem regra própria)
t_ignore = ' \t\r'

# Função para calcular coluna
def find_column(input_str, token):
    line_start = input_str.rfind('\n', 0, token.lexpos)
    if line_start < 0:
        line_start = -1
    return token.lexpos - line_start

# --- Regras de Erros Prévias (Prioridade de Erro para IDs e Números) ---

# Número mal formado (ex: 2.a3 ou 2.3a)
def t_NUMERO_MAL_FORMADO(t):
    r'[0-9]+\.[0-9]*[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+\.[a-zA-Z_][a-zA-Z0-9_]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Número mal formado: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Identificador mal formado iniciando com número (ex: 1a)
def t_ID_MAL_FORMADO_DIGITO(t):
    r'[0-9]+[a-zA-Z_][a-zA-Z0-9_]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Identificador/variável mal formado: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Identificador contendo caractere inválido grudado (ex: j@)
def t_ID_MAL_FORMADO_CARACTERE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[^a-zA-Z0-9_\s\=\{\}\.\,\(\)\#\'\"\/]+[a-zA-Z0-9_]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Identificador/variável mal formado: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# --- Regras para Tokens Válidos (e seus respectivos erros de fechamento) ---

# 1. Comentário de bloco fechado
def t_COMENTARIO_BLOCO(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    t.type = 'COMENTARIO'
    return t

# 2. Comentário de bloco NÃO fechado (captura o resto do arquivo se abrir /*)
def t_COMENTARIO_BLOCO_UNCLOSED(t):
    r'/\*(.|\n)*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Fim de arquivo inesperado (comentário não fechado): Estado final do autômato de comentários não é atingido.',
        'erro'
    ))
    t.lexer.lineno += t.value.count('\n')
    t.lexer.skip(len(t.value))
    return None

# Comentário de linha única
def t_COMENTARIO(t):
    r'\#[^\n]*'
    return t

# Strings de aspas duplas normais fechadas
def t_STRING(t):
    r'"[^"\n]*"'
    return t

# Strings de aspas duplas normais NÃO fechadas
def t_STRING_UNCLOSED(t):
    r'"[^"\n]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Char ou string mal formados: abrir aspas e não fechar: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Strings de aspas curvas fechadas
def t_STRING_CURLY(t):
    r'“[^”\n]*”'
    t.type = 'STRING'
    return t

# Strings de aspas curvas NÃO fechadas
def t_STRING_CURLY_UNCLOSED(t):
    r'“[^”\n]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Char ou string mal formados: abrir aspas e não fechar: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Chars de aspas simples fechadas
def t_CHAR(t):
    r'\'[^\'\n]*\''
    t.type = 'STRING'
    return t

# Chars de aspas simples NÃO fechadas
def t_CHAR_UNCLOSED(t):
    r'\'[^\'\n]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Char ou string mal formados: abrir aspas e não fechar: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Chars de aspas simples curvas fechadas
def t_CHAR_CURLY(t):
    r'‘[^’\n]*’'
    t.type = 'STRING'
    return t

# Chars de aspas simples curvas NÃO fechadas
def t_CHAR_CURLY_UNCLOSED(t):
    r'‘[^’\n]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Char ou string mal formados: abrir aspas e não fechar: {t.value}',
        'erro'
    ))
    t.lexer.skip(len(t.value))
    return None

# Número válido (inteiro ou real)
def t_NUMERO(t):
    r'[0-9]+\.[0-9]+|[0-9]+'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    
    # Contagem de dígitos no lexema
    digitos = sum(c.isdigit() for c in t.value)
    if digitos > 10:
        erros.append((
            t.lexpos,
            f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Tamanho excessivo do número (máximo de 10 dígitos): {t.value}',
            'erro'
        ))
        return None
    return t

# Identificador válido (pode ser palavra reservada ou ID genérico)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    
    # Verificar se é palavra reservada
    if t.value in TOKENS:
        t.type = TOKENS[t.value]
    else:
        # Verificar limite de tamanho (exemplo: 30 caracteres)
        if len(t.value) > 30:
            erros.append((
                t.lexpos,
                f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Tamanho do identificador/variável excessivo (máximo 30 caracteres): {t.value}',
                'erro'
            ))
            return None
        t.type = 'ID'
    return t

# --- Regras Auxiliares ---

# Tratamento de quebras de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Erros de caracteres isolados inválidos (ex: @ isolado)
def t_error(t):
    line = t.lineno
    col = find_column(t.lexer.lexdata, t)
    erros.append((
        t.lexpos,
        f'Linha: {line} - Coluna {col} - ERRO LÉXICO: Símbolo não pertencente ao conjunto de símbolos terminais da linguagem: {t.value[0]}',
        'erro'
    ))
    t.lexer.skip(1)

# Construir o analisador léxico
lexer = lex.lex()

# Função principal de análise para ser consumida pela interface
def analisar_codigo(codigo):
    # Reiniciar o estado global de erros e linha do lexer
    erros.clear()
    lexer.lineno = 1
    lexer.input(codigo)
    
    elementos = []
    
    # Executar o loop do lexer
    while True:
        tok = lexer.token()
        if not tok:
            break
        # Adicionar token válido na lista de elementos com seu lexpos
        col = find_column(codigo, tok)
        elementos.append((
            tok.lexpos,
            f'Linha: {tok.lineno} - Coluna {col} - Token:<{tok.type}, {tok.value}>',
            'token'
        ))
        
    # Adicionar todos os erros acumulados
    for err in erros:
        elementos.append(err)
        
    # Ordenar elementos cronologicamente de acordo com a posição (lexpos) no arquivo original
    elementos.sort(key=lambda x: x[0])
    
    # Retornar uma lista de tuplas (conteúdo, tipo) para a interface poder estilizar
    # Tipo pode ser: 'token' ou 'erro'
    return [(item[1], item[2]) for item in elementos]