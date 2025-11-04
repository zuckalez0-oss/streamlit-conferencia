import tkinter as tk
from tkinter import filedialog, messagebox
import glob
import os

def gerar_lista_de_arquivos():
    """
    Abre uma interface gráfica para o usuário selecionar uma pasta
    e gera um 'lista_arquivos.txt' contendo todos os arquivos .pdf
    encontrados nessa pasta.
    """
    # 1. Configura a janela principal (invisível)
    root = tk.Tk()
    root.withdraw() # Esconde a janela root principal

    # 2. Abre a caixa de diálogo para selecionar a pasta
    messagebox.showinfo(
        "Gerador de Lista", 
        "Por favor, selecione a pasta onde seus pedidos (arquivos .pdf) estão localizados."
    )
    
    directory_path = filedialog.askdirectory(title="Selecione a pasta dos Pedidos PDF")

    # 3. Verifica se o usuário selecionou uma pasta
    if directory_path:
        try:
            # Define o caminho completo do arquivo de saída
            output_file_path = os.path.join(directory_path, "lista_arquivos.txt")
            
            # 4. Define o padrão de busca para encontrar todos os arquivos .pdf
            search_pattern = os.path.join(directory_path, "*.pdf")
            
            # 5. Usa glob para encontrar todos os arquivos e extrai apenas o nome
            pdf_files = [os.path.basename(f) for f in glob.glob(search_pattern)]

            # 6. Escreve a lista de nomes no arquivo .txt
            with open(output_file_path, 'w', encoding='utf-8') as f:
                for file in pdf_files:
                    f.write(f"{file}\n")
            
            # 6. Mostra mensagem de sucesso
            messagebox.showinfo(
                "Sucesso", 
                f"'lista_arquivos.txt' foi criado com sucesso!\n\n"
                f"{len(pdf_files)} arquivos PDF foram encontrados e listados.\n\n"
                "Pode fechar esta janela e carregar o arquivo no Streamlit."
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o arquivo: {e}")
    else:
        # 7. Mostra mensagem se o usuário cancelar a seleção da pasta
        messagebox.showinfo("Operação Cancelada", "Nenhuma pasta foi selecionada. A operação foi cancelada.")

if __name__ == "__main__":
    gerar_lista_de_arquivos()
