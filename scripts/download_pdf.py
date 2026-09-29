"""Download the assignment eBook from Google Drive."""

from pathlib import Path
import gdown

FILE_ID = "15VLphKcY23_fpYxN62UEQRri_psRVfP9"
OUTPUT = Path("data/Ebook-Agentic-AI.pdf")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
gdown.download(id=FILE_ID, output=str(OUTPUT), quiet=False)
print(f"Saved eBook to {OUTPUT}")
