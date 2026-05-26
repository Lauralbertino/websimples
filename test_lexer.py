from lexer import analisar_codigo

def testar():
    casos = {
        "1. Token Válido Simples": 'pagina { titulo = "Loja Virtual". } fim',
        "2. Símbolo Inválido": 'pagina { titulo = "Loja". } @ fim',
        "3. Identificador Mal Formado (inicia com dígito)": 'pagina { 1a = "Teste". } fim',
        "4. Identificador Mal Formado (caractere inválido)": 'pagina { j@ = "Teste". } fim',
        "5. Tamanho do Identificador": 'pagina { minha_variavel_muito_longa_para_o_analisador = "Teste". } fim',
        "6. Número Mal Formado": 'pagina { texto = 2.a3. } fim',
        "7. Número com tamanho excessivo": 'pagina { texto = 5555555555555555. } fim',
        "8. Comentário de bloco não fechado": 'pagina { titulo = "Loja". } /* comentário sem fechar',
        "9. String não fechada (aspas normais)": 'pagina { titulo = "Minha Página. } fim',
        "10. String não fechada (aspas simples)": "pagina { titulo = 'Minha Página. } fim",
        "11. Comentário de bloco válido": 'pagina { titulo = "Loja". } /* comentário de bloco */ fim',
    }

    for nome, codigo in casos.items():
        print(f"\n=== Testando: {nome} ===")
        print(f"Código: {repr(codigo)}")
        resultado = analisar_codigo(codigo)
        for msg, tipo in resultado:
            status = "[OK]" if tipo == "token" else "[ERRO]"
            print(f"  {status} {msg}")

if __name__ == "__main__":
    testar()
