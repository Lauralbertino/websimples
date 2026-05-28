

from tokens import TOKENS

# Lista de erros
erros = []


def identificar_token(palavra):

    # =========================
    # PALAVRAS RESERVADAS
    # =========================
    if palavra in TOKENS:
        return TOKENS[palavra]

    # =========================
    # IDs VÁLIDOS
    # regra:
    # começa com letra
    # pode ter letras e números
    # =========================
    if palavra[0].isalpha():

        valido = True

        for c in palavra:

            if not (c.isalpha() or c.isdigit()):
                valido = False
                break

        if valido:
            return "ID"

    return None


def analisar_codigo(codigo):

    resultado = []
    erros.clear()

    linha_num = 1
    i = 0

    while i < len(codigo):

        c = codigo[i]

        # =========================
        # ESPAÇOS
        # =========================
        if c == ' ' or c == '\t':
            i += 1
            continue

        # =========================
        # NOVA LINHA
        # =========================
        if c == '\n':
            linha_num += 1
            i += 1
            continue

        # =========================
        # ATRIBUIÇÃO =
        # =========================
        if c == '=':
            resultado.append(
                f'Linha: {linha_num} - Token:<ATRIBUICAO, =>'
            )
            i += 1
            continue

        # =========================
        # ABRE CHAVES {
        # =========================
        if c == '{':
            resultado.append(
                f'Linha: {linha_num} - Token:<ABRE_CHAVES, {{>'
            )
            i += 1
            continue

        # =========================
        # FECHA CHAVES }
        # =========================
        if c == '}':
            resultado.append(
                f'Linha: {linha_num} - Token:<FECHA_CHAVES, }}>'
            )
            i += 1
            continue

        # =========================
        # PONTO .
        # =========================
        if c == '.':
            resultado.append(
                f'Linha: {linha_num} - Token:<PONTO, .>'
            )
            i += 1
            continue

        # =========================
        # COMENTÁRIO
        # =========================
        if c == '#':

            comentario = ""

            while i < len(codigo) and codigo[i] != '\n':
                comentario += codigo[i]
                i += 1

            resultado.append(
                f'Linha: {linha_num} - Token:<COMENTARIO, {comentario}>'
            )

            continue

        # =========================
        # STRING
        # =========================
        if c == '"':

            string = '"'
            i += 1

            while i < len(codigo) and codigo[i] != '"':
                string += codigo[i]
                i += 1

            # string fechada corretamente
            if i < len(codigo):

                string += '"'
                i += 1

                resultado.append(
                    f'Linha: {linha_num} - Token:<STRING, {string}>'
                )

            else:

                erros.append(
                    f'ERRO LÉXICO: string não fechada '
                    f'na linha {linha_num}'
                )

            continue

        # =========================
        # IDENTIFICADORES
        # =========================
        if c.isalpha():

            palavra = ""

            while i < len(codigo) and (
                codigo[i].isalpha() or
                codigo[i].isdigit()
            ):
                palavra += codigo[i]
                i += 1

            tipo = identificar_token(palavra)

            # =========================
            # SE FOR PALAVRA RESERVADA
            # =========================
            if palavra in TOKENS:

                resultado.append(
                    f'Linha: {linha_num} - '
                    f'Token:<{tipo}, {palavra}>'
                )

            # =========================
            # SE FOR ID VÁLIDO
            # =========================
            elif tipo == "ID":

                # exemplo de regra:
                # ID deve começar com "id"

                if palavra.startswith("id"):

                    resultado.append(
                        f'Linha: {linha_num} - '
                        f'Token:<ID, {palavra}>'
                    )

                else:

                    erros.append(
                        f'ERRO LÉXICO: identificador inválido '
                        f'"{palavra}" na linha {linha_num}'
                    )

            else:

                erros.append(
                    f'ERRO LÉXICO: identificador inválido '
                    f'"{palavra}" na linha {linha_num}'
                )

            continue

        # =========================
        # ERRO DE SÍMBOLO
        # =========================
        erros.append(
            f'ERRO LÉXICO: símbolo inválido '
            f'"{c}" na linha {linha_num}'
        )

        i += 1

    return erros + resultado