from enum import Enum


class ConfidenceLevelEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unsure = "unsure"
