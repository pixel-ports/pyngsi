import sys
import time
import random
import openpyxl
import csv


from pathlib import Path
from loguru import logger

from pyngsi.sources.source import Source, Row


class SourceSampleOrion(Source):

    """
    A SourceSampleOrion implements the Source from the NGSI Walkthrough tutorial.

    Please have a look at :
    https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creationhttps://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation

    First two records are those of the tutorial.
    Following records are randomized.
    """

    def __init__(self, count: int = 5, delay: float = 1.0):
        self.count = count if count > 0 else sys.maxsize
        self.delay = delay

    def __iter__(self):
        i: int = 0
        if self.count >= 1:  # 1st element is fixed
            yield Row("orionSample", "Room1;23;720")
            i += 1
            time.sleep(self.delay)
        if self.count >= 2:  # 2nd element is fixed
            yield Row("orionSample", "Room2;21;711")
            i += 1
            time.sleep(self.delay)
        # next elements are randomized
        while i < self.count:
            yield Row("orionSample", f"Room{i%9+1};{round(random.uniform(-10,50), 1)};{random.randint(700,1000)}")
            i += 1
            time.sleep(self.delay)

    def reset(self):
        pass


class SourceMicrosoftExcel(Source):

    def __init__(self, filename, sheetid: int = 0, sheetname: str = None, ignore: int = 0):
        logger.debug(f"{filename=}")
        wb = openpyxl.load_workbook(filename, data_only=True)
        ws = wb[sheetname] if sheetname else wb.worksheets[sheetid]
        self.rows = ws.rows
        self.provider = Path(filename).name
        for _ in range(ignore):  # skip lines
            next(self.rows)

    def __iter__(self):
        for row in self.rows:
            record = ";".join(
                [str(cell.value) if cell.value else "" for cell in row])
            logger.debug(f"{self.provider=}{record=}")
            yield Row(self.provider, record)
