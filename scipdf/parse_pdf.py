import os
import os.path as op
import subprocess
import urllib

import requests
from bs4 import BeautifulSoup

from scipdf.models import Article
from scipdf.pdf.parser_functions import validate_url, convert_article_soup_to_pydantic


class SciPDFParser:
    def __init__(self, grobid_url: str = "http://localhost:8070"):
        self.grobid_url = grobid_url
        self.pdf_figures_jar_path = op.join(op.dirname(__file__),
                                            "pdf/pdffigures2/pdffigures2-assembly-0.0.12-SNAPSHOT.jar")

    def parse_pdf(self,
                  pdf_path: str,
                  fulltext: bool = True,
                  return_coordinates: bool = True,
                  ) -> Article:
        """
        Function to parse PDF to XML or BeautifulSoup using GROBID tool

        You can see http://grobid.readthedocs.io/en/latest/Install-Grobid/ on how to run GROBID locally
        After loading GROBID zip file, you can run GROBID by using the following
        >> ./gradlew run

        Parameters
        ==========
        pdf_path: str or bytes, path or URL to publication or article or bytes string of PDF
        fulltext: bool, option for parsing, if True, parse full text of the article
            if False, parse only header
        grobid_url: str, url to GROBID parser, default at 'http://localhost:8070'
            This could be changed to "https://cloud.science-miner.com/grobid/" for the cloud service
        soup: bool, if True, return BeautifulSoup of the article

        Output
        ======
        parsed_article: if soup is False, return parsed XML in text format,
            else return BeautifulSoup of the XML
        Example
        =======
        >> parsed_article = parse_pdf(pdf_path, fulltext=True, soup=True)
        """
        # GROBID URL
        if fulltext:
            url = "%s/api/processFulltextDocument" % self.grobid_url
        else:
            url = "%s/api/processHeaderDocument" % self.grobid_url

        files = []
        if return_coordinates:
            files += [
                ("teiCoordinates", (None, "persName")),
                ("teiCoordinates", (None, "figure")),
                ("teiCoordinates", (None, "ref")),
                ("teiCoordinates", (None, "formula")),
                ("teiCoordinates", (None, "biblStruct")),
            ]

        if isinstance(pdf_path, str):
            if op.splitext(pdf_path)[-1].lower() != ".pdf":
                raise ValueError("The input has to end with ``.pdf``")
            elif validate_url(pdf_path):
                page = urllib.request.urlopen(pdf_path).read()
                parsed_article = requests.post(url, files={"input": page}).text
            elif op.exists(pdf_path):
                parsed_article = requests.post(
                    url, files={"input": open(pdf_path, "rb")}
                ).text
            else:
                raise RuntimeError("The input URL is not valid")
        elif isinstance(pdf_path, bytes):
            # assume that incoming is byte string
            parsed_article = requests.post(url, files={"input": pdf_path}).text
        else:
            raise RuntimeError("Failed to parse PDF, Do you have GROBID running?")

        parsed_article = BeautifulSoup(parsed_article, "lxml")

        return convert_article_soup_to_pydantic(parsed_article)

    def parse_figures(
            self,
            pdf_folder: str,
            resolution: int = 300,
            output_folder: str = "figures",
    ):
        """
        Parse figures from the given scientific PDF using pdffigures2

        Parameters
        ==========
        pdf_folder: str, path to a folder that contains PDF files. A folder must contains only PDF files
        jar_path: str, default path to pdffigures2-assembly-0.0.12-SNAPSHOT.jar file
        resolution: int, resolution of the output figures
        output_folder: str, path to folder that we want to save parsed data (related to figures) and figures

        Output
        ======
        folder: making a folder of output_folder/data and output_folder/figures of parsed data and figures relatively
        """
        if not op.isdir(output_folder):
            os.makedirs(output_folder)

        # create ``data`` and ``figures`` subfolder within ``output_folder``
        data_path = op.join(output_folder, "data")
        figure_path = op.join(output_folder, "figures")
        if not op.exists(data_path):
            os.makedirs(data_path)
        if not op.exists(figure_path):
            os.makedirs(figure_path)

        if op.isdir(data_path) and op.isdir(figure_path):
            args = [
                "java",
                "-jar",
                self.pdf_figures_jar_path,
                pdf_folder,
                "-i",
                str(resolution),
                "-d",
                op.join(op.abspath(data_path), ""),
                "-m",
                op.join(op.abspath(figure_path), ""),  # end path with "/"
            ]
            _ = subprocess.run(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20
            )
            print("Done parsing figures from PDFs!")
        else:
            print(
                "You may have to check of ``data`` and ``figures`` in the the output folder path."
            )
