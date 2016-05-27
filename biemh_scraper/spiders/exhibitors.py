# -*- coding: utf-8 -*-

import scrapy
import geocoder
from unicodedata import normalize

escapesymbols=["\t","\n"]
def escape(txt):
  """ 
  Deletes tabs and line breaks from a given text.
  Also normalizes the text to unicode to avoid excel/calc encoding issues
  """

  for i in escapesymbols: txt=txt.replace(i,"")
  return normalize("NFKD", unicode(txt))

class exhibitors(scrapy.Spider):

  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  # Use URL with 100 exhibitors per page (less chances of 'find next page' fails)
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/?pagenum=1&num_elem=100&nombre&pais&pabellon&sector&subsector&producto&destino=expositores&idioma=US&tab=expositores&seccli&contextual&buscar=2&letra']

  def parseexhibitor(self, response):

    name=escape(response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0])
    stand=response.xpath("//*/h4/text()").extract()[0].lstrip("Stand: ")

    # Assumes description will always be in the second fila div. 
    # TO-DO: Make sure descriptions are processed
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
    titles=["delegado", "jefe", "director", "dpto", "servicio"]
    for item in contactinfo:
      # Sometimes telephones and faxes are divided by /
      # Convert that to list to prevent excel/calc from interpreting that as a division
      item=escape(item)
      if "tel" in item.lower(): 
        telephone=item.strip().split(": ")[-1]
        if "/" in telephone: telephone=telephone.split("/")
      elif "fax" in item.lower(): 
        fax=item.strip().split(": ")[-1]
        if "/" in fax: fax=fax.split("/")
      # First line of address are all caps
      elif item.isupper(): addr.append(item)
      # Store other contact info that may be useful 
      elif not "web" in item.lower() and any(i in item.lower() for i in titles): contactmisc.append(item)
      # Second lines of addresses always have ',' and '('
      elif not ":" in item and all(i in item for i in [",","("]): addr.append(item)
      # PO boxes fail a lot with previous filters
      elif "PO" in item: addr.append(item)

    addrreplaces={"PG": "poligono", "AVDA": "avenida", "IND.": "industrial", "AV":"avenida", "PL": "plaza", "CL": "calle",
                  "CR": "carretera", "POL.": "poligono", "C/": "calle", "PQ": "parque", "EMP.": "empresarial"}
    
    # Process address
    address=" ".join(addr).lower()
    #for tag,item in addrreplaces.iteritems():address=address.replace(tag,item)

    # Geocoding
    # Uses OSM data. Some addresses may need extra processing
    # Only processes street name and number (First line)
    latitude=longitude=""
    a=geocoder.google(address)
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
