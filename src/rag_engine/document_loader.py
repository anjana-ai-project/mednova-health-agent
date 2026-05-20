from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents(documents_dir: str = "documents") -> tuple[list[str], list[str]]:
    """Returns (chunks, sources) where sources[i] is the filename that chunk i came from."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    all_chunks = []
    all_sources = []
    docs_path = Path(documents_dir)

    for txt_file in sorted(docs_path.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        print(f"{txt_file.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)
        all_sources.extend([txt_file.name] * len(chunks))

    return all_chunks, all_sources


if __name__ == "__main__":
    chunks, sources = load_and_split_documents()
    print(f"\nTotal chunks: {len(chunks)}")
