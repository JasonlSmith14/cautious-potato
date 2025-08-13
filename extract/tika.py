from typing import List
from tika import parser

from extract.parser import Parser


class TikaParser(Parser):
    def __init__(self):
        pass

    def parse_document(self, file_path: str) -> str:
        parsed = parser.from_file(file_path)
        return parsed.get("content", "")

    def parse_documents(self, file_paths: List[str]) -> List[str]:
        files = []
        for file_path in file_paths:
            parsed = parser.from_file(file_path)
            files.append(parsed.get("content", ""))

        return files


if __name__ == "__main__":
    tika_parser = TikaParser()

    files = tika_parser.parse_files(["data/test.pdf"])

    print(files)
