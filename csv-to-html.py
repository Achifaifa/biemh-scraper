#! /usr/bin/env python

import csv

baseurl="<a href='https://www.openstreetmap.org/search?query="

with open("data/datafinal.html","w+") as dataout, open("data/datafinal_csv.csv", "r") as csvin:
  d=csv.reader(csvin, delimiter='\t')
  dataout.write("""
    <head>
    <meta charset="UTF-8">
    </head> 
    <style media="screen" type="text/css">
      table, th, td {
        border-collapse: collapse;
        border: 1px solid black;
      }
    </style>
    <center>
    <img src='./novakide.jpg'><br/>
    <a href='https://achifaifa.cartodb.com/viz/8f7ac4dc-2399-11e6-81d2-0e674067d321/public_map'>Mapa general</a><br/><br/>
    </center>
    <table border='1'>\n
    """)
  
  for n,row in enumerate(d):
    dataout.write("  <tr>\n")
    location="location" if row[2]=="latitude" else baseurl+" ".join(row[2:4])+"#map=5/45.136/3.867'>%s</a>"%row[1] if row[2] else ""
    url="Site" if row[7]=="web" else row[7].lstrip("http://").lstrip("www.") if row[7] else ""
    url="Site" if url=="Site" else "<a href='http://%s'>%s</a>"%(url,url) if url else ""
    outstruct=[row[0]]+[row[5].replace(" ",""),row[6],url, location]
    for j in outstruct:
      if not n: dataout.write("    <th>%s</th>\n"%j)
      else:     dataout.write("    <td>%s</td>\n"%j)
    dataout.write("  </tr>\n")
  dataout.write("</table>\n")