#!/usr/bin/env python
from __future__ import print_function
import csv

temp = open("template.html").read()
temp_people = open("people.html").read()
temp_alumni = open("alumni.html").read()
temp_papers = open("papers.html").read()
temp_jobs = open("jobs.html").read()
temp_tools = open("tools.html").read()
temp_news = open("news.html").read()
temp_research = open("research.html").read()

authors = {}

people = ""
lalumni = "<ul>"
ix = 0;
for i in csv.reader(open("people.csv"), delimiter=";"):
    authors[i[6]] = i
    if i[1] != "Alumni":
        people += temp_people.format(name=i[0], title=i[1], description=i[2], imgsrc="imgs/" + i[3], imgalt=i[4],
                                     email=i[5])
        ix += 1
    else:
        lalumni += "<li>" + i[0]
people += temp_alumni.format(alumni=lalumni + "</ul>")


def makeup_author(s):
    sp = s.split(", ")
    nl = []
    for i in sp:
        if i in authors:
            nl.append("<span class='author' onmouseover='author_image=\"imgs/" + authors[i][
                3] + "\";'><b><u>" + i + "</u></b></span>")
        else:
            nl.append(i)
    return ", ".join(nl)



paper_free_links_title = {}
paper_free_links_id = {}
for i in csv.reader(open("paper_free_links.csv"), delimiter="|"):
    if len(i)>2:
      if i[0]!="":
        paper_free_links_title[i[0]]=i[2]
      if i[1]!="":
        paper_free_links_id[i[1]]=i[2]
        
papers = "";
pix = 0;
py = ""
papercount = 0
for i in csv.reader(open("papers.csv"), delimiter="|"):
    papercount += 1
for i in csv.reader(open("papers.csv"), delimiter="|"):
    if py != i[3]:
        if py != "":
            papers += "      </table><br>"
        papers += "      <b>" + i[3] + "</b><br>\n      <table class='papertable'>\n"
    img1, img2, img3 = "", "", ""
    if i[5] != "":
        img1 = "<a href='" + i[5] + "'><img class='paperimg' src='" + i[6] + "'/></a>"
    if i[7] != "":
        img2 = "<a href='" + i[7] + "'><img class='paperimg' src='" + i[8] + "'/></a>"
    if i[0] in paper_free_links_title:
        img3 = "<a href='" + paper_free_links_title[i[0]] + "'><img class='paperimg' src='imgs/link.png'/></a>"
    papers += temp_papers.format(title=i[0], authors=makeup_author(i[1]), journal=i[2], year=i[3], ref=i[4], img1=img1,
                                 img2=img2, img3=img3, index=str(papercount))
    papercount -= 1
    pix += 1
    py = i[3]
papers += "      </table>"

research = "      <div class='research-div'>\n";
for i in csv.reader(open("research.csv"), delimiter=";"):
    research += temp_research.format(title=i[0], description=i[1], img="imgs/" + i[2])
research += "      </div>"

tools = "      <div class='w3-row'>";
for i in csv.reader(open("tools.csv"), delimiter=";"):
    tools += temp_tools.format(card='<div class="github-card" data-github="' + i[
        1] + '" data-width="100%" data-height="200" data-theme="default"></div>')
tools += "</div>"
tools += '<script src="//cdn.jsdelivr.net/github-cards/latest/widget.js"></script>\n'

news_archive="<ul>"
news = "      <div class='w3-row'>";
pix = 0
for i in csv.reader(open("news.csv"), delimiter=";"):
    link, img = "", ""
    if (i[1] != ""):
        link = "<b>More: </b><a href='" + i[1] + "'>" + i[1] + "</a>"
    if (i[2] != ""):
        img = "<img src='" + i[2] + "' class='w3-center' style='width:90%;'>"
    if pix < 4:
        news += temp_news.format(title=i[0], link=link, img=img, subtitle=i[3], footer=i[4], description=i[5])
    news_archive += "<li><b>{title}</b> {subtitle} <br> {description}<br>{img} {link}<br> {footer} <br><br>".format(
      title=i[0], link=link, img=img, subtitle=i[3], footer=i[4], description=i[5])
    pix += 1
news += "</div>"

print(temp.replace("{{people}}", people).replace("{{papers}}", papers).replace("{{positions}}", temp_jobs).replace(
    "{{research}}", research).replace("{{news}}", news).replace("{{tools}}", tools).replace("{{news_archive}}",news_archive))
