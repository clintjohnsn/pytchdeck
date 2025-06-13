"""Readers/ Document Loaders."""
import logging
import os
from collections.abc import Callable
from pathlib import Path

from langchain_community.document_loaders import WebBaseLoader
from langgraph.func import task
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.readers.file import DocxReader, MarkdownReader, PyMuPDFReader, RTFReader

from pytchdeck.models.exceptions import NoContentError

logger = logging.getLogger(__name__)

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
    input_dir: str, file_extractor: dict[str, any] = DEFAULT_FILE_EXTRACTOR
) -> ReaderFunc:
    """Return a reader function that reads a file from the input directory."""
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory {input_dir} does not exist or is not a directory.")

    async def read_fn(file_names: list[str]) -> list[Document]:
        """
        Read a file from the input directory.

        Only supports files with extensions in DEFAULT_SUPPORTED_EXTS.
        """
        file_paths = [os.path.join(input_dir, file_name) for file_name in file_names]
        docs: list[Document] = await SimpleDirectoryReader(
            input_dir=input_dir,
            input_files=file_paths,
            file_extractor=file_extractor,
            required_exts=DEFAULT_SUPPORTED_EXTS,
        ).aload_data()
        return docs

    return read_fn

async def read_files(path: Path) -> list[Document]:
    """Read files from a directory."""
    read = local_reader(path)
    docs = await read(os.listdir(path))
    return docs

@task()
async def fetch_content(url: str) -> str:
    """Fetch content from a URL."""
    logger.info(f"Fetching content from url {url}")
    loader = WebBaseLoader(url)
    docs = loader.load()
    if not docs:
        raise NoContentError(f"No content could be fetched from {url}")
    return "\n\n".join(doc.page_content for doc in docs)
