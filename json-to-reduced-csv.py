# -*- coding: utf-8 -*-
#! /usr/bin/env python

import json

with open("datafinal.json","r") as data:
  dat=json.load(data)

cats={"electronics": "Electric / Electronics", "aeronautics": "Aeronautics / Aerospace", "automotive": "Automotive", "shipbuilding":"Naval / Shipbuilding"}

with open("datafinal_csv_red.csv", "w+") as dataout:
  dataout.write("name\tlatitude\tlongitude\tcategory\n")

  for i in dat:
    # Write simplified category
    lookup="".join(i["sector"])
    category="others"
    for tag,val in cats.iteritems():
      if tag in lookup.lower(): 
        category=val
        break

    # Write data to file
    dataout.write((u"%s\t%s\t%s\t%s\n"%(i["name"],
                                    i["contact"]["coords"]["latitude"],
                                    i["contact"]["coords"]["longitude"],
                                    category
                                    )).encode('utf-8'))
