import warnings

import numpy as np
import pandas as pd
import spacy
import textstat
from bs4 import BeautifulSoup
from spacy.tokens import Doc

from scipdf.models import ReadabilityStats, TextStats, JournalFeatures

nlp = spacy.load("en_core_web_sm")

PRESENT_TENSE_VERB_LIST = ["VB", "VBP", "VBZ", "VBG"]
VERB_LIST = ["VB", "VBP", "VBZ", "VBG", "VBN", "VBD"]
NOUN_LIST = ["NNP", "NNPS"]

SECTIONS_MAPS = {
    "Authors": "Authors",
    "AUTHORS": "AUTHORS",
    "Abstract": "Abstract",
    "ABSTRACT": "Abstract",
    "Date": "Date",
    "DATE": "DATE",
    "INTRODUCTION": "Introduction",
    "MATERIALS AND METHODS": "Methods",
    "Materials and methods": "Methods",
    "METHODS": "Methods",
    "RESULTS": "Results",
    "CONCLUSIONS": "Conclusions",
    "CONCLUSIONS AND FUTURE APPLICATIONS": "Conclusions",
    "DISCUSSION": "Discussion",
    "ACKNOWLEDGMENTS": "Acknowledgement",
    "TABLES": "Tables",
    "Tabnles": "Tables",
    "DISCLOSURE": "Disclosure",
    "CONFLICT OF INTEREST": "Disclosure",
    "Acknowledgement": "Acknowledgements",
}


def compute_readability_stats(text) -> ReadabilityStats:
    """
    Compute reading statistics of the given text
    Reference: https://github.com/shivam5992/textstat

    Parameters
    ==========
    text: str, input section or abstract text
    """
    functions = {
        "flesch_reading_ease": textstat.flesch_reading_ease,
        "smog": textstat.smog_index,
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade,
        "coleman_liau_index": textstat.coleman_liau_index,
        "automated_readability_index": textstat.automated_readability_index,
        "dale_chall": textstat.dale_chall_readability_score,
        "difficult_words": textstat.difficult_words,
        "linsear_write": textstat.linsear_write_formula,
        "gunning_fog": textstat.gunning_fog,
        "text_standard": textstat.text_standard,
        "n_syllable": textstat.syllable_count,
        "avg_letter_per_word": textstat.avg_letter_per_word,
        "avg_sentence_length": textstat.avg_sentence_length,
    }

    readability_dict = {}

    for key, function in functions.items():
        try:
            readability_dict[key] = function(text)
        except Exception:
            readability_dict[key] = None

    return ReadabilityStats(**readability_dict)


from collections import Counter


def count_pos(text):
    return dict(Counter([token.pos_ for token in text]))


def count_pos_tag(text):
    return dict(Counter([token.tag_ for token in text]))


def sum_present_verb(pos_tag):
    return sum([v for k, v in pos_tag.items() if k in PRESENT_TENSE_VERB_LIST])


def sum_verb(pos_tag):
    return sum([v for k, v in pos_tag.items() if k in VERB_LIST])


def count_word_shape(text):
    return dict(Counter([token.shape_ for token in text]))


def count_digits(text):
    return sum([token.is_digit or token.like_num for token in text])


def compute_text_stats(text):
    """
    Compute part of speech features from a given spacy wrapper of text

    Parameters
    ==========
    text: spacy.tokens.doc.Doc, spacy wrapper of the section or abstract text

    Output
    ======
    text_stats: TextStats, part of speech and text features extracted from the given text
    """
    spacy_text: Doc = nlp(text)
    text_stats_dict = {}
    functions = [
        (count_pos, "pos"),
        (count_pos_tag, "pos_tag"),
        (count_word_shape, "word_shape"),
        (count_digits, "n_digits"),
    ]
    for function, key in functions:
        try:
            text_stats_dict[key] = function(spacy_text)
        except Exception:
            text_stats_dict[key] = None
    try:
        pos_tag = text_stats_dict.get("pos_tag", {})
        text_stats_dict["n_present_verb"] = sum_present_verb(pos_tag)
        text_stats_dict["n_verb"] = sum_verb(pos_tag)
    except Exception:
        text_stats_dict["n_present_verb"] = None
        text_stats_dict["n_verb"] = None
    # Use spacy to parse the text

    n_word_per_sents = [len([token for token in sent]) for sent in spacy_text.sents]
    text_stats_dict["n_word"] = sum(n_word_per_sents)
    text_stats_dict["n_sents"] = len(n_word_per_sents)
    text_stats_dict["percent_digits"] = (
        text_stats_dict["n_digits"] / text_stats_dict["n_word"]
        if text_stats_dict["n_word"] > 0
        else None
    )
    text_stats_dict["n_word_per_sents"] = n_word_per_sents
    text_stats_dict["avg_word_per_sents"] = np.mean(n_word_per_sents)

    return TextStats(**text_stats_dict)


def filter_valid_years(years):
    return [year for year in years if year.isdigit() and int(year) in range(1800, 2100)]


def compute_journal_features(soup: BeautifulSoup):
    """
    Parse features about journal references from a given dictionary of parsed article

    Parameters
    ==========
    soup: dict, article dictionary parsed from GROBID and converted to dictionary

    Output
    ======
    journal_features: JournalFeatures, features about journal references
    """
    functions = [
        ("n_reference", lambda: len(soup.get("references", []))),
        ("n_unique_journals", lambda: len(pd.unique([a.get("journal") for a in soup.get("references", [])]))),
        ("avg_ref_year", lambda: np.mean(filter_valid_years([a.get("year") for a in soup.get("references", [])]))),
        ("median_ref_year", lambda: np.median(filter_valid_years([a.get("year") for a in soup.get("references", [])]))),
        ("min_ref_year", lambda: np.min(filter_valid_years([a.get("year") for a in soup.get("references", [])])), ),
        ("max_ref_year", lambda: np.max(filter_valid_years([a.get("year") for a in soup.get("references", [])]))),
    ]

    journal_features_dict = {}
    failed_functions = []

    for key, function in functions:
        try:
            journal_features_dict[key] = function()
        except Exception:
            failed_functions.append(key)

    if failed_functions:
        warnings.warn(f"The following functions failed: {failed_functions}")

    return JournalFeatures(**journal_features_dict)
