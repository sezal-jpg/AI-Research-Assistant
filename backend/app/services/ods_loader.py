import pandas as pd
from pathlib import Path
from langchain_core.documents import Document
from app.core.logger import logger

class OdsLoader:

    def load(self, file_path: Path):
        logger.info(f"Loading ODS: {file_path.name}")

        docs = []
        excel_file = pd.ExcelFile(
            file_path,
            engine="odf" )

        try:
            for sheet_name in excel_file.sheet_names:
                dataframe = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    engine="odf"
                )

                content = dataframe.to_string(
                    index=False
                )

                if content.strip():
                    docs.append(
                        Document(
                            page_content=content,
                            metadata={
                                "source_file": file_path.name,
                                "source_type": "ods",
                                "sheet": sheet_name,
                            },
                        ) )

        finally:
            excel_file.close()

        logger.info(
            f"Loaded {len(docs)} ODS sheets" )

        return docs

ods_loader = OdsLoader()