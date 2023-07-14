# SciPDF Parser

A Python parser for scientific PDF based on [GROBID](https://github.com/kermitt2/grobid).

## Installation

Use `pip` to install from this Github repository

```bash
pip install git+https://github.com/skuam/scipdf_parser
```

**Note**
* We also need an `en_core_web_sm` model for spacy, where you can run `python -m spacy download en_core_web_sm` to download it
* You can change GROBID version in `serve_grobid.sh` to test the parser on a new GROBID version

```bash
python -m spacy download en_core_web_sm
```


## Usage

Run the GROBID using the given bash script before parsing PDF

```bash
bash serve_grobid.sh
```

This script will download GROBID and run the service at default port 8070 (see more [here](https://grobid.readthedocs.io/en/latest/Grobid-service/)).
To parse a PDF provided in `example_data` folder or direct URL, use the following function:

```python
import json
from scipdf.parse_pdf import SciPDFParser
from scipdf.models import Article

parser = SciPDFParser()

article:Article = parser.parse_pdf('https://www.biorxiv.org/content/biorxiv/early/2018/11/20/463760.full.pdf')

print(json.dumps(article.dict(), indent = 4))
# output example
{
    "title": "A new method for measuring daytime sleepiness: the Epworth sleepiness scale.",
    "authors": "Murray Johns",
    "pub_date": "1991",
    "abstract": "Text of abstract",
    "sections": [
        {
            "heading": "Introduction",
            "text": "Text of introduction",
            "n_publication_ref": 1,
            "n_figure_ref": 1
        }
    ],
    "references": [
        {
            "title": "The Epworth Sleepiness Scale in Clinical Practice",
            "journal": "Sleep Breath",
            "year": "2017",
            "authors": "Chervin RD, et al."
        },
        {
            "title": "A new method for measuring daytime sleepiness: the Epworth sleepiness scale.",
            "journal": "Sleep",
            "year": "1991",
            "authors": "Johns MW"
        }
    ],
    "figures": [
        {
            "figure_label": "Figure 1",
            "figure_type": "table",
            "figure_id": "fig1",
            "figure_caption": "Caption of figure 1",
            "figure_data": "Data of figure 1"
        }
    ],
    "formulas": [
        {
            "formula_id": "f1",
            "formula_text": "a^2 + b^2 = c^2",
            "formula_coordinates": [
                1,
                2,
                3,
                4
            ]
        }
    ],
    "doi": "10.1111/j.1365-2869.1991.tb00031.x"
}
```

!!! Warning Parsing of figures is not supported yet in pydantic models, so you need to parse it manually. !!!

To parse figures from PDF using [pdffigures2](https://github.com/allenai/pdffigures2), you can run

```python
from scipdf.parse_pdf import SciPDFParser
parser = SciPDFParser()
parser.parse_figures('example_data', output_folder='figures') # folder should contain only PDF files
```

You can see example output figures in `figures` folder.
