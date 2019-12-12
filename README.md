# Web-page

Abyzov lab [web page](https://abyzovlab.github.io/Web-page/)

## Update steps

(I) Update papers using TJ's script:
```
$ ./papers_csv.py -c 40799671 > papers.csv
```

(II) Manually update: news.csv people.csv research.csv tools.csv

(III) Generate page
```
$ python generate.py > index.html
```

(IV) Test
```
$ python -m SimpleHTTPServer
```
Then open in broser [web page](localhost:8000)

(V) Commit and push to github
```
$ git add *csv *html
$ git commit -m “Update”
$ git push
```
