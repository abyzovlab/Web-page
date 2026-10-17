#!/usr/bin/env python3

import argparse
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from time import sleep, localtime, strftime
import re
import sys
from collections import defaultdict

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

class MyNCBI:
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.8059.84 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument(f'user-agent={user_agent}')
    path = 'chromedriver'

    def __init__(self, authid, members_fname=None):
        self.papers = defaultdict(list)
        self.set_members(members_fname)

        service = Service(executable_path='./chromedriver')
        self.myncbi = webdriver.Chrome(service=service, options=self.options)

        self.myncbi.implicitly_wait(5)
        self.pubmed = webdriver.Chrome(service=service, options=self.options)
        self.pubmed.implicitly_wait(5)

        self.scrap_myncbi(authid)

        self.myncbi.quit()
        self.pubmed.quit()

    def scrap_myncbi(self, authid):
        self.myncbi.get("https://www.ncbi.nlm.nih.gov/myncbi/{authid}.1/bibliography/public/?sortby=pubDate&sdirection=ascending".format(authid=authid))
        index = 0
        while True:
            for docsum in self.myncbi.find_elements(By.XPATH, '//div[@class="ncbi-docsum"]'):
                index += 1

                try:
                    title = docsum.find_element(By.XPATH, './span[@class="title"]').text
                except NoSuchElementException:
                    title = docsum.find_element(By.XPATH, './a').text
                
                sys.stderr.write("Scraping {index}. {title}...\n".format(index=index, title=title[:40]))
                
                author = docsum.find_element(By.XPATH, './span[@class="authors"]').text.rstrip(".")
                author = self.highlight_members(author)
                
                try:
                    pmid = docsum.find_element(By.XPATH, './span[@class="pmid"]').text.split()[-1]
