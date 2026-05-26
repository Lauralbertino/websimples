import zipfile
import os

files_to_zip = [
    "main.py",
    "lexer.py",
    "interface.py",
    "tokens.py",
    "requirements.txt",
    "exemplo1.ws",
    "exemplos.ws",
    "README.txt",
    "relatorio_etapa_bibliotecas.txt",
    "test_lexer.py",
    "README.pdf"
]

def create_zip():
    zip_filename = "websimples_compilador.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file} to zip.")
            else:
                print(f"Warning: {file} not found.")
                
    print(f"\nCreated {zip_filename} successfully!")

if __name__ == "__main__":
    create_zip()
