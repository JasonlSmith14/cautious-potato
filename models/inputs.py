from typing import List
from sqlmodel import SQLModel

from models.information import TrackedCategoryInformation, TrackedParsedInformation


class ParsedInformationInputs(SQLModel):
    parsed_information_inputs: List[TrackedParsedInformation]


class CategoryInformationInputs(SQLModel):
    category_information_inputs: List[TrackedCategoryInformation]
