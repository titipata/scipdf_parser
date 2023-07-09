import re
from glob import glob
from os import path as op

from bs4 import BeautifulSoup, NavigableString

from scipdf.features import compute_readability_stats, compute_text_stats, compute_journal_features
from scipdf.models import Section, Reference, Figure, Formula, Article, TextStatistic


def list_pdf_paths(pdf_folder: str):
    """
    list of pdf paths in pdf folder
    """
    return glob(op.join(pdf_folder, "*", "*", "*.pdf"))


def validate_url(path: str):
    """
    Validate a given ``path`` if it is URL or not
    """
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, path) is not None


def parse_authors(article: BeautifulSoup) -> str:
    """
    Parse authors from a given BeautifulSoup of an article
    """
    author_names = article.find("sourcedesc").findAll("persname")
    authors = []
    for author in author_names:
        firstname = author.find("forename", {"type": "first"})
        firstname = firstname.text.strip() if firstname is not None else ""
        middlename = author.find("forename", {"type": "middle"})
        middlename = middlename.text.strip() if middlename is not None else ""
        lastname = author.find("surname")
        lastname = lastname.text.strip() if lastname is not None else ""
        if middlename != "":
            authors.append(firstname + " " + middlename + " " + lastname)
        else:
            authors.append(firstname + " " + lastname)
    authors = "; ".join(authors)
    return authors


def parse_date(article: BeautifulSoup) -> str:
    """
    Parse date from a given BeautifulSoup of an article
    """
    pub_date = article.find("publicationstmt")
    year = pub_date.find("date")
    year = year.attrs.get("when") if year is not None else ""
    return year


def parse_abstract(article: BeautifulSoup) -> str:
    """
    Parse abstract from a given BeautifulSoup of an article
    """
    div = article.find("abstract")
    abstract = ""
    for p in list(div.children):
        if not isinstance(p, NavigableString) and len(list(p)) > 0:
            abstract += " ".join(
                [elem.text for elem in p if not isinstance(elem, NavigableString)]
            )
    return abstract


def calculate_number_of_references(div):
    """
    For a given section, calculate number of references made in the section
    """
    n_publication_ref = len(
        [ref for ref in div.find_all("ref") if ref.attrs.get("type") == "bibr"]
    )
    n_figure_ref = len(
        [ref for ref in div.find_all("ref") if ref.attrs.get("type") == "figure"]
    )
    return {"n_publication_ref": n_publication_ref, "n_figure_ref": n_figure_ref}


def parse_sections(article: BeautifulSoup) -> list[str]:
    """
    Parse list of sections from a given BeautifulSoup of an article

    Parameters
    ==========
    as_list: bool, if True, output text as a list of paragraph instead
        of joining it together as one single text
    """
    article_text = article.find("text")
    divs = article_text.find_all("div", attrs={"xmlns": "http://www.tei-c.org/ns/1.0"})
    sections: list[str] = []
    for div in divs:
        div_list = list(div.children)
        if len(div_list) == 0:
            heading = ""
            text = ""
        elif len(div_list) == 1:
            if isinstance(div_list[0], NavigableString):
                heading = str(div_list[0])
                text = ""
            else:
                heading = ""
                text = div_list[0].text
        else:
            text = []
            heading = div_list[0]
            if isinstance(heading, NavigableString):
                heading = str(heading)
                p_all = list(div.children)[1:]
            else:
                heading = ""
                p_all = list(div.children)
            for p in p_all:
                if p is not None:
                    try:
                        text.append(p.text)
                    except:
                        pass
            text = " ".join(text)

        if heading != "" or text != "":
            ref_dict = calculate_number_of_references(div)
            sections.append(
                Section(
                    heading=heading,
                    text=text,
                    n_publication_ref=ref_dict["n_publication_ref"],
                    n_figure_ref=ref_dict["n_figure_ref"],
                )
            )
    return sections


