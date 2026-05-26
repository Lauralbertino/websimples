import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser
import http.server
import socketserver
import threading
import json
from lexer import analisar_codigo, obter_tokens

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

# Tradutor de Cores em Português para CSS/Hex
COLOR_MAP = {
    "preto": "#111827",
    "cinza": "#4b5563",
    "azul": "#3b82f6",
    "azul_escuro": "#1e3a8a",
    "vermelho": "#ef4444",
    "vermelho_escuro": "#991b1b",
    "verde": "#10b981",
    "amarelo": "#f59e0b",
    "branco": "#ffffff"
}

# --- Estado Global do Servidor de Prévia em Tempo Real ---
PREVIEW_HTML = "<h1>Editor Websimples</h1><p>Digite seu código para ver a prévia em tempo real!</p>"
VERSION = 0
PORT = 8080

class PreviewHTTPHandler(http.server.BaseHTTPRequestHandler):
    """
    Servidor HTTP leve para responder com o HTML gerado e um endpoint de status
    usado pelo script de live-reload na página do navegador.
    """
    def log_message(self, format, *args):
        # Suprimir logs no terminal para não poluir
        pass

    def do_GET(self):
        global PREVIEW_HTML, VERSION
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Script para verificar alterações e dar reload
            live_reload_script = f"""
            <script>
                let lastVersion = {VERSION};
                setInterval(() => {{
                    fetch('/status')
                        .then(res => res.json())
                        .then(data => {{
                            if (data.version > lastVersion) {{
                                window.location.reload();
                            }}
                        }})
                        .catch(err => console.log("Erro de conexão com o compilador"));
                }}, 500);
            </script>
            """
            content = PREVIEW_HTML.replace('</body>', f'{live_reload_script}</body>')
            self.wfile.write(content.encode('utf-8'))
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'version': VERSION}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def iniciar_servidor():
    global PORT
    while True:
        try:
            handler = PreviewHTTPHandler
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer(("", PORT), handler)
            server.serve_forever()
            break
        except OSError:
            # Se a porta estiver em uso, tenta a próxima
            PORT += 1

# Iniciar o servidor HTTP em segundo plano (thread daemon)
server_thread = threading.Thread(target=iniciar_servidor, daemon=True)
server_thread.start()

# --- Funções de Compilação/Tradução ---

