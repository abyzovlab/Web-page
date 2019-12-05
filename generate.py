#!/usr/bin/env python
from __future__ import print_function
import csv

temp=open("template.html").read()
temp_people=open("people.html").read()
temp_papers=open("papers.html").read()
temp_jobs=open("jobs.html").read()
temp_tools=open("tools.html").read()
temp_news=open("news.html").read()
temp_research=open("research.html").read()

authors={}

s="      <div class='w3-row'>";
ix=0;
for i in csv.reader(open("people.csv"),delimiter=";"):
  authors[i[6]]=i
  if i[1]!="Alumni":
    t=temp_people.replace("{{name}}",i[0])
    t=t.replace("{{title}}",i[1])
    t=t.replace("{{description}}",i[2])
    t=t.replace("{{imgsrc}}","imgs/"+i[3])
    t=t.replace("{{imgalt}}",i[4])
    t=t.replace("{{email}}",i[5])
    s+=t
  ix+=1
s+="</div>"
temp=temp.replace("{{people}}",s)

def makeup_author(s):
  sp=s.split(", ")
  nl=[]
  for i in sp:
    if i in authors:
      nl.append("<span class='author' onmouseover='author_image=\"imgs/"+authors[i][3]+"\";'><b><u>"+i+"</u></b></span>")
    else:
      nl.append(i)
  return ", ".join(nl)


s="";
pix=0;
py=""
papercount=0
for i in csv.reader(open("papers.csv"),delimiter="|"):
  papercount+=1
for i in csv.reader(open("papers.csv"),delimiter="|"):
  if py!=i[3]:
    if py!="":
      s+="      </table><br>"
    s+="      <b>"+i[3]+"</b><br>\n      <table class='papertable'>\n"
  t=temp_papers.replace("{{title}}",i[0])
  t=t.replace("{{authors}}",makeup_author(i[1]))
  t=t.replace("{{journal}}",i[2])
  t=t.replace("{{year}}",i[3])
  t=t.replace("{{ref}}",i[4])
  if i[5]!="":
    t=t.replace("{{img1}}","<a href='"+i[5]+"'><img class='paperimg' src='"+i[6]+"'/></a>")
  else:
    t=t.replace("{{img1}}","")
  if i[7]!="":
    t=t.replace("{{img2}}","<a href='"+i[7]+"'><img class='paperimg' src='"+i[8]+"'/></a>")
  else:
    t=t.replace("{{img2}}","")
  t=t.replace("{{index}}",str(papercount))
  papercount-=1
  s+=t
  pix+=1
  py=i[3]
s+="      </table>"

temp=temp.replace("{{papers}}",s)

s="      <div class='w3-row'>";
pix=0;
for i in csv.reader(open("research.csv"),delimiter=";"):
  t=temp_research.replace("{{title}}",i[0])
  t=t.replace("{{description}}",i[1])
  t=t.replace("{{img}}","imgs/"+i[2])
  s+=t
  pix+=1
s+="      </div>"

temp=temp.replace("{{research}}",s)

temp=temp.replace("{{positions}}",temp_jobs)

s="      <div class='w3-row'>";
pix=0;
py=""
for i in csv.reader(open("tools.csv"),delimiter=";"):
  t=temp_tools.replace("{{title}}",i[0])
  if(i[3]!=""):
    t=t.replace("{{ref}}","<br>More: <a href='"+i[3]+"'>ref</a>")
  else:
    t=t.replace("{{ref}}","")
  if(i[4]!=""):
    t=t.replace("{{img}}","<img src='"+i[2]+"' class='w3-center' style='width:90%;'>")
  else:
    t=t.replace("{{img}}","")
  if(i[1]!=""):
    t=t.replace("{{card}}",'<div class="github-card" data-github="'+i[1]+'" data-width="100%" data-height="153" data-theme="default"></div>')
  else:
    t=t.replace("{{card}}","")

  t=t.replace("{{description}}",i[2])
  s+=t
  pix+=1
s+="</div>"
s+='<script src="//cdn.jsdelivr.net/github-cards/latest/widget.js"></script>\n'


temp=temp.replace("{{tools}}",s)

s="      <div class='w3-row'>";
pix=0;
py=""
for i in csv.reader(open("news.csv"),delimiter=";"):
  if pix<4:
    t=temp_news.replace("{{title}}",i[0])
    if(i[1]!=""):
      t=t.replace("{{link}}","<b>More: </b><a href='"+i[1]+"'>"+i[1]+"</a>")
    else:
      t=t.replace("{{link}}","")
    if(i[2]!=""):
      t=t.replace("{{img}}","<img src='"+i[2]+"' class='w3-center' style='width:90%;'>")
    else:
      t=t.replace("{{img}}","")

    t=t.replace("{{subtitle}}",i[3])
    t=t.replace("{{footer}}",i[4])
    t=t.replace("{{description}}",i[5])
    s+=t
  pix+=1
s+="</div>"
temp=temp.replace("{{news}}",s)

print(temp)
