from app.core.logger import logger
from app.services.entity_extraction_service import (
    entity_extraction_service
)
from app.services.relationship_extraction_service import (
    relationship_extraction_service
)
from app.services.graph_service import graph_service


class GraphConstructionService:

    def __init__(self):
        self.processed_chunks = set()
        self.batch_size = 4

    def build_from_document(self, document):

        text = document.page_content

        if not text or not text.strip():
            return

        text = text.strip()

        if text in self.processed_chunks:
            logger.info(
                'Graph construction skipped: '
                'chunk already processed'
            )
            return

        logger.info(
            'Building graph from document chunk'
        )

        entities = (
            entity_extraction_service
            .extract_entities(text)
        )

        if not entities:
            logger.info(
                'No entities extracted '
            )

            self.processed_chunks.add(text)
            return

        graph_service.add_entities(
            entities
        )

        relationships = (
            relationship_extraction_service
            .extract_relationships(
                text,
                entities
            )
        )

        graph_service.add_relationships(
            relationships
        )

        self.processed_chunks.add(text)

        logger.info(
            f'Graph construction completed: '
            f'{len(entities)} entities, '
            f'{len(relationships)} relationships'
        )

    def build_from_documents(self, documents):

        if not documents:
            logger.warning(
                'No documents available '
                'for graph construction'
            )
            return

        logger.info(
            f'Batch graph construction started '
            f'for {len(documents)} chunks'
        )

        unique_documents = []

        for document in documents:

            text = document.page_content

            if not text or not text.strip():
                continue

            text = text.strip()

            if text in self.processed_chunks:
                logger.info(
                    'Skipping already processed chunk'
                )
                continue

            unique_documents.append(
                document
            )

        if not unique_documents:
            logger.info(
                'All chunks were already processed'
            )
            return

        for start in range(
            0,
            len(unique_documents),
            self.batch_size
        ):

            batch = unique_documents[
                start:start + self.batch_size
            ]

            logger.info(
                f'Processing graph batch '
                f'{start // self.batch_size + 1} '
                f'with {len(batch)} chunks'
            )

            entities = (
                entity_extraction_service
                .extract_entities_batch(
                    batch
                )
            )

            if not entities:
                logger.warning(
                    'No entities extracted '
                    'for current graph batch'
                )

                for document in batch:
                    self.processed_chunks.add(
                        document.page_content.strip()
                    )

                continue
            clean_entities = []

            for entity in entities:

                clean_entities.append({
                    'name': entity['name'],
                    'type': entity['type']
                })

            graph_service.add_entities(
                clean_entities
            )

            relationships = (
                relationship_extraction_service
                .extract_relationships_batch(
                    batch,
                    entities
                )
            )

            graph_service.add_relationships(
                relationships
            )

            for document in batch:
                self.processed_chunks.add(
                    document.page_content.strip()
                )

            logger.info(
                f'Graph batch completed: '
                f'{len(entities)} entities, '
                f'{len(relationships)} relationships'
            )

        logger.info(
            'Batch graph construction completed'
        )


graph_construction_service = (
    GraphConstructionService()
)