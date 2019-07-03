import os
from glob import glob
import subprocess
import json
import requests
from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm, tqdm_notebook


GROBID_URL = 'http://localhost:8070'


def list_pdf_paths(pdf_folder):
    """
    list of pdf paths in pdf folder
    """
    return glob(os.path.join(pdf_folder, '*', '*', '*.pdf'))


def parse_pdf(pdf_path,
              fulltext=True,
              soup=False,
              grobid_url=GROBID_URL):
    """
    Function to parse PDF to XML or BeautifulSoup using GROBID tool
    
    You can see http://grobid.readthedocs.io/en/latest/Install-Grobid/ on how to run GROBID locally
    After loading GROBID zip file, you can run GROBID by using the following
    >> ./gradlew run
    
    Parameters
    ==========
    pdf_path: str, path to publication or article
    fulltext: bool, option for parsing, if True, parse full text of the article
        if False, parse only header
    grobid_url: str, url to GROBID parser, default at 'http://localhost:8070'
    soup: bool, if True, return BeautifulSoup of the article
    
    Output
    ======
    parsed_article: if soup is False, return parsed XML in text format, 
        else return BeautifulSoup of the XML
    Example
    =======
    >> parsed_article = parse_pdf(pdf_path, fulltext=True, soup=True)
    """
    if os.path.exists(pdf_path):
        if fulltext:
            url = '%s/api/processFulltextDocument' % grobid_url
        else:
            url = '%s/api/processHeaderDocument' % grobid_url
        parsed_article = requests.post(url, files={'input': open(pdf_path, 'rb')}).text

        if soup:
            parsed_article = BeautifulSoup(parsed_article, 'lxml')

        return parsed_article
    else:
        return None


def parse_abstract(article):
    """
    Parse abstract from a given BeautifulSoup of an article 
    """
    div = article.find('abstract')
    abstract = ''
    for p in list(div.children):
        if not isinstance(p, NavigableString) and len(list(p)) > 0:
            abstract += ' '.join([elem.text for elem in p if not isinstance(elem, NavigableString)])    
    return abstract


def parse_sections(article):
    """
    Parse list of sections from a given BeautifulSoup of an article 
    """
    article_text = article.find('text')
    divs = article_text.find_all('div', attrs={'xmlns': 'http://www.tei-c.org/ns/1.0'})
    sections = []
    for div in divs:
        div_list = list(div.children)
        if len(div_list) == 0:
            pass
        elif len(div_list) == 1:
            if isinstance(div_list[0], NavigableString):
                heading = str(div_list[0])
                text = ''
            else:
                heading = ''
                text = div_list[0].text
        else:
            text = []
            heading = div_list[0]
            if isinstance(heading, NavigableString):
                heading = str(heading)
                p_all = list(div.children)[1:]
            else:
                heading = ''
                p_all = list(div.children)
            for p in p_all:
                if p is not None:
                    try:
                        text.append(p.text)
                    except:
                        pass
            text = ' '.join(text)
        if heading is not '' or text is not '':
            sections.append({
                'heading': heading, 
                'text': text
            })
    return sections


def parse_references(article):
    """
    Parse list of references from a given BeautifulSoup of an article
    """
    reference_list = []
    references = article.find('text').find('div', attrs={'type': 'references'})
    references = references.find_all('biblstruct') if references is not None else []
    reference_list = []
    for reference in references:
        title = reference.find('title', attrs={'level': 'a'})
        if title is None:
            title = reference.find('title', attrs={'level': 'm'})
        title = title.text if title is not None else ''
        journal = reference.find('title', attrs={'level': 'j'})
        journal = journal.text if journal is not None else ''
        if journal is '':
            journal = reference.find('publisher')
            journal = journal.text if journal is not None else ''
        year = reference.find('date')
        year = year.attrs.get('when') if year is not None else ''
        authors = []
        for author in reference.find_all('author'):
            firstname = author.find('forename', {'type': 'first'})
            firstname = firstname.text.strip() if firstname is not None else ''
            middlename = author.find('forename', {'type': 'middle'})
            middlename = middlename.text.strip() if middlename is not None else ''
            lastname = author.find('surname')
            lastname = lastname.text.strip() if lastname is not None else ''
            if middlename is not '':
                authors.append(firstname + ' ' + middlename + ' ' + lastname)
            else:
                authors.append(firstname + ' ' + lastname)
        authors = '; '.join(authors)
        reference_list.append({
            'title': title,
            'journal': journal,
            'year': year,
            'authors': authors
        })
    return reference_list


