import os
import pytest

from scipdf.models import Article
from scipdf.parse_pdf import SciPDFParser


def test_parse_pdf():
    # Requires GROBID to be running locally
    try:
        parser = SciPDFParser()
        article: Article = parser.parse_pdf(os.path.join(os.path.dirname(__file__), "../example_data/futoma2017improved.pdf" ))
        assert article.title == 'An Improved Multi-Output Gaussian Process RNN with Real-Time Validation for Early Sepsis Detection'
    except OSError:
        print(" \n GROBID is not running locally, skipping test_parse_pdf")
        pytest.skip("GROBID is not running locally, skipping test_parse_pdf")
