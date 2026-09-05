import json
from app.core.config import model
from app.core.logger import logger
from app.core.gemini_utils import log_gemini_error


class RelationshipExtractionService:

    def __init__(self):
        self.cache = {}
        self.quota_exhausted=False

    def extract_relationships(self, text, entities):
        if not text or not text.strip():
            return []

        if not entities:
            return []

        text = text.strip()
        entity_names = [
            entity['name']
            for entity in entities
            if 'name' in entity
        ]

        cache_key = (
            text,
            tuple(sorted(entity_names))
        )

        if cache_key in self.cache:
            logger.info(
                'Relationship extraction cache hit'
            )
            return self.cache[cache_key]

        prompt = f"""
You are a relationship extraction system for an AI Research Assistant.

Extract relationships ONLY between the entities provided below.

ENTITIES:
{entity_names}

TEXT:
{text}

Rules:

1. Use only entities present in the entity list.
2. Use only relationships explicitly supported by the text.
3. Do not invent relationships.
4. Do not use outside knowledge.
5. Return an empty list if no relationship is clearly present.

Return ONLY valid JSON in this format:

[
    {{
        "source": "entity 1",
        "relationship": "relationship name",
        "target": "entity 2"
    }}
]
"""

        try:
            logger.info(
                'Relationship extraction Gemini call started'
            )

            response = model.generate_content(prompt)

            result = response.text.strip()

            if result.startswith("```"):
                result = result.replace("```json", "")
                result = result.replace("```", "")
                result = result.strip()

            relationships = json.loads(result)

            if not isinstance(relationships, list):
                logger.warning(
                    'Relationship extraction did not return a list'
                )
                return []

            valid_relationships = []

            for relationship in relationships:

                if not isinstance(relationship, dict):
                    continue

                source = relationship.get('source')
                relation = relationship.get('relationship')
                target = relationship.get('target')

                if (
                    source in entity_names
                    and target in entity_names
                    and relation
                ):
                    valid_relationships.append({
                        'source': source,
                        'relationship': relation,
                        'target': target
                    })

            self.cache[cache_key] = valid_relationships

            logger.info(
                f'Extracted '
                f'{len(valid_relationships)} valid relationships'
            )

            return valid_relationships

        except Exception as e:
            log_gemini_error(
                'relationship extraction',
                e
            )
            return []

    def extract_relationships_batch(
        self,
        documents,
        entities
    ):
        
        if not documents or not entities:
            return []
        
        valid_documents=[]
        for index,document in enumerate(documents):
            text=document.page_content.strip()
            
            if text:
                valid_documents.append((index,text))
                
        if not valid_documents:
            return []        

        grouped_entities = {}

        for entity in entities:
            if not isinstance(entity,dict):
                continue

            chunk_id = entity.get('chunk')
            name=entity.get('name')

            if chunk_id is None or not name:
                continue

            grouped_entities.setdefault(
                chunk_id,
                []
            ).append(name)

        if not grouped_entities:
            return []
        
        batch_sections=[]
        for chunk_id,text in valid_documents:
            chunk_entities=grouped_entities.get(chunk_id,[])
            
            if not chunk_entities:
                continue
            batch_sections.append(f""" CHUNK{chunk_id}
                                  ENTITIES:
                                  {chunk_entities}
                                  Text:
                                  {text}""")
        
        if not batch_sections:
            return []
        combined_text="\n".join(batch_sections)
        cache_key=('BATCH_RELATIONSHIPS',combined_text)
        

        prompt = f"""
You are a relationship extraction system for an AI Research Assistant.

Extract relationships ONLY between the entities provided below.

IMPORTANT:

- Extract relationships only between entities explicitly
  provided for the corresponding chunk.
- Do not use entities from another chunk.
- Do not invent relationships.
- Do not use outside knowledge.
- Only extract relationships explicitly supported by the text.
- Avoid duplicate relationships.

For every relationship return:

- chunk
- source
- relationship
- target

ENTITIES AND DOCUMENT CHUNKS:

{combined_text}

Return ONLY valid JSON in this format:

[
    {{
        "chunk": 0,
        "source": "entity 1",
        "relationship": "relationship name",
        "target": "entity 2"
    }}
]
"""
        try:

                logger.info(
                    f'Batch relationship extraction Gemini '
                    f'call started for {len(valid_documents)} oocuments'
                )

                response = model.generate_content(
                    prompt
                )
                result = response.text.strip()

                if result.startswith("```"):
                    result = result.replace(
                        "```json",
                        ""
                    )
                    result = result.replace(
                        "```",
                        ""
                    )
                    result = result.strip()

                relationships = json.loads(result)

                if not isinstance(
                    relationships,
                    list
                ):
                    logger.warning(
                        'Relationship extraction did not '
                        'return a list'
                    )
                    return []

                valid_relationships = []
                valid_chunk_ids={index for index,_ in valid_documents}
                
                entity_map={chunk_id:set(names) for chunk_id,names in grouped_entities.items()}
                

                for relationship in relationships:

                    if not isinstance(
                        relationship,
                        dict
                    ):
                        continue
                    
                    chunk_id=relationship.get('chunk')
                    
                    source = relationship.get(
                        'source'
                    )

                    relation = relationship.get(
                        'relationship'
                    )

                    target = relationship.get(
                        'target'
                    )
                    if chunk_id not in valid_chunk_ids:
                        continue
                    chunk_entities=entity_map.get(chunk_id,set())

                    if (
                        source in chunk_entities
                        and target in chunk_entities
                        and relation
                    ):
                        valid_relationships.append({
                            'source': source,
                            'relationship': relation,
                            'target': target
                        })

                self.cache[
                    cache_key
                ] = valid_relationships

                logger.info(f'Batch relationship extraction returned'
                            f'{len(valid_relationships)} valid relationships')
                return valid_relationships

        except Exception as e:

            error_type=log_gemini_error(
                    f'batch relationship extraction ',e)
            if error_type =='quota':
                self.quota_exhausted=True
                logger.warning('Gemini quota exhausted. future graph relationship extraction calls will be skipped')
                return []
          

relationship_extraction_service = (
    RelationshipExtractionService()
)