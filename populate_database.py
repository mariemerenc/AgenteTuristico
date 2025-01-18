import argparse
import os
import shutil
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma


CHROMA_ROOT_PATH = "chroma"  # Caminho principal para armazenar os Chromas
DATA_ROOT_PATH = "pdf"       # Caminho principal contendo as subpastas de cidades


def main():
    # Checa se o banco de dados deve ser limpo (usando a flag --reset).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the databases.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing all Chromas")
        clear_all_databases()

    # Itera sobre cada subpasta dentro da pasta `pdf`, tratando cada subpasta como uma cidade.
    for city_folder in os.listdir(DATA_ROOT_PATH):
        city_path = os.path.join(DATA_ROOT_PATH, city_folder)
        
        # Verifica se é uma subpasta válida.
        if os.path.isdir(city_path):
            print(f"🔄 Processando a cidade: {city_folder}")
            process_city(city_folder, city_path)


def process_city(city_name: str, city_path: str):
    """
    Processa uma subpasta de cidade, criando ou atualizando o Chroma correspondente.
    """
    # Caminho para armazenar o Chroma da cidade.
    chroma_city_path = os.path.join(CHROMA_ROOT_PATH, f"chroma_{city_name}")

    # Cria ou atualiza o Data store para a cidade.
    documents = load_documents(city_path)
    chunks = split_documents(documents)
    add_to_chroma(chunks, chroma_city_path)


def load_documents(city_path: str):
    """
    Carrega documentos PDF da subpasta de uma cidade.
    """
    document_loader = PyPDFDirectoryLoader(city_path)
    return document_loader.load()


def split_documents(documents: list[Document]):
    """
    Divide os documentos em chunks menores.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], chroma_path: str):
    """
    Adiciona ou atualiza os documentos no Chroma específico da cidade.
    """
    # Carrega ou cria um Chroma para a cidade.
    db = Chroma(
        persist_directory=chroma_path, embedding_function=get_embedding_function()
    )

    # Calcula os IDs para os chunks.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Adiciona os documentos que não existem no banco de dados.
    existing_items = db.get(include=[])  # IDs são incluídos por padrão
    existing_ids = set(existing_items["ids"])
    print(f"Número de documentos no banco de dados '{chroma_path}': {len(existing_ids)}")

    # Filtra apenas os chunks novos.
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if len(new_chunks):
        print(f"👉 Adicionando {len(new_chunks)} novo(s) documento(s) ao banco '{chroma_path}'")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # db.persist()  # Persistência automática
    else:
        print(f"✅ Nenhum novo documento para adicionar ao banco '{chroma_path}'")


def calculate_chunk_ids(chunks):
    """
    Calcula IDs únicos para cada chunk com base na fonte e na página.
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # Incrementa o Chunk ID se o Número da Página for igual
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calcula o Chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Adiciona o Chunk ID ao metadata
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_all_databases():
    """
    Remove todos os bancos de dados Chroma existentes.
    """
    if os.path.exists(CHROMA_ROOT_PATH):
        shutil.rmtree(CHROMA_ROOT_PATH)


if __name__ == "__main__":
    main()
