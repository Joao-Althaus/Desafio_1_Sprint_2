from src.ingestion import ingest
from src.chunking import chunking


# execute the ingestion process to generate the processed data
ingest.main()

# execute the chunking process to generate chunks from the processed data
chunking.main()