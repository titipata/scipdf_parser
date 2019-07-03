import numpy as np
import pandas as pd
import textstat
import spacy
from collections import Counter


nlp = spacy.load('en_core_web_sm')

PRESENT_TENSE_VERB_LIST = ['VB', 'VBP', 'VBZ', 'VBG']
VERB_LIST = ['VB', 'VBP', 'VBZ', 'VBG', 'VBN', 'VBD']
NOUN_LIST = ['NNP', 'NNPS']


def compute_readability_stats(text):
    """
    Compute reading statistics of the given text
    Reference: https://github.com/shivam5992/textstat
    Parameters
    ==========
    text: str, input section or abstract text
    """
    return {
        'flesch_reading_ease': textstat.flesch_reading_ease(text),
        'smog': textstat.smog_index(text),
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
        'coleman_liau_index': textstat.coleman_liau_index(text),
        'automated_readability_index': textstat.automated_readability_index(text),
        'dale_chall': textstat.dale_chall_readability_score(text),
        'difficult_words': textstat.difficult_words(text),
        'linsear_write': textstat.linsear_write_formula(text),
        'gunning_fog': textstat.gunning_fog(text),
        'text_standard': textstat.text_standard(text), 
        'n_syllable': textstat.syllable_count(text),
        'avg_letter_per_word': textstat.avg_letter_per_word(text),
        'avg_sentence_length': textstat.avg_sentence_length(text)
    }


def compute_text_stats(text):
    """
    Compute text 
    Parameters
    ==========
    text: spacy.tokens.doc.Doc, spacy wrapper of the section or abstract text
    Output
    ======
    text_stat: dict, part of speech and text features extracted from the given text
    """
    pos = dict(Counter([token.pos_ for token in text]))
    pos_tag = dict(Counter([token.tag_ for token in text])) # detailed part-of-speech

    n_present_verb = sum([v for k, v in pos_tag.items() if k in PRESENT_TENSE_VERB_LIST])
    n_verb = sum([p for p in pos_tag if p in VERB_LIST])

    word_shape = dict(Counter([token.shape_ for token in text])) # word shape
    n_word_per_sents = [len([token for token in sent]) for sent in text.sents]
    n_digits = sum([token.is_digit or token.like_num for token in text])
    n_word = sum(n_word_per_sents)
    n_sents = len(n_word_per_sents)
    return {
        'pos': pos,
        'pos_tag': pos_tag,
        'word_shape': word_shape,
        'n_word': n_word,
        'n_sents': n_sents,
        'n_present_verb': n_present_verb,
        'n_verb': n_verb,
        'n_digits': n_digits,
        'percent_digits': n_digits / n_word,
        'n_word_per_sents': n_word_per_sents,
        'avg_word_per_sents': np.mean(n_word_per_sents)
    }


def compute_journal_features(article):
    """
    Parameters
    ==========
    article: dict, article dictionary parsed from GROBID and converted to dictionary
        see ``parse_metadata.py`` for the detail
    Output
    ======
    reference_dict: dict, dictionary of 
    """
    n_reference = len(article['references'])
    n_unique_journals = len(pd.unique([a['journal'] for a in article['references']]))
    reference_years = []
    for reference in article['references']:
        year = reference['year']
        if year.isdigit():
            # filter outliers
            if int(year) in range(1800, 2100):
                reference_years.append(int(year))
    avg_ref_year = np.mean(reference_years)
    median_ref_year = np.median(reference_years)
    min_ref_year = np.min(reference_years)
    max_ref_year = np.max(reference_years)
    return {
        'n_reference': n_reference,
        'n_unique_journals': n_unique_journals,
        'avg_ref_year': avg_ref_year,
        'median_ref_year': median_ref_year,
        'min_ref_year': min_ref_year,
        'max_ref_year': max_ref_year
    }