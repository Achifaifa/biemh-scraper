# -*- coding: utf-8 -*-

import scrapy
import geocoder
from unicodedata import normalize

escapesymbols=["\t","\n"]
def escape(txt):

  for i in escapesymbols: txt=txt.replace(i,"")
  return normalize("NFKD", unicode(txt))

class exhibitors(scrapy.Spider):

  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/?pagenum=1&num_elem=100&nombre&pais&pabellon&sector&subsector&producto&destino=expositores&idioma=US&tab=expositores&seccli&contextual&buscar=2&letra']

  def parseexhibitor(self, response):

    name=escape(response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0])
    stand=response.xpath("//*/h4/text()").extract()[0].lstrip("Stand: ")

    # Assumes description will always be in the second fila div. 
    # TO-DO (maybe): Get videos, pic urls, etc from description
    description=escape("".join(response.xpath("//*/div[@class='fila'][2]/div/text()").extract()).strip())

    # Since the data is not ordered in the site, this takes all the data
    # and processes it later
    data=response.xpath("//div[@class='fila']/ul/li/text()").extract()
    sector=[]
    countries=[]
    categories=[]
    country_list=["Russian Federation", "United States", "United Kingdom"]
    for item in data:
      item=escape(item)
      if item.isupper(): categories.append(item)
      elif item in country_list: countries.append(item)
      elif any(i in item for i in [",",".",":","-"," ","/"]): sector.append(item)
      else: countries.append(item)

    # Assumes everything in p is contact info. May screw things up
    contactinfo=response.xpath("//p[@class='fila']/text()").extract()
    addr=[]
    telephone=""
    fax=""
    contactmisc=[]
    for item in contactinfo:
      item=escape(item)
      if "tel" in item.lower(): 
        telephone=item.strip().split(": ")[-1]
        if "/" in telephone: telephone=telephone.split("/")
      elif "fax" in item.lower(): 
        fax=item.strip().split(": ")[-1]
        if "/" in fax: fax=fax.split("/")
      elif item.isupper(): addr.append(item)
      elif not ":" in item and all(i in item for i in [",","("]): addr.append(item)
      elif ":" in item and not "web" in item.lower(): contactmisc. append(item)
    address=" ".join(addr)

    # Geocoding
    latitude=longitude=""
    a=geocoder.osm(address)
    if a.latlng:
      latitude, longitude=a.latlng

    # Exhibitor page may or may not have a website
    try:                web=response.xpath("//p[@class='fila']/a/@href").extract()[0]
    except IndexError:  web=""

    yield { "name": name, 
            "contact": {
              "address": address, 
              "telephone": telephone, 
              "fax": fax,
              "web": web,
              "stand": stand,
              "coords": {
                "latitude": latitude,
                "longitude": longitude
              },
              "misc": contactmisc
            },
            "description": description,
            "sector": sector,
            "countries": countries,
            "categories": categories,
          }

  def parse(self, response):

    # Promoted and unpromoted exhibitors have different classes but share
    # the same html structures, so the two things are joined and processed
    standsa=response.xpath("//*[@class='resaltadoS']/td[@class='titulo']/a/@href").extract()
    standsb=response.xpath("//*[@class='resaltadoN']/td[@class='titulo']/a/@href").extract()
    for stand in standsa+standsb:
      standurl=response.urljoin(stand)
      try:
        yield scrapy.Request(standurl,callback=self.parseexhibitor)
      except Exception as e: 
        print "Error parsing"
        print e
        exit()

    nexturl=response.xpath("//*[@class='resultados']/div[@class='tablenav']/div/a[@class='next page-numbers']/@href").extract()
    npurl=response.urljoin(nexturl[0])
    try:
      yield scrapy.Request(npurl, callback=self.parse)
    except Exception as e:
      print "Error parsing"
      print e
      exit()
