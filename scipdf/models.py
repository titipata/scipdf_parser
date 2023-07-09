"""
All Pydantic models for the scipdf package.
"""
from typing import Optional

from pydantic import BaseModel


# Text Stats models
class ReadabilityStats(BaseModel):
    flesch_reading_ease: Optional[float]
    smog: Optional[float]
    flesch_kincaid_grade: Optional[float]
    coleman_liau_index: Optional[float]
    automated_readability_index: Optional[float]
    dale_chall: Optional[float]
    difficult_words: Optional[int]
    linsear_write: Optional[float]
    gunning_fog: Optional[float]
    text_standard: Optional[str]
    n_syllable: Optional[int]
    avg_letter_per_word: Optional[float]
    avg_sentence_length: Optional[float]


class TextStats(BaseModel):
    pos: dict
    pos_tag: dict
    word_shape: dict
    n_word: int
    n_sents: int
    n_present_verb: Optional[int]
    n_verb: Optional[int]
    n_digits: int
    percent_digits: float
    n_word_per_sents: list
    avg_word_per_sents: float


class JournalFeatures(BaseModel):
    n_reference: Optional[int]
    n_unique_journals: Optional[int]
    avg_ref_year: Optional[float]
    median_ref_year: Optional[float]
    min_ref_year: Optional[int]
    max_ref_year: Optional[int]


class TextStatistic(BaseModel):
    readability: ReadabilityStats
    text_stats: TextStats
    journal_features: JournalFeatures


# Text content models
class Section(BaseModel):
    heading: Optional[str]
    text: str
    n_publication_ref: int
    n_figure_ref: int

    @property
    def full_text(self):
        return self.heading + "\n" + self.text


class Reference(BaseModel):
    title: str
    journal: str
    year: Optional[str]
    authors: str


class Figure(BaseModel):
    figure_label: str
    figure_type: str
    figure_id: str
    figure_caption: str
    figure_data: str


class Formula(BaseModel):
    formula_id: str
    formula_text: str
    formula_coordinates: list


class Article(BaseModel):
    title: str
    authors: str
    pub_date: str
    abstract: str
    sections: list[Section]
    references: list[Reference]
    figures: list[Figure]
    formulas: list[Formula]
    doi: str
    text_stats: Optional[TextStatistic]

    @property
    def full_text(self) -> str:
        return "\n\n".join([section.full_text for section in self.sections])
