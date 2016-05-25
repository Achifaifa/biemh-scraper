# -*- coding: utf-8 -*-
#! /usr/bin/env python

import json

with open("datafinal.json","r") as data:
  dat=json.load(data)

with open("datafinal_csv.csv", "w+") as dataout:
  dataout.write("name\taddr\tfax\tstand\ttel\tweb\tcontries\tdesc\tsector\n")
  for i in dat:
    dataout.write((u"%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(i["name"],
                                                          i["contact"]["address"],
                                                          i["contact"]["fax"],
                                                          i["contact"]["stand"],
                                                          i["contact"]["telephone"],
                                                          i["contact"]["web"],
                                                          ", ".join(i["countries"]),
                                                          i["description"],
                                                          ", ".join(i["sector"])
                                                          )).encode('utf-8'))