def parse_references(article: BeautifulSoup) -> list[Reference]:
    """
    Parse list of references from a given BeautifulSoup of an article
    """
    references = article.find("text").find("div", attrs={"type": "references"})
    references = references.find_all("biblstruct") if references is not None else []
    reference_list = []
    for reference in references:
        title = reference.find("title", attrs={"level": "a"})
        if title is None:
            title = reference.find("title", attrs={"level": "m"})
        title = title.text if title is not None else ""
        journal = reference.find("title", attrs={"level": "j"})
        journal = journal.text if journal is not None else ""
        if journal == "":
            journal = reference.find("publisher")
            journal = journal.text if journal is not None else ""
        year = reference.find("date")
        year = year.attrs.get("when")
        authors = []
        for author in reference.find_all("author"):
            firstname = author.find("forename", {"type": "first"})
            firstname = firstname.text.strip() if firstname is not None else ""
            middlename = author.find("forename", {"type": "middle"})
            middlename = middlename.text.strip() if middlename is not None else ""
            lastname = author.find("surname")
            lastname = lastname.text.strip() if lastname is not None else ""
            if middlename != "":
                authors.append(firstname + " " + middlename + " " + lastname)
            else:
                authors.append(firstname + " " + lastname)
        authors = "; ".join(authors)
        reference_list.append(
            Reference(title=title, journal=journal, year=year, authors=authors)
        )
    return reference_list


def parse_figure_caption(article: BeautifulSoup) -> list[Figure]:
    """
    Parse list of figures/tables from a given BeautifulSoup of an article
    """
    figures_list = []
    figures = article.find_all("figure")
    for figure in figures:
        figure_type = figure.attrs.get("type") or ""
        figure_id = figure.attrs.get("xml:id") or ""
        label = figure.find("label").text
        if figure_type == "table":
            caption = figure.find("figdesc").text
            data = figure.table.text
        else:
            caption = figure.text
            data = ""
        figures_list.append(
            Figure(
                figure_label=label,
                figure_type=figure_type,
                figure_id=figure_id,
                figure_caption=caption,
                figure_data=data,
            )
        )
    return figures_list


def parse_formulas(article: BeautifulSoup) -> list[Formula]:
    """
    Parse list of formulas from a given BeautifulSoup of an article

    Parameters
    ==========
    article: BeautifulSoup, parsed article in BeautifulSoup format

    Returns
    =======
    formulas_list: list[Formula], list of formulas parsed from the article
    """
    formulas_list = []

    formulas = article.find_all("formula")
    for formula in formulas:
        formula_id = formula.attrs.get("xml:id", "")
        formula_text = formula.text
        formula_coordinates = formula.attrs.get("coords", [])

        if formula_coordinates:
            formula_coordinates = [float(x) for x in formula_coordinates.split(",")]

        formula_data = Formula(
            formula_id=formula_id,
            formula_text=formula_text,
            formula_coordinates=formula_coordinates,
        )
        formulas_list.append(formula_data)

    return formulas_list


def calculate_text_stats(article: Article, soup: BeautifulSoup) -> Article:
    """
    Function to calculate text statistics for a given article

    Parameters
    ==========
    article: Article, parsed article in JSON format

    Returns
    =======
    article: Article, parsed article with text statistics
    """
    full_text = article.full_text

    article.text_stats = TextStatistic(
        readability=compute_readability_stats(full_text),
        text_stats=compute_text_stats(full_text),
        journal_features=compute_journal_features(soup),
    )


def convert_article_soup_to_pydantic(soup: BeautifulSoup) -> Article:
    """
    Function to convert BeautifulSoup to JSON format similar to the output from https://github.com/allenai/science-parse/

    Parameters
    ==========
    soup: BeautifulSoup

    Output
    ======
    article_dict: ArticleDict, parsed dictionary of a given article
    """
    if soup is None:
        raise ValueError("Soup is None")

    title = soup.find("title", attrs={"type": "main"})
    title = title.text.strip() if title is not None else ""
    doi = soup.find("idno", attrs={"type": "DOI"})
    doi = doi.text if doi is not None else ""

    article = Article(
        title=title,
        authors=parse_authors(soup),
        pub_date=parse_date(soup),
        abstract=parse_abstract(soup),
        sections=parse_sections(soup),
        references=parse_references(soup),
        figures=parse_figure_caption(soup),
        formulas=parse_formulas(soup),
        doi=doi,
    )

    article.text_stats = calculate_text_stats(article, soup)
    return article
