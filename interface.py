import tkinter as tk
from tkinter import filedialog
from lexer import analisar_codigo

def abrir_arquivo():

    caminho = filedialog.askopenfilename(
        filetypes=[("Websimples", "*.ws")]
    )

    if caminho:

        with open(caminho, 'r', encoding='utf-8') as arquivo:
            codigo = arquivo.read()

        entrada.delete('1.0', tk.END)
        entrada.insert(tk.END, codigo)

def executar():

    codigo = entrada.get("1.0", tk.END)

    resultado = analisar_codigo(codigo)

    saida.delete("1.0", tk.END)

    for token in resultado:
        saida.insert(tk.END, token + "\n")

def iniciar_interface():

    global entrada
    global saida

    janela = tk.Tk()

    janela.title("Compilador Websimples")
    janela.geometry("1000x700")
    janela.configure(bg="#1e1e1e")

    titulo = tk.Label(
        janela,
        text="Analisador Léxico - Websimples",
        font=("Arial", 20, "bold"),
        bg="#1e1e1e",
        fg="white"
    )

    titulo.pack(pady=10)

    frame_botoes = tk.Frame(janela, bg="#1e1e1e")
    frame_botoes.pack()

    botao_abrir = tk.Button(
        frame_botoes,
        text="Abrir Arquivo",
        command=abrir_arquivo,
        bg="#4CAF50",
        fg="white",
        width=15
    )

    botao_abrir.pack(side=tk.LEFT, padx=10)

    botao_analisar = tk.Button(
        frame_botoes,
        text="Analisar Código",
        command=executar,
        bg="#2196F3",
        fg="white",
        width=15
    )

    botao_analisar.pack(side=tk.LEFT, padx=10)

    label_entrada = tk.Label(
        janela,
        text="Código Fonte",
        bg="#1e1e1e",
        fg="white",
        font=("Arial", 12, "bold")
    )

    label_entrada.pack(pady=5)

    entrada = tk.Text(
        janela,
        height=15,
        bg="#2d2d2d",
        fg="white",
        insertbackground="white",
        font=("Consolas", 11)
    )

    entrada.pack(fill=tk.BOTH, padx=10, pady=5)

    label_saida = tk.Label(
        janela,
        text="Saída Léxica",
        bg="#1e1e1e",
        fg="white",
        font=("Arial", 12, "bold")
    )

    label_saida.pack(pady=5)

    saida = tk.Text(
        janela,
        height=15,
        bg="black",
        fg="#00ff00",
        font=("Consolas", 11)
    )

    saida.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    janela.mainloop()