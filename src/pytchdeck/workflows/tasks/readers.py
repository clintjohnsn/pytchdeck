import os
from collections.abc import Callable
from pathlib import Path

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.readers.file import DocxReader, MarkdownReader, PyMuPDFReader, RTFReader

DEFAULT_SUPPORTED_EXTS: list[str] = [".pdf", ".txt", ".md", ".docx", ".doc", "rtf"]

ReaderFunc = Callable[[str], list[Document]]

DEFAULT_FILE_EXTRACTOR: dict[str, any] = {
    ".pdf": PyMuPDFReader(),
    ".md": MarkdownReader(),
    ".docx": DocxReader(),
    ".doc": RTFReader(),
    "rtf": RTFReader(),
}

def local_reader(
    input_dir: str,
    file_extractor: dict[str, any] = DEFAULT_FILE_EXTRACTOR
) -> ReaderFunc:
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory {input_dir} does not exist or is not a directory.")

    def read_fn(file_name: str) -> list[Document]:
        file_path = os.path.join(input_dir, file_name)
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist in input directory {input_dir}.")
        docs: list[Document] =  SimpleDirectoryReader(
            input_dir=input_dir,
            input_files=[file_path],
            file_extractor=file_extractor,
            required_exts=DEFAULT_SUPPORTED_EXTS,
        ).load_data()
        return docs

    return read_fn
