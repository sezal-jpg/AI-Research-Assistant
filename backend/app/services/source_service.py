class SourceService:

    def build_sources(
        self,
        docs,
    ):

        sources = []

        for doc in docs:
            source_file=doc.metadata.get('source_file')
            source_url=doc.metadata.get('source_url')
            
            if source_file:

                page = doc.metadata.get("page", 0)

                sources.append(
                    {
                        "type": "file",
                        "pdf": source_file,
                        "page": int(page) + 1,
                    }
                )

            elif source_url:

                sources.append(
                    {
                        "type": "website",
                        "url": source_url,
                    }
                ) 

        unique_sources = []

        seen = set()

        for source in sources:
            if source['type']=='file':
             key = ('file',
                source["pdf"],
                source["page"],
            )
            else:
                key=('website',source['url'],)
                
            if key not in seen:

                unique_sources.append(source)

                seen.add(key)

        return unique_sources


source_service = SourceService()