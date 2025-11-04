import os
import glob
import time

print("--- Gerador de Lista de Arquivos PDF ---")
print("\nPor favor, copie e cole o caminho completo da sua pasta de pedidos.")
print(r"Exemplo: C:\Users\SeuUsuario\Documentos\Pedidos\2025\Novembro\OP")

# 1. Pede o caminho da pasta ao usuário
folder_path = input("\nCole o caminho da pasta aqui e pressione Enter: ")

# 2. Verifica se o caminho é válido
if not os.path.isdir(folder_path):
    print(f"\nERRO: O caminho '{folder_path}' não foi encontrado ou não é uma pasta.")
    print("Por favor, rode o script novamente e insira um caminho válido.")
    time.sleep(5)
    exit()

try:
    # 3. Define o caminho completo do arquivo de saída (dentro da pasta informada)
    output_file_path = os.path.join(folder_path, "lista_arquivos.txt")
    
    # 4. Define o padrão de busca para encontrar todos os arquivos .pdf
    search_pattern = os.path.join(folder_path, "*.pdf")
    
    # 5. Usa glob para encontrar todos os arquivos que correspondem ao padrão
    pdf_files = glob.glob(search_pattern)
    
    # 6. Extrai apenas o nome do arquivo (ex: "03_11_460317_P.pdf")
    pdf_filenames = [os.path.basename(f) for f in pdf_files]

    # 7. Escreve a lista de nomes no arquivo .txt
    with open(output_file_path, "w", encoding="utf-8") as f:
        for name in pdf_filenames:
            f.write(name + "\n")
            
    print(f"\nSUCESSO! {len(pdf_filenames)} arquivos PDF encontrados.")
    print(f"O arquivo 'lista_arquivos.txt' foi criado (ou atualizado) em:")
    print(f"{output_file_path}")
    print("\nAgora você pode carregar este arquivo 'lista_arquivos.txt' no seu aplicativo Streamlit.")

except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")

# 8. Pausa para o usuário ler a mensagem
print("\nEsta janela fechará em 10 segundos...")
time.sleep(10)