def compilar_para_html(codigo):
    """
    Simula uma compilação direcionada por sintaxe simples para traduzir 
    os tokens do Websimples em um código HTML/CSS responsivo.
    """
    toks, errs = obter_tokens(codigo)
    if errs:
        return None, "Não é possível gerar a prévia: Existem erros léxicos no seu código."
        
    html_title = "Página Websimples"
    bg_color = "#ffffff"
    text_color = "#111827"
    
    elements = []
    current_section = None
    
    # Parser de atribuição simplificado: KEYWORD = VALUE [.]
    i = 0
    n = len(toks)
    
    while i < n:
        tok = toks[i]
        
        # Mapear declarações de atribuição
        if tok.type in ['TITULO', 'COR', 'TEXTO', 'SECAO', 'BOTAO', 'LINK', 'IMAGEM']:
            key = tok.type
            # Próximo deve ser '='
            if i + 1 < n and toks[i+1].type == 'ATRIBUICAO':
                # Próximo deve ser STRING ou NUMERO
                if i + 2 < n and toks[i+2].type in ['STRING', 'NUMERO']:
                    val = toks[i+2].value
                    
                    # Remover aspas externas de Strings
                    if toks[i+2].type == 'STRING':
                        if len(val) >= 2 and val[0] in ['"', "'", '“', '‘'] and val[-1] in ['"', "'", '”', '’']:
                            val = val[1:-1]
                            
                    # Verificar se há ponto no final
                    tem_ponto = False
                    if i + 3 < n and toks[i+3].type == 'PONTO':
                        tem_ponto = True
                        
                    # Processar atribuições e construir a árvore simples
                    if key == 'TITULO':
                        html_title = val
                    elif key == 'COR':
                        bg_color = COLOR_MAP.get(val.lower(), val)
                        # Adaptar cor de texto baseada no fundo
                        if val.lower() in ["preto", "azul_escuro", "vermelho_escuro", "cinza"]:
                            text_color = "#f3f4f6"
                        else:
                            text_color = "#111827"
                    elif key == 'SECAO':
                        current_section = {'type': 'section', 'title': val, 'content': []}
                        elements.append(current_section)
                    elif key == 'TEXTO':
                        item = {'type': 'text', 'text': val}
                        if current_section:
                            current_section['content'].append(item)
                        else:
                            elements.append(item)
                    elif key == 'BOTAO':
                        item = {'type': 'button', 'text': val, 'link': '#'}
                        if current_section:
                            current_section['content'].append(item)
                        else:
                            elements.append(item)
                    elif key == 'LINK':
                        # Associar o link ao último botão inserido na seção ou página
                        target = current_section['content'] if current_section else elements
                        for el in reversed(target):
                            if el['type'] == 'button':
                                el['link'] = val
                                break
                    elif key == 'IMAGEM':
                        item = {'type': 'image', 'src': val}
                        if current_section:
                            current_section['content'].append(item)
                        else:
                            elements.append(item)
                            
                    i += 4 if tem_ponto else 3
                    continue
        i += 1

    # Definir classe de tema claro se aplicável
    is_dark = bg_color.lower() in ["#111827", "#1e3a8a", "#991b1b", "#4b5563"] or bg_color.startswith("#1") or bg_color.startswith("#2")
    body_class = "" if is_dark else 'class="light-theme"'

    # Gerar HTML com design responsivo premium
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: {bg_color};
            color: {text_color};
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px;
            transition: all 0.3s ease;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 40px;
            max-width: 750px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}
        body.light-theme .card {{
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
        }}
        h1 {{
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 30px;
            text-align: center;
            background: linear-gradient(135deg, #8aadf4, #b7bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
        }}
        body.light-theme h1 {{
            background: linear-gradient(135deg, #1e3a8a, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .secao {{
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
        }}
        body.light-theme .secao {{
            border-top: 1px solid rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 18px;
            color: #8aadf4;
            letter-spacing: -0.02em;
        }}
        body.light-theme h2 {{
            color: #1e3a8a;
        }}
        p {{
            font-size: 1.1rem;
            line-height: 1.65;
            margin-bottom: 20px;
            opacity: 0.9;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #8aadf4, #789be3);
            color: #1e1e2e !important;
            font-weight: 700;
            text-decoration: none;
            padding: 12px 28px;
            border-radius: 10px;
            box-shadow: 0 4px 14px rgba(138, 173, 244, 0.35);
            transition: all 0.3s ease;
            margin: 10px 0;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(138, 173, 244, 0.5);
            background: linear-gradient(135deg, #789be3, #8aadf4);
        }}
        body.light-theme .btn {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        }}
        body.light-theme .btn:hover {{
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
        }}
        .img-fluid {{
            max-width: 100%;
            height: auto;
            border-radius: 14px;
            margin: 15px 0 25px 0;
            border: 2px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        }}
        body.light-theme .img-fluid {{
            border: 2px solid rgba(0, 0, 0, 0.06);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }}
        footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.85rem;
            opacity: 0.55;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 20px;
        }}
        body.light-theme footer {{
            border-top: 1px solid rgba(0, 0, 0, 0.08);
        }}
    </style>
</head>
<body {body_class}>
    <div class="card">
        <header>
            <h1>{html_title}</h1>
        </header>
        <main>
    """
    
    for el in elements:
        if el['type'] == 'section':
            html += f"""
            <div class="secao">
                <h2>{el['title']}</h2>
            """
            for sub in el['content']:
                if sub['type'] == 'text':
                    html += f"                <p>{sub['text']}</p>\n"
                elif sub['type'] == 'button':
                    html += f"                <a href=\"{sub['link']}\" target=\"_blank\" class=\"btn\">{sub['text']}</a>\n"
                elif sub['type'] == 'image':
                    src = sub['src']
                    if not src.startswith("http") and not os.path.exists(src):
                        src = f"https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=600&q=80"
                    html += f"                <img src=\"{src}\" class=\"img-fluid\" alt=\"Imagem da Seção\">\n"
            html += "            </div>\n"
            
        elif el['type'] == 'text':
            html += f"            <p>{el['text']}</p>\n"
        elif el['type'] == 'button':
            html += f"            <a href=\"{el['link']}\" target=\"_blank\" class=\"btn\">{el['text']}</a>\n"
        elif el['type'] == 'image':
            src = el['src']
            if not src.startswith("http") and not os.path.exists(src):
                src = f"https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=600&q=80"
            html += f"            <img src=\"{src}\" class=\"img-fluid\" alt=\"Imagem\">\n"
            
    html += """
        </main>
        <footer>
            <p>Gerado automaticamente pelo Compilador Websimples &copy; 2026</p>
        </footer>
    </div>
