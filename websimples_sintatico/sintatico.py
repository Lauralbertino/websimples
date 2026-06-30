from lexer import obter_tokens, find_column

# Palavras reservadas que representam comandos válidos dentro do bloco 'pagina'
SYNTAX_KEYWORDS = {'TITULO', 'TEXTO', 'BOTAO', 'COR', 'IMAGEM', 'LINK', 'SECAO'}


class ParseError(Exception):
    """Exceção customizada para indicar erros de análise sintática."""
    pass


class SintaticoParser:
    def __init__(self, codigo, tokens):
        # Texto original do programa para calcular linha/coluna em mensagens de erro
        self.codigo = codigo
        # Remover comentários antes da análise sintática para simplificar o parser
        self.tokens = [tok for tok in tokens if tok.type != 'COMENTARIO']
        self.pos = 0
        self.errors = []

    def current_token(self):
        """Retorna o token atual ou None se chegou ao fim da lista."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        """Consome o token atual e avança para o próximo."""
        token = self.current_token()
        self.pos += 1
        return token

    def is_at_end(self):
        """Retorna True quando não há mais tokens a processar."""
        return self.current_token() is None

    def error(self, token, message):
        """Registra um erro sintático com linha e coluna no código original."""
        if token is None:
            line = self.codigo.count('\n') + 1
            col = 1
            self.errors.append(f"Linha: {line} - Coluna {col} - ERRO SINTÁTICO: {message}")
        else:
            col = find_column(self.codigo, token)
            self.errors.append(f"Linha: {token.lineno} - Coluna {col} - ERRO SINTÁTICO: {message}")

    def expect(self, token_type, message):
        """Verifica se o token atual é do tipo esperado."""
        token = self.current_token()
        if token is None:
            self.error(token, message)
            return None
        if token.type == token_type:
            return self.advance()
        self.error(token, message)
        return None

    def synchronize(self, sync_tokens=None):
        """Avança até encontrar um token que represente ponto de recuperação."""
        if sync_tokens is None:
            sync_tokens = set(SYNTAX_KEYWORDS) | {'PAGINA', 'FIM'}
        while self.current_token() and self.current_token().type not in sync_tokens:
            self.advance()

    def synchronize_statement(self):
        """Recupera o parser avançando até o fim da instrução atual."""
        sync_tokens = set(SYNTAX_KEYWORDS) | {'PAGINA', 'FIM', 'PONTO'}
        while self.current_token() and self.current_token().type not in sync_tokens:
            self.advance()
        if self.current_token() and self.current_token().type == 'PONTO':
            self.advance()

    def parse(self):
        """Ponto de entrada do parser para analisar todo o programa."""
        ast = {
            'type': 'program',
            'pagina': None,
            'statements': [],
            'fim': None
        }

        # Espera a palavra reservada inicial 'pagina'
        if self.current_token() and self.current_token().type == 'PAGINA':
            ast['pagina'] = self.advance().value
        else:
            self.error(self.current_token(), "Esperado a palavra reservada 'pagina' no início do programa.")
            self.synchronize({'PAGINA', 'FIM'})
            if self.current_token() and self.current_token().type == 'PAGINA':
                ast['pagina'] = self.advance().value

        # Processa todas as declarações até encontrar 'FIM'
        while self.current_token() and self.current_token().type != 'FIM':
            statement = self.parse_statement()
            if statement:
                ast['statements'].append(statement)

        # Espera a palavra reservada final 'fim'
        if self.current_token() and self.current_token().type == 'FIM':
            ast['fim'] = self.advance().value
        else:
            self.error(self.current_token(), "Esperado a palavra reservada 'fim' ao final do programa.")

        # Se existir token após o fim, também é um erro
        if self.current_token():
            token = self.current_token()
            self.error(token, f"Token inesperado após o fechamento do programa: '{token.value}'")

        return ast

    def parse_statement(self):
        """Analisa uma única instrução dentro do bloco 'pagina'."""
        token = self.current_token()
        if token is None:
            return None

        if token.type in SYNTAX_KEYWORDS:
            return self.parse_assignment()

        self.error(token, f"Esperado comando válido dentro do bloco da página, encontrado '{token.value}'.")
        self.synchronize()
        return None

    def parse_assignment(self):
        """Analisa um comando de atribuição do tipo COMANDO = VALOR ."""
        keyword_token = self.advance()
        atribuicao = self.expect('ATRIBUICAO', f"Esperado '=' após '{keyword_token.value}'.")

        if atribuicao is None:
            # Se não houver '=', pule a instrução até o fim para evitar erros em cascata.
            self.synchronize_statement()
            return None

        value, consumed_ponto, last_token = self.parse_value()

        if consumed_ponto:
            pass
        elif self.current_token() and self.current_token().type == 'PONTO':
            self.advance()
        elif value is None and last_token is not None:
            # Quando a análise de valor detectou erro e já sincronizou até o final,
            # não registra um erro extra de ponto final duplicado.
            pass
        else:
            self.error(last_token or self.current_token(), "Esperado '.' ao final da instrução.")
            self.synchronize_statement()

        return {
            'type': 'assignment',
            'keyword': keyword_token.type,
            'value': value,
            'line': keyword_token.lineno,
            'column': find_column(self.codigo, keyword_token)
        }

    def parse_value(self):
        """Analisa o valor de uma atribuição, que pode ser STRING ou expressão numérica."""
        token = self.current_token()
        if token is None:
            self.error(token, "Esperado um valor após '='.")
            return None, False, None

        if token.type == 'STRING':
            self.advance()
            if self.current_token() and self.current_token().type in {'MAIS', 'MENOS', 'MULTIPLICACAO', 'DIVISAO'}:
                self.error(self.current_token(), "Expressão inválida: STRING não pode ser usada em uma expressão aritmética.")
                self.synchronize_statement()
                return None, True, token
            return {
                'type': 'literal',
                'value_type': 'STRING',
                'value': token.value
            }, False, token

        if token.type in {'NUMERO', 'ABRE_PARENTESES', 'MAIS', 'MENOS'}:
            expr, terminated, last_token = self.parse_expression()
            return expr, terminated, last_token

        self.error(token, "Esperado um valor do tipo STRING ou expressão numérica após '='.")
        self.synchronize_statement()
        return None, True, token

    def parse_expression(self):
        """Analisa expressões aritméticas com precedência de operadores."""
        node, terminated, last_token = self.parse_term()
        if terminated:
            return None, True, last_token

        while self.current_token() and self.current_token().type in {'MAIS', 'MENOS'}:
            op = self.advance()
            right, right_terminated, right_last = self.parse_term()
            if right_terminated:
                return None, True, right_last
            node = {
                'type': 'binary',
                'operator': op.type,
                'left': node,
                'right': right
            }
            last_token = right_last

        if self.current_token() and self.current_token().type in {'NUMERO', 'STRING', 'ABRE_PARENTESES'}:
            self.error(self.current_token(), "Esperado operador entre operandos na expressão.")
            self.synchronize_statement()
            return None, True, self.current_token()

        return node, False, last_token

    def parse_term(self):
        """Analisa termos da expressão que usam * ou /."""
        node, terminated, last_token = self.parse_factor()
        if terminated:
            return None, True, last_token

        while self.current_token() and self.current_token().type in {'MULTIPLICACAO', 'DIVISAO'}:
            op = self.advance()
            right, right_terminated, right_last = self.parse_factor()
            if right_terminated:
                return None, True, right_last
            node = {
                'type': 'binary',
                'operator': op.type,
                'left': node,
                'right': right
            }
            last_token = right_last

        return node, False, last_token

    def parse_factor(self):
        """Analisa fatores: números, parênteses ou operadores unários."""
        token = self.current_token()
        if token is None:
            self.error(token, "Esperado um número ou '(' na expressão.")
            return None, False, None

        if token.type == 'NUMERO':
            self.advance()
            return {
                'type': 'literal',
                'value_type': 'NUMERO',
                'value': token.value
            }, False, token

        if token.type == 'ABRE_PARENTESES':
            self.advance()
            expr, terminated, last_token = self.parse_expression()
            if terminated:
                return None, True, last_token
            if self.current_token() and self.current_token().type == 'FECHA_PARENTESES':
                close_token = self.advance()
                return expr, False, close_token
            else:
                self.error(self.current_token(), "Esperado ')' no final da expressão.")
                self.synchronize_statement()
                return None, True, last_token

        if token.type in {'MAIS', 'MENOS'}:
            op = self.advance()
            factor, terminated, last_token = self.parse_factor()
            if terminated:
                return None, True, last_token
            return {
                'type': 'unary',
                'operator': op.type,
                'operand': factor
            }, False, last_token

        if token.type == 'STRING':
            self.error(token, "Expressão numérica não pode conter STRING.")
            self.advance()
            self.synchronize_statement()
            return None, True, token

        self.error(token, "Esperado um número ou '(' na expressão.")
        self.advance()
        self.synchronize_statement()
        return None, True, token

    def get_tree_text(self, node=None, level=0):
        """Gera uma representação em texto legível da AST."""
        if node is None:
            node = self.parse()

        indent = '  ' * level
        lines = []

        if node['type'] == 'program':
            lines.append(f"{indent}Programa")
            lines.append(f"{indent}  Bloco: pagina ... fim")
            for statement in node['statements']:
                lines.append(self.get_tree_text(statement, level + 1))
        elif node['type'] == 'assignment':
            lines.append(f"{indent}{node['keyword']} =")
            lines.append(self.get_tree_text(node['value'], level + 1))
        elif node['type'] == 'binary':
            lines.append(f"{indent}{node['operator']}")
            lines.append(self.get_tree_text(node['left'], level + 1))
            lines.append(self.get_tree_text(node['right'], level + 1))
        elif node['type'] == 'unary':
            lines.append(f"{indent}{node['operator']}")
            lines.append(self.get_tree_text(node['operand'], level + 1))
        elif node['type'] == 'literal':
            lines.append(f"{indent}{node['value_type']}({node['value']})")
        else:
            lines.append(f"{indent}{node}")

        return '\n'.join(lines)


def analisar_sintatico(codigo):
    """Função pública que realiza a análise sintática do código completo."""
    tokens, lex_errors = obter_tokens(codigo)
    parser = SintaticoParser(codigo, tokens)
    ast = parser.parse()
    return ast, parser.errors, lex_errors
