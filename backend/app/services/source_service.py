class SourceService:

    def build_sources(
        self,
        docs,
    ):

        sources = []

        for doc in docs:

            sources.append(
                {
                    "pdf": doc.metadata.get(
                        "source_file",
                        "Unknown PDF",
                    ),
                    "page": doc.metadata.get(
                        "page",
                        0,
                    )
                    + 1,
                }
            )

        unique_sources = []

        seen = set()

        for source in sources:

            key = (
                source["pdf"],
                source["page"],
            )

            if key not in seen:

                unique_sources.append(source)

                seen.add(key)

        return unique_sources


source_service = SourceService()