</body>
</html>
"""
    return html, None

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
        try:
            result = self.tk.call(self._orig, *args)
        except Exception:
            return ""

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
        
        self.redraw_line_numbers()

    def _on_scrollbar(self, *args):
        self.text.yview(*args)
        self.redraw_line_numbers()

    def _on_key_release(self, event=None):
        self.redraw_line_numbers()
        self._on_cursor_update()

    def _on_cursor_update(self, event=None):
        if self.on_cursor_change:
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
        
        self.center_window()
        
        self.criar_menu_superior()
        self.criar_layout_principal()
        self.criar_barra_status()
        
        self.atualizar_estatisticas(0, 0)
        
        # Binding para processamento em tempo real
        self.editor.text.bind("<<Change>>", self.ao_mudar_texto)
        
        self.carregar_exemplo_valido()

    def center_window(self):
        self.root.update_idletasks()
        width = 1150
        height = 780
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def criar_menu_superior(self):
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
        
        self.criar_botao_sidebar(sidebar, "Abrir Arquivo", self.abrir_arquivo)
        self.criar_botao_sidebar(sidebar, "Salvar Arquivo", self.salvar_arquivo)
        self.criar_botao_sidebar(sidebar, "Limpar Código", self.limpar_editor)
        
        separador = tk.Frame(sidebar, bg="#2a2e40", height=2)
        separador.pack(fill="x", pady=15)
        
        lbl_templates = tk.Label(
            sidebar, text="MODELOS", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=FG_TEXT
        )
        lbl_templates.pack(anchor="w", pady=(0, 10))
        
        self.criar_botao_sidebar(sidebar, "Exemplo Válido", self.carregar_exemplo_valido)
        self.criar_botao_sidebar(sidebar, "Exemplo com Erros", self.carregar_exemplo_erros)
        
        separador2 = tk.Frame(sidebar, bg="#2a2e40", height=2)
        separador2.pack(fill="x", pady=15)
        
        # Botões de Execução
        self.criar_botao_sidebar(sidebar, "Visualizar HTML", self.visualizar_pagina_html)
        
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
        
        # --- PAINÉIS DE CÓDIGO E RESULTADOS ---
        panes_frame = tk.Frame(container, bg=BG_MAIN)
        panes_frame.pack(side="left", fill="both", expand=True)
        
        # Painel Esquerdo: Editor
        painel_editor = tk.Frame(panes_frame, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        painel_editor.place(relx=0.0, rely=0.0, relwidth=0.49, relheight=1.0)
        
        lbl_editor_title = tk.Label(
            painel_editor, text="Código Fonte (.ws)", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=COLOR_ACCENT, padx=10, pady=8
        )
        lbl_editor_title.pack(anchor="w")
        
        self.editor = TextEditorWithLineNumbers(
            painel_editor,
            on_cursor_change=self.atualizar_posicao_cursor
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Painel Direito: Resultados
        painel_resultados = tk.Frame(panes_frame, bg=BG_SIDEBAR, bd=0, highlightthickness=0)
        painel_resultados.place(relx=0.51, rely=0.0, relwidth=0.49, relheight=1.0)
        
        lbl_resultados_title = tk.Label(
            painel_resultados, text="Tokens & Erros Detectados", font=("Segoe UI", 11, "bold"),
            bg=BG_SIDEBAR, fg=COLOR_SUCCESS, padx=10, pady=8
        )
        lbl_resultados_title.pack(anchor="w")
        
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
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_BTN))

    def criar_barra_status(self):
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
        
        self.lbl_status_msg = tk.Label(
            self.status_bar,
            text="Pronto para análise.",
            font=("Segoe UI", 9, "bold"),
            bg=BG_SIDEBAR,
            fg=COLOR_ACCENT
        )
        self.lbl_status_msg.pack(side="left", expand=True, pady=8)
        
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
        if total_erros > 0:
            self.lbl_status_msg.config(
                text=f"ANÁLISE: {total_erros} erro(s) léxico(s) detectado(s)!",
                fg=COLOR_ERROR
            )
        else:
            self.lbl_status_msg.config(
                text="ANÁLISE: Sucesso! Nenhum erro léxico detectado.",
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
                
                # Executar análise inicial
                self.executar_analise_lexica()
                self.compilacao_tempo_real()
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
            "  titulo = \"MegaTech - A sua Loja de Eletrônicos\".\n"
            "  cor = \"azul_escuro\".\n"
            "  \n"
            "  secao = \"Promoção de Outono\".\n"
            "  texto = \"Notebooks e periféricos com até 40% de desconto e frete grátis\".\n"
            "  imagem = \"https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=600&q=80\".\n"
            "  botao = \"Garantir Desconto\".\n"
            "  link = \"https://megatech.com/promocoes\".\n"
            "  \n"
            "  secao = \"Fale Conosco\".\n"
            "  texto = \"Dúvidas? Fale com nosso suporte 24 horas por dia\".\n"
            "  botao = \"Iniciar Chat no WhatsApp\".\n"
            "  link = \"https://wa.me/megatech\".\n"
            "}\n"
            "fim\n"
        )
        self.editor.text.delete('1.0', tk.END)
        self.editor.text.insert(tk.END, codigo)
        self.editor.redraw_line_numbers()
        self.atualizar_posicao_cursor(1, 0)
        self.executar_analise_lexica()
        self.compilacao_tempo_real()

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
        self.executar_analise_lexica()
        self.compilacao_tempo_real()

    def ao_mudar_texto(self, event=None):
        """
        Gatilho ativado a cada alteração de caractere no editor de código.
        Executa a análise léxica e a compilação HTML em tempo real.
        """
        # Preservar posição do scroll da saída para evitar pulos de tela indesejados
        scroll_pos = self.saida_text.yview()
        
        # Rodar análise léxica (atualiza a lista à direita e estatísticas)
        self.executar_analise_lexica()
        
        # Tentar atualizar a prévia HTML em memória do servidor local
        self.compilacao_tempo_real()
        
        # Restaurar scroll da lista lateral
        self.saida_text.yview_moveto(scroll_pos[0])

    def executar_analise_lexica(self):
        codigo = self.editor.text.get("1.0", tk.END)
        
        resultado = analisar_codigo(codigo)
        
        self.saida_text.config(state="normal")
        self.saida_text.delete('1.0', tk.END)
        
        tokens_valido = 0
        erros_lexicos = 0
        
        self.saida_text.insert(tk.END, "--- RESULTADO DA ANÁLISE LÉXICA ---\n\n", "titulo")
        
        for msg, tipo in resultado:
            if tipo == "token":
                tokens_valido += 1
                self.saida_text.insert(tk.END, msg + "\n", "token")
            elif tipo == "erro":
                erros_lexicos += 1
                self.saida_text.insert(tk.END, msg + "\n", "erro")
                
        self.atualizar_estatisticas(tokens_valido, erros_lexicos)
        self.saida_text.config(state="disabled")

    def compilacao_tempo_real(self):
        global PREVIEW_HTML, VERSION
        codigo = self.editor.text.get("1.0", tk.END)
        
        html_content, erro = compilar_para_html(codigo)
        
        if not erro:
            # Só atualiza a versão se houver alguma mudança útil
            if html_content != PREVIEW_HTML:
                PREVIEW_HTML = html_content
                VERSION += 1
                self.lbl_status_msg.config(text="Código válido! Prévia em tempo real atualizada.", fg=COLOR_SUCCESS)

    def visualizar_pagina_html(self):
        global PORT
        self.compilacao_tempo_real()
        
        # Abre no navegador no endereço do servidor local
        webbrowser.open(f"http://localhost:{PORT}/")
        self.lbl_status_msg.config(text="Prévia em tempo real aberta no navegador!", fg=COLOR_SUCCESS)

def iniciar_interface():
    root = tk.Tk()
    app = CompiladorApp(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()