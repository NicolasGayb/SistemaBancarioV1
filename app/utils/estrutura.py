import os

# Caminho raiz do seu projeto (ajuste conforme necessário)
ROOT_DIR = r"C:\Projetos\sistemabancariov1"

# Pastas e arquivos a ignorar
IGNORAR_PASTAS = {".git", "__pycache__", ".venv", "env", "venv", ".idea", ".mypy_cache"}
IGNORAR_EXTENSOES = {".db", ".sqlite3", ".log", ".json"}

def print_tree(path, prefix=""):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return

    # filtra somente o que interessa
    items = [
        i for i in items
        if i not in IGNORAR_PASTAS
        and not any(i.endswith(ext) for ext in IGNORAR_EXTENSOES)
    ]

    for index, item in enumerate(items):
        full_path = os.path.join(path, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(full_path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(full_path, prefix + extension)

print(f"📁 Estrutura do projeto: {os.path.basename(ROOT_DIR)}\n")
print_tree(ROOT_DIR)
