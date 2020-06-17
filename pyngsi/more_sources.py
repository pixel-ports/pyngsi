import openpyxl
import csv

from pathlib import Path

from pyngsi.source import Source, Row


class SourceMicrosoftExcel(Source):

    def __init__(self, filename: str, sheetid: int = 0, sheetname: str = None, ignore: int = 0):
        wb = openpyxl.load_workbook(filename)
        ws = wb[sheetname] if sheetname else wb.worksheets[sheetid]
        self.rows = ws.rows
        self.provider = Path(filename).name
        for _ in range(ignore):  # skip lines
            next(self.rows)

    def __iter__(self):
        for row in self.rows:
            record = ",".join([str(cell.value) if cell.value else "" for cell in row])
            yield Row(self.provider, record)
