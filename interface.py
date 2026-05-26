import tkinter as tk
from tkinter import filedialog, messagebox
from lexer import analisar_codigo

# Cores do tema (Catppuccin Macchiato)
BG_MAIN = "#1e1e2e"        # Cor de fundo principal
BG_SIDEBAR = "#181926"     # Cor de fundo da barra lateral / painéis
BG_EDITOR = "#24273a"      # Cor de fundo do editor
FG_TEXT = "#cad3f5"        # Cor do texto do editor
COLOR_ACCENT = "#8aadf4"   # Azul pastel (acento/botão executar)
COLOR_SUCCESS = "#a6da95"  # Verde pastel (sucesso/tokens)
COLOR_ERROR = "#ed8796"    # Vermelho/rosa pastel (erros)
COLOR_TEXT_MUTED = "#8087a2"# Texto secundário / número de linhas
COLOR_BTN = "#363a4f"      # Botão secundário
COLOR_BTN_HOVER = "#494d64"# Hover do botão secundário
COLOR_WHITE = "#ffffff"

class CustomText(tk.Text):
    """
    Subclasse de tk.Text que gera eventos virtuais quando o conteúdo muda
    ou o scroll acontece, permitindo sincronizar a numeração de linhas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._cmd)

    def _cmd(self, *args):
        # Chama o comando original
        try:
            result = self.tk.call(self._orig, *args)
        except Exception:
            return ""

        # Gera eventos virtuais para qualquer mudança de texto ou scroll
        if (args[0] in ("insert", "delete", "replace") or 
            args[0] in ("yview", "xview") or
            (len(args) > 1 and args[1] == "moveto") or
            (len(args) > 1 and args[1] == "scroll")):
            self.event_generate("<<Change>>", when="tail")

        return result

class TextEditorWithLineNumbers(tk.Frame):
    """
    Frame contendo o editor de código sincronizado com a numeração de linhas lateral.
    """
    def __init__(self, parent, on_cursor_change=None, *args, **kwargs):
        super().__init__(parent, bg=BG_EDITOR)
        self.on_cursor_change = on_cursor_change
        
        # Canvas lateral para desenhar números de linha
        self.canvas = tk.Canvas(self, width=45, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="y")
        
        # Scrollbar customizada
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self._on_scrollbar)
        self.vsb.pack(side="right", fill="y")
        
        # Widget CustomText para o editor
        self.text = CustomText(
            self, 
            bg=BG_EDITOR, 
            fg=FG_TEXT, 
            insertbackground=FG_TEXT,
            font=("Consolas", 11),
            bd=0,
            highlightthickness=0,
            undo=True,
            yscrollcommand=self.vsb.set,
            *args, **kwargs
        )
        self.text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Bindings para atualizar numeração de linhas
        self.text.bind("<<Change>>", self.redraw_line_numbers)
        self.text.bind("<Configure>", self.redraw_line_numbers)
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<ButtonRelease-1>", self._on_cursor_update)
        
        # Executa numeração inicial
        self.redraw_line_numbers()

    def _on_scrollbar(self, *args):
        self.text.yview(*args)
        self.redraw_line_numbers()

    def _on_key_release(self, event=None):
        self.redraw_line_numbers()
        self._on_cursor_update()

    def _on_cursor_update(self, event=None):
        if self.on_cursor_change:
            # Obtém linha e coluna atual do cursor
            pos = self.text.index(tk.INSERT)
            line, col = pos.split(".")
            self.on_cursor_change(int(line), int(col))

    def redraw_line_numbers(self, event=None):
        self.canvas.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if not dline:
                break
            y = dline[1]
            linenum = i.split(".")[0]
            # Desenhar o número centralizado/alinhado à direita no canvas
            self.canvas.create_text(
                35, y + 2, 
                anchor="ne", 
                text=linenum, 
                fill=COLOR_TEXT_MUTED, 
                font=("Consolas", 11, "bold")
            )
            i = self.text.index(f"{i}+1line")

class CompiladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Websimples IDE - Analisador Léxico")
        self.root.geometry("1150x780")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(900, 600)
        
        # Centralizar janela na tela
        self.center_window()
        
        # Criar Estrutura da UI
        self.criar_menu_superior()
        self.criar_layout_principal()
        self.criar_barra_status()
        
        # Inicializar estatísticas
        self.atualizar_estatisticas(0, 0)
        
        # Carregar exemplo válido inicialmente
        self.carregar_exemplo_valido()

    def center_window(self):
        self.root.update_idletasks()
        width = 1150
        height = 780
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def criar_menu_superior(self):
        # Cabeçalho da aplicação
        header = tk.Frame(self.root, bg=BG_SIDEBAR, height=60, bd=0, highlightthickness=0)
        header.pack(fill="x", side="top")
        
        titulo = tk.Label(
            header,
            text="WEBSIMPLES IDE",
            font=("Segoe UI", 16, "bold"),
            bg=BG_SIDEBAR,
            fg=COLOR_ACCENT
        )
        titulo.pack(side="left", padx=20, pady=15)
        
        subtitulo = tk.Label(
            header,
            text="|   Analisador Léxico (Trabalho Prático)",
            font=("Segoe UI", 10, "italic"),
            bg=BG_SIDEBAR,
            fg=FG_TEXT
        )
        subtitulo.pack(side="left", pady=15)
        
        grupo_label = tk.Label(
            header,
            text="Grupo: Alice, Ayane, Fabíola, Laura",
            font=("Segoe UI", 10),
            bg=BG_SIDEBAR,
            fg=COLOR_TEXT_MUTED
        )
        grupo_label.pack(side="right", padx=20, pady=15)

    def criar_layout_principal(self):
        # Container central que abriga a barra lateral e os painéis de texto
        container = tk.Frame(self.root, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # --- BARRA LATERAL DE AÇÕES (SIDEBAR) ---
        sidebar = tk.Frame(container, bg=BG_SIDEBAR, width=200, padx=15, pady=15)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        lbl_sidebar = tk.Label(
            sidebar, text="CONTROLES", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=FG_TEXT
        )
        lbl_sidebar.pack(anchor="w", pady=(0, 15))
        
        # Botões da Barra Lateral
        self.criar_botao_sidebar(sidebar, "Abrir Arquivo", self.abrir_arquivo)
        self.criar_botao_sidebar(sidebar, "Salvar Arquivo", self.salvar_arquivo)
        self.criar_botao_sidebar(sidebar, "Limpar Código", self.limpar_editor)
        
        # Linha separadora
        separador = tk.Frame(sidebar, bg="#2a2e40", height=2)
        separador.pack(fill="x", pady=15)
        
        lbl_templates = tk.Label(
            sidebar, text="MODELOS", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=FG_TEXT
        )
        lbl_templates.pack(anchor="w", pady=(0, 10))
        
        self.criar_botao_sidebar(sidebar, "Exemplo Válido", self.carregar_exemplo_valido)
        self.criar_botao_sidebar(sidebar, "Exemplo com Erros", self.carregar_exemplo_erros)
        
        # Separador para botão Executar
        separador2 = tk.Frame(sidebar, bg="#2a2e40", height=2)
        separador2.pack(fill="x", pady=15)
        
        # Botão ANALISAR (Destacado)
        btn_analisar = tk.Button(
            sidebar,
            text="Analisar Código",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_ACCENT,
            fg=BG_MAIN,
            activebackground="#789be3",
            activeforeground=BG_MAIN,
            bd=0,
            cursor="hand2",
            command=self.executar_analise_lexica,
            height=2
        )
        btn_analisar.pack(fill="x", pady=10)
        
        # --- PAINÉIS DE CÓDIGO E RESULTADOS (DIVISÃO LADO A LADO) ---
        panes_frame = tk.Frame(container, bg=BG_MAIN)
        panes_frame.pack(side="left", fill="both", expand=True)
        
        # Painel Esquerdo: Editor de Código Fonte
        painel_editor = tk.Frame(panes_frame, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        painel_editor.place(relx=0.0, rely=0.0, relwidth=0.49, relheight=1.0)
        
        lbl_editor_title = tk.Label(
            painel_editor, text="Código Fonte (.ws)", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=COLOR_ACCENT, padx=10, pady=8
        )
        lbl_editor_title.pack(anchor="w")
        
        # Instanciar o Editor com Numeração
        self.editor = TextEditorWithLineNumbers(
            painel_editor,
            on_cursor_change=self.atualizar_posicao_cursor
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Painel Direito: Resultados da Análise
        painel_resultados = tk.Frame(panes_frame, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        painel_resultados.place(relx=0.51, rely=0.0, relwidth=0.49, relheight=1.0)
        
        lbl_resultados_title = tk.Label(
            painel_resultados, text="Tokens & Erros Detectados", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=COLOR_SUCCESS, padx=10, pady=8
        )
        lbl_resultados_title.pack(anchor="w")
        
        # Campo de Saída do Lexer
        self.saida_frame = tk.Frame(painel_resultados, bg=BG_EDITOR)
        self.saida_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        self.saida_scroll = tk.Scrollbar(self.saida_frame, orient="vertical")
        self.saida_scroll.pack(side="right", fill="y")
        
        self.saida_text = tk.Text(
            self.saida_frame,
            bg=BG_EDITOR,
            fg=FG_TEXT,
            font=("Consolas", 11),
            bd=0,
            highlightthickness=0,
            yscrollcommand=self.saida_scroll.set,
            state="disabled"
        )
        self.saida_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.saida_scroll.config(command=self.saida_text.yview)
        
        # Configurar tags de colorização da saída
        self.saida_text.tag_config("token", foreground=COLOR_SUCCESS)
        self.saida_text.tag_config("erro", foreground=COLOR_ERROR, font=("Consolas", 11, "bold"))
        self.saida_text.tag_config("titulo", foreground=COLOR_ACCENT, font=("Consolas", 11, "bold"))

    def criar_botao_sidebar(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_BTN,
            fg=FG_TEXT,
            activebackground=COLOR_BTN_HOVER,
            activeforeground=COLOR_WHITE,
            bd=0,
            cursor="hand2",
            command=command,
            height=2
        )
        btn.pack(fill="x", pady=5)
        
        # Efeito Hover responsivo
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_BTN))

    def criar_barra_status(self):
        # Barra inferior para informações de status
        self.status_bar = tk.Frame(self.root, bg=BG_SIDEBAR, height=35)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.lbl_cursor_pos = tk.Label(
            self.status_bar,
            text="Linha: 1  |  Coluna: 0",
            font=("Segoe UI", 9),
            bg=BG_SIDEBAR,
            fg=COLOR_TEXT_MUTED
        )
        self.lbl_cursor_pos.pack(side="left", padx=15, pady=8)
        
        # Painel central da barra de status (sucesso / erros acumulados)
        self.lbl_status_msg = tk.Label(
            self.status_bar,
            text="Pronto para análise.",
            font=("Segoe UI", 9, "bold"),
            bg=BG_SIDEBAR,
            fg=COLOR_ACCENT
        )
        self.lbl_status_msg.pack(side="left", expand=True, pady=8)
        
        # Estatísticas à direita
        self.lbl_stats = tk.Label(
            self.status_bar,
            text="Tokens: 0  |  Erros: 0",
            font=("Segoe UI", 9, "bold"),
            bg=BG_SIDEBAR,
            fg=FG_TEXT
        )
        self.lbl_stats.pack(side="right", padx=15, pady=8)

    # --- Métodos de Controle ---
    
    def atualizar_posicao_cursor(self, line, col):
        self.lbl_cursor_pos.config(text=f"Linha: {line}  |  Coluna: {col}")

    def atualizar_estatisticas(self, total_tokens, total_erros):
        self.lbl_stats.config(text=f"Tokens: {total_tokens}  |  Erros: {total_erros}")
        
        # Ajustar a cor do painel de status de acordo com a presença de erros
        if total_erros > 0:
            self.lbl_status_msg.config(
                text=f"ANÁLISE CONCLUÍDA: {total_erros} erro(s) léxico(s) detectado(s)!",
                fg=COLOR_ERROR
            )
        else:
            self.lbl_status_msg.config(
                text="ANÁLISE CONCLUÍDA: Sucesso! Nenhum erro léxico detectado.",
                fg=COLOR_SUCCESS
            )

    def abrir_arquivo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Websimples", "*.ws"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            try:
                with open(caminho, 'r', encoding='utf-8') as arquivo:
                    codigo = arquivo.read()
                
                self.editor.text.delete('1.0', tk.END)
                self.editor.text.insert(tk.END, codigo)
                self.editor.redraw_line_numbers()
                self.atualizar_posicao_cursor(1, 0)
                
                # Limpar resultados anteriores
                self.saida_text.config(state="normal")
                self.saida_text.delete('1.0', tk.END)
                self.saida_text.config(state="disabled")
                self.lbl_status_msg.config(text=f"Arquivo '{caminho.split('/')[-1]}' carregado.", fg=COLOR_ACCENT)
                self.atualizar_estatisticas(0, 0)
            except Exception as e:
                messagebox.showerror("Erro ao Abrir Arquivo", f"Não foi possível ler o arquivo:\n{str(e)}")

    def salvar_arquivo(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".ws",
            filetypes=[("Websimples", "*.ws"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            try:
                codigo = self.editor.text.get("1.0", tk.END)
                with open(caminho, 'w', encoding='utf-8') as arquivo:
                    # Remove o caractere de nova linha automático do tkinter no final
                    if codigo.endswith("\n"):
                        codigo = codigo[:-1]
                    arquivo.write(codigo)
                messagebox.showinfo("Arquivo Salvo", f"Arquivo salvo com sucesso em:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar Arquivo", f"Não foi possível salvar o arquivo:\n{str(e)}")

    def limpar_editor(self):
        self.editor.text.delete('1.0', tk.END)
        self.editor.redraw_line_numbers()
        self.atualizar_posicao_cursor(1, 0)
        
        self.saida_text.config(state="normal")
        self.saida_text.delete('1.0', tk.END)
        self.saida_text.config(state="disabled")
        
        self.lbl_status_msg.config(text="Editor limpo.", fg=COLOR_ACCENT)
        self.atualizar_estatisticas(0, 0)

    def carregar_exemplo_valido(self):
        codigo = (
            "# Exemplo Válido da Linguagem Websimples\n"
            "pagina {\n"
            "  titulo = \"Minha Loja Virtual\".\n"
            "  texto = \"Bem-vindo à nossa loja! Aproveite os descontos\".\n"
            "  cor = \"azul\".\n"
            "  \n"
            "  # Comentário de bloco abaixo para teste\n"
            "  /* Botão de contato simples \n"
            "     com cor e link externo */\n"
            "  botao = \"Contato\".\n"
            "  link = \"https://lojavirtual.com\".\n"
            "}\n"
            "fim\n"
        )
        self.editor.text.delete('1.0', tk.END)
        self.editor.text.insert(tk.END, codigo)
        self.editor.redraw_line_numbers()
        self.atualizar_posicao_cursor(1, 0)
        self.lbl_status_msg.config(text="Modelo Válido carregado.", fg=COLOR_ACCENT)
        self.atualizar_estatisticas(0, 0)
        
        # Limpar resultados anteriores
        self.saida_text.config(state="normal")
        self.saida_text.delete('1.0', tk.END)
        self.saida_text.config(state="disabled")

    def carregar_exemplo_erros(self):
        codigo = (
            "# Exemplo com Diversos Erros Léxicos para Teste\n"
            "pagina {\n"
            "  titulo = \"Minha Loja Virtual.  # Erro: String não fechada\n"
            "  \n"
            "  # Identificador mal formado (contém caractere inválido)\n"
            "  j@ = \"Erro de caractere inválido\".\n"
            "  \n"
            "  # Identificador mal formado (inicia com dígito)\n"
            "  1a = \"Erro de início com dígito\".\n"
            "  \n"
            "  # Identificador com tamanho excessivo (máximo 30 caracteres)\n"
            "  minha_variavel_longa_para_identificar_a_cor = \"azul\".\n"
            "  \n"
            "  # Número mal formado\n"
            "  texto = 2.a3.\n"
            "  \n"
            "  # Número com tamanho excessivo (máximo de 10 dígitos)\n"
            "  botao = 5555555555555555.\n"
            "  \n"
            "  # Símbolo inválido (não pertence à linguagem)\n"
            "  @\n"
            "}\n"
            "fim\n"
            "\n"
            "# Erro: Fim de arquivo inesperado (comentário de bloco não fechado)\n"
            "/* Início do comentário de bloco sem fechamento..."
        )
        self.editor.text.delete('1.0', tk.END)
        self.editor.text.insert(tk.END, codigo)
        self.editor.redraw_line_numbers()
        self.atualizar_posicao_cursor(1, 0)
        self.lbl_status_msg.config(text="Modelo com Erros carregado.", fg=COLOR_ACCENT)
        self.atualizar_estatisticas(0, 0)
        
        # Limpar resultados anteriores
        self.saida_text.config(state="normal")
        self.saida_text.delete('1.0', tk.END)
        self.saida_text.config(state="disabled")

    def executar_analise_lexica(self):
        codigo = self.editor.text.get("1.0", tk.END)
        
        # Executa a análise léxica através do lexer
        resultado = analisar_codigo(codigo)
        
        # Ativar escrita na saída
        self.saida_text.config(state="normal")
        self.saida_text.delete('1.0', tk.END)
        
        tokens_valido = 0
        erros_lexicos = 0
        
        # Escrever título informativo
        self.saida_text.insert(tk.END, "--- RESULTADO DA ANÁLISE LÉXICA ---\n\n", "titulo")
        
        for msg, tipo in resultado:
            if tipo == "token":
                tokens_valido += 1
                self.saida_text.insert(tk.END, msg + "\n", "token")
            elif tipo == "erro":
                erros_lexicos += 1
                self.saida_text.insert(tk.END, msg + "\n", "erro")
                
        # Atualizar painel de estatísticas e status
        self.atualizar_estatisticas(tokens_valido, erros_lexicos)
        
        # Desativar escrita na saída
        self.saida_text.config(state="disabled")

def iniciar_interface():
    root = tk.Tk()
    app = CompiladorApp(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()