# SciPDF Parser

A Python parser for scientific PDF based on [GROBID](https://github.com/kermitt2/grobid).

## Usage

Run the GROBID using the given bash script first

```bash
bash serve_grobid.sh
```

To parse PDF, use the following function

```python
import scipdf
article_dict = scipdf.parse_pdf_dict('/path_to_pdf/example.pdf')
```

To parse figures from PDF using [pdffigures2](https://github.com/allenai/pdffigures2), you can run

```python
scipdf.parse_figures('path_to_pdf_folder')
```