from sintatico import analisar_sintatico

codigo = '''# Exemplo com Diversos Erros Sintáticos para Teste
pagina
  # Erro: falta de ponto final
  titulo = "Minha Loja Virtual"
  
  # Erro: comando inválido
  naoexiste = "Comando inválido".
  
  # Erro: falta do símbolo '='\n  texto "Sem atribuicao".\n  \n  # Erro: expressão incompleta\n  botao = 1 + . 2.\n  \n  # Erro: parêntese não fechado\n  cor = (1 + 2.\n  \n  # Erro: token extra após número\n  botao = 1 2.\n  \n  # Erro: expressão inválida com string+numero\n  botao = "a" + 1.\nfim\n'''

ast, errors, lex_errors = analisar_sintatico(codigo)
print('AST:', ast)
print('errors:', errors)
print('lex_errors:', lex_errors)