def parse_figure_caption(article):
    """
    Parse list of figures/tables from a given BeautifulSoup of an article
    """
    figures_list = []
    figures = article.find_all('figure')
    for figure in figures:
        figure_type = figure.attrs.get('type') or ''
        figure_id = figure.attrs['xml:id'] or ''
        label = figure.find('label').text
        if figure_type == 'table':
            caption = figure.find('figdesc').text
            data = figure.table.text
        else:
            caption = figure.text
            data = ''
        figures_list.append({
            'figure_label': label,
            'figure_type': figure_type,
            'figure_id': figure_id,
            'figure_caption': caption,
            'figure_data': data
        })
    return figures_list


def convert_article_soup_to_dict(article):
    """
    Function to convert BeautifulSoup to JSON format 
    similar to the output from https://github.com/allenai/science-parse/

    Parameters
    ==========
    article: BeautifulSoup

    Output
    ======
    article_json: dict, parsed dictionary of a given article in the following format
        {
            'title': ..., 
            'abstract': ..., 
            'sections': [
                {'heading': ..., 'text': ...}, 
                {'heading': ..., 'text': ...},
                ...
            ],
            'references': [
                {'title': ..., 'journal': ..., 'year': ..., 'authors': ...}, 
                {'title': ..., 'journal': ..., 'year': ..., 'authors': ...},
                ...
            ], 
            'figures': [
                {'figure_label': ..., 'figure_type': ..., 'figure_id': ..., 'figure_caption': ..., 'figure_date': ...},
                ...
            ]
        }
    """
    article_dict = {}
    title = article.find('title', attrs={'type': 'main'})
    title = title.text.strip() if title is not None else ''
    article_dict['title'] = title
    article_dict['abstract'] = parse_abstract(article)
    article_dict['sections'] = parse_sections(article)
    article_dict['references'] = parse_references(article)
    article_dict['figures'] = parse_figure_caption(article)

    doi = article.find('idno', attrs={'type': 'DOI'})
    doi = doi.text if doi is not None else ''
    article_dict['doi'] = doi

    return article_dict


def parse_pdf_to_dict(pdf_path):
    """
    Parse the given 

    Parameters
    ==========
    pdf_path: str, path to publication or article

    Ouput
    =====
    article_dict: dict, dictionary of an article
    """
    parsed_article = parse_pdf(pdf_path, fulltext=True, soup=True)
    article_dict = convert_article_soup_to_dict(parsed_article)
    return article_dict


def parse_figures(pdf_folder,
                  jar_path='scipdf/pdf/pdffigures2/pdffigures2-assembly-0.0.12-SNAPSHOT.jar',
                  resolution=300, 
                  save_data='figures/data/', 
                  save_figures='figures/figures/'):
    """
    Parse figures from the given scientific PDF using pdffigures2

    Parameters
    ==========
    pdf_folder: glob path to folder that contains PDF
    resolution: resolution of the output figures
    save_data: path to folder that we want to save data related to figures
    save_figures: path to folder that we want to save figures
    """
    if os.path.isdir(save_data) and os.path.isdir(save_figures):
        args = [
            'java',
            '-jar', jar_path,
            pdf_folder,
            '-i', str(resolution),
            '-d', save_data,
            '-m', save_figures
        ]
        _ = subprocess.run(
            args, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )
        print('Done parsing figures from PDFs!')
    else:
        print('save_data and save_figures have to be placeholder folders')