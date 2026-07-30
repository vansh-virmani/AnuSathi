from pathlib import Path
import warnings
import logging

import pdfplumber
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

# Suppress unnecessary warnings from pypdf and langchain config change old warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("pypdf").setLevel(logging.ERROR)


def load_pdf(file_path: str) -> list[Document]:
    """
    Load a single PDF using LangChain's PyPDFLoader.

    If any page has no extracted text, fall back to pdfplumber
    for only that specific page.

    Returns:
        list[Document]: One Document object per page.
        Document is like a class which contains->{metadata,page_content}
    """

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    repaired_pages = 0

    for document in documents:

        # Skip pages that already contain text
        if document.page_content.strip():
            continue

        page_number = document.metadata["page"]      # 0-indexed
        source_file = document.metadata["source"]

        try:
            with pdfplumber.open(source_file) as pdf:  #returns object

                fallback_text = (
                    pdf.pages[page_number].extract_text()
                    or ""
                )

            if fallback_text.strip():
                document.page_content = fallback_text
                repaired_pages += 1

        except Exception as e:
            print(
                f"Failed to repair "
                f"{Path(source_file).name} "
                f"(Page {page_number + 1}): {e}"
            )

    

    return documents


if __name__ == "__main__":  #development phase only not for users checking if loading works

    pdf_path = r"Data/Papers/NIPS-2017-attention-is-all-you-need-Paper.pdf"

    documents = load_pdf(pdf_path)

    print(f"\nSuccessfully loaded {len(documents)} pages.")