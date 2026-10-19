import argparse
import hashlib
from pathlib import Path
import fitz
from backend.app.services.pinecone_service import ensure_index
from backend.app.services.groqai_service import embed
from backend.app.services.kb_service import search_kb


def chunks(text, chunk_size=1100, overlap=180):
    """
    Splits the text into chunks of specified size with overlap.
    """
    text = ' '.join(text.split())
    step = chunk_size - overlap
    return (text[i:i + chunk_size] for i in range(0, len(text), step) if len(text[i:i + chunk_size]) > 80)
   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', default='data/medical_book.pdf')
    args = parser.parse_args()
    pdf = Path(args.pdf)
    if not pdf.exists():
        raise SystemExit(f'PDF not found: {pdf}')
    index = ensure_index()
    with fitz.open(pdf) as doc:
        batch = []
        for page_number, page in enumerate(doc, start=1):
            for part, content in enumerate(chunks(page.get_text()), start=1):
                key = hashlib.sha256(f'{pdf.name}:{page_number}:{part}:{content}'.encode()).hexdigest()
                batch.append((key,content,{'page':page_number,'text':content,'file':pdf.name}))
                if len(batch) >= 50:
                    vectors = embed([b[1] for b in batch])
                    index.upsert(vectors=[{'id':b[0],'values':v,'metadata':b[2]} for b,v in zip(batch,vectors)])
                    batch=[]
            if page_number % 50 == 0:
                print(f'Indexed pages: {page_number}/{len(doc)}',flush=True)
        if batch:
            vectors=embed([b[1] for b in batch])
            index.upsert(vectors=[{'id':b[0],'values':v,'metadata':b[2]} for b,v in zip(batch,vectors)])
    print('Ingestion complete')
if __name__ == '__main__': main()