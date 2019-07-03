# SciPDF Parser

A Python parser for scientific PDF based on [GROBID](https://github.com/kermitt2/grobid).

## Usage

Run the GROBID using the given bash script before parsing PDF

```bash
bash serve_grobid.sh
```

To parse example PDF provided in `example_data` folder, use the following function:

```python
import scipdf
article_dict = scipdf.parse_pdf_to_dict('example_data/futoma2017improved.pdf') 
```

To parse figures from PDF using [pdffigures2](https://github.com/allenai/pdffigures2), you can run

```python
scipdf.parse_figures('example_data') # folder should contain only PDF files
```