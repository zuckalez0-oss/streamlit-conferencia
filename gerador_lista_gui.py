import tkinter as tk
from tkinter import filedialog, messagebox
import os

def gerar_lista_de_arquivos():
    '''
    Abre uma interface gráfica para o usuário selecionar uma pasta de ENTRADA (PDFs)
    e uma pasta de SAÍDA (onde o .txt será salvo).
    '''
    # 1. Configura a janela principal (invisível)
    root = tk.Tk()
    root.withdraw() # Esconde a janela root principal

    # 2. Abre a caixa de diálogo para selecionar a pasta de ENTRADA (PDFs)
    messagebox.showinfo(
        "Gerador de Lista (Passo 1/2)", 
        "Por favor, selecione a pasta de ENTRADA onde seus pedidos (arquivos .pdf) estão localizados."
    )
    input_directory_path = filedialog.askdirectory(title="Selecione a pasta dos Pedidos PDF (ENTRADA)")

    # 3. Verifica se o usuário selecionou a pasta de entrada
    if not input_directory_path:
        messagebox.showinfo("Operação Cancelada", "Nenhuma pasta de entrada foi selecionada. A operação foi cancelada.")
        return # Encerra a função

    # 4. Abre a caixa de diálogo para selecionar a pasta de SAÍDA (Relatório .txt)
    messagebox.showinfo(
        "Gerador de Lista (Passo 2/2)", 
        "Agora, selecione a pasta de SAÍDA onde o arquivo 'lista_arquivos.txt' deve ser salvo (ex: sua Área de Trabalho)."
    )
    output_directory_path = filedialog.askdirectory(title="Selecione a pasta para salvar o Relatório (SAÍDA)")

    # 5. Verifica se o usuário selecionou a pasta de saída
    if not output_directory_path:
        messagebox.showinfo("Operação Cancelada", "Nenhuma pasta de saída foi selecionada. A operação foi cancelada.")
        return # Encerra a função

    # 6. Se ambas as pastas foram selecionadas, processa os arquivos
    try:
        output_file = os.path.join(output_directory_path, "lista_arquivos.txt")
        pdf_files = []
        
        # 7. Varre a pasta de ENTRADA
        for filename in os.listdir(input_directory_path):
            # Procura por .pdf (ignorando maiúsculas/minúsculas)
            if filename.lower().endswith('.pdf'):
                pdf_files.append(filename)
        
        # 8. Escreve os arquivos encontrados no .txt na pasta de SAÍDA
        with open(output_file, 'w', encoding='utf-8') as f:
            for file in pdf_files:
                f.write(f"{file}\n")
        
        # 9. Mostra mensagem de sucesso
        messagebox.showinfo(
            "Sucesso", 
            f"'lista_arquivos.txt' foi criado com sucesso!\n\n"
            f"{len(pdf_files)} arquivos PDF foram encontrados e listados.\n\n"
            f"O arquivo foi salvo em: {output_file}\n\n"
            f"Pode fechar esta janela e carregar o arquivo no Streamlit."
        )
        
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o arquivo: {e}")

if __name__ == "__main__":
    gerar_lista_de_arquivos()
