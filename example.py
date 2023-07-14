import json
from scipdf.parse_pdf import SciPDFParser
from scipdf.models import Article

if __name__ == '__main__':
    parser = SciPDFParser()
    article: Article = parser.parse_pdf('https://www.biorxiv.org/content/biorxiv/early/2018/11/20/463760.full.pdf')

    print(json.dumps(article.dict(), indent=4))