#                    sys.stdout.write("PMID is {pmid}\n".format(pmid=pmid))
                    year, paper = self.paper_from_pmid(pmid)
                    paper = paper.format(index=index, title=title, author=author)
                except NoSuchElementException:
                    try:
                        year = docsum.find_element(By.XPATH, './span[@class="displaydate"]').text[:4]
                        page = docsum.find_element(By.XPATH, './span[@class="page"]').text.rstrip(".")
                        try:
                            journal = docsum.find_element(By.XPATH, './span[@class="journalname"]').text.rstrip(".")
                            volume = docsum.find_element(By.XPATH, './span[@class="volume"]').text
                            issue = docsum.find_element(By.XPATH, './span[@class="issue"]').text
                        
                            paper = '''{title}|{author}|{journal}|{year}|{volume} {issue}; {page}||||\n'''.format(index=index, title=title, 
                                        author=author, year=year, journal=journal, issue=issue, volume=volume, page=page)  
                        except NoSuchElementException:    
                            editor = docsum.find_element(By.XPATH, './span[@class="editors"]').text    
                            publisher = docsum.find_element(By.XPATH, './span[@class="book-publisher"]').text
                            try:
                                ch_title = docsum.find_element(By.XPATH,'./span[@class="chaptertitle"]').text
                                ch_num = docsum.find_element(By.XPATH,'./span[@class="chapter-details"]').text
                                paper = '''{title}|{author}|{chapter}|{year}|{issue}; {page}||||\n'''.format(index=index, chapter=ch_title+", "+publisher, title=title,
                                          author=author, issue=ch_num, year=year, page=page) 
                            except NoSuchElementException:
                                paper = '''{title}|{author}|{chapter}|{year}|{page}||||\n'''.format(index=index, chapter=publisher, title=title,
                                          author=author, year=year, page=page)
                    except NoSuchElementException:
                        tmp = docsum.find_element(By.XPATH,'./span[@class="confloc"]').text
                        publisher  = tmp.split("; ")[1]
                        year = tmp.split("; c")[-1].rstrip(". ")
                        paper = '''{title}|{author}|{publisher}|{year}|||||\n'''.format(index=index, publisher=publisher, title=title,
                                          author=author, year=year)
                        
                self.papers[year].append(paper)

            try:
                self.myncbi.find_element(By.XPATH, '//a[@class="nextPage enabled"]').click()
            except NoSuchElementException:
                break

    def set_members(self, fname):
        if fname is None:
            self.members = None
        else:
            with open(fname) as f:
                self.members = [line.strip() for line in f]

    def highlight_members(self, author):
        if self.members is not None:
            for member in self.members:
                author = author.replace(member, "==^"+member+"$==")
        return author

    # def paper_from_pmid(self, pmid): # Old function written by TJ
    #     self.pubmed.get("https://pubmed.ncbi.nlm.nih.gov/{pmid}".format(pmid=pmid))

    #     journal = self.pubmed.find_element(By.XPATH, '//button[@id="full-view-journal-trigger"]').text

    #     cite_info = self.pubmed.find_element(By.XPATH, '//span[@class="cit"]').text
    #     year = re.search(r"[12]\d\d\d", cite_info.split(sep=';')[0])[0] 
    #     try:
    #         issue = cite_info.split(sep=';')[1].strip().rstrip(".")
    #     except IndexError:
    #         issue = "[Epub ahead of print]"
    #     paper = '{{title}}|{{author}}|{journal}|{year}|{issue}|'.format(journal=journal, year=year, issue=issue)
        
    #     try:
    #         link_tag = self.pubmed.find_elements(By.XPATH, '//a[contains(@class,"link-item") and contains(@class,"dialog-focus")]')
    #         paper += '{href}|{src}|'.format(href=link_tag[0].get_attribute('href'),
    #           src=link_tag[0].find_element(By.TAG_NAME, 'img').get_attribute('src'))
    #     except NoSuchElementException:
    #         paper += '||'
    #     paper += 'https://pubmed.ncbi.nlm.nih.gov/{pmid}|imgs/pubmed.png\n'.format(pmid=pmid)

    #     return (year, paper)


    def paper_from_pmid(self, pmid): # New function generated with the help of ChatGPT

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        params = urllib.parse.urlencode({
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
        })

        url = f"{base_url}?{params}"

        with urllib.request.urlopen(url, timeout=20) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        article = root.find(".//PubmedArticle")

        if article is None:
            raise ValueError(f"No PubMed record found for PMID {pmid}")

        journal = article.findtext(".//Article/Journal/Title",default="")

        # If the full journal title is unavailable, try abbreviation.
        if not journal:
            journal = article.findtext(
                ".//Article/Journal/ISOAbbreviation",
                default=""
            )

        year = article.findtext(".//Article/Journal/JournalIssue/PubDate/Year",default="")

        if not year:
            medline_date = article.findtext(".//Article/Journal/JournalIssue/PubDate/MedlineDate",default="")

            match = re.search(r"[12]\d{3}", medline_date)

            if match:
                year = match.group(0)

        if not year:
            year = article.findtext(".//DateCompleted/Year",default="")

        if not year:
            year = "Unknown"

        volume = article.findtext(".//Article/Journal/JournalIssue/Volume",default="")

        issue = article.findtext(".//Article/Journal/JournalIssue/Issue",default="")

        pages = article.findtext(".//Article/Pagination/MedlinePgn",default="")

        cite_parts = []

        if volume:
            cite_parts.append(volume)

        if issue:
            if cite_parts:
                cite_parts[-1] += f"({issue})"
            else:
                cite_parts.append(f"({issue})")

        cite_info = ""

        if cite_parts:
            cite_info = "".join(cite_parts)
            
        if pages:
            if cite_info:
                cite_info += f":{pages}"
            else:
                cite_info = pages

        if not cite_info:
            cite_info = "[Epub ahead of print]"
            
        doi = ""

        for article_id in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = article_id.text or ""
                break

        paper = ("{title}|{author}|"f"{journal}|{year}|{cite_info}|")

        if doi:
            paper += f"https://doi.org/{doi}|imgs/doi.png|"
        else:
            paper += "||"

        paper += f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/|imgs/pubmed.png\n"

        return year, paper

    
    @property
    def csv(self):
        total_n = 0
        csv = ""
        for year, year_papers in sorted(self.papers.items(), reverse=True):
            year_papers.reverse()
            year_n = len(year_papers)
            total_n += year_n
            csv +="".join(year_papers);
        return csv

    
def main():
    parser = argparse.ArgumentParser(
        description='html builder for a publication list')

    parser.add_argument('-m', '--members', metavar='lab_member_list.txt', help='Lab member list to highlight in authors')
    parser.add_argument('-a', '--authid', metavar='firstname.lastname', required=True, help='My NCBI author name. ex) alexej.abyzov')

    args = parser.parse_args()
    
    m = MyNCBI(args.authid, args.members)
    print(m.csv,end='')

if __name__ == "__main__":
    main()
    
