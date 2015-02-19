#!/usr/bin/python3

from xml.dom.minidom import parseString
import http.client

def printElement(el, indent=0):
   for child in el.childNodes:
      pass
endpoint = "192.168.1.115:8200"
envelope= """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Body>
<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
<ObjectID>%s</ObjectID>
<BrowseFlag>BrowseDirectChildren</BrowseFlag>
<Filter>*</Filter>
<StartingIndex>0</StartingIndex>
<RequestCount>10</RequestCount>
</u:Browse>
</s:Body>
</s:Envelope>
"""
def getNodeContent(node, content):
   return node.getElementsByTagName(content)[0].childNodes[0].nodeValue
def getTitle(node):
   return getNodeContent(node,'dc:title')
def getUrl(node):
   return getNodeContent(node,'res')

class DLNAClient:
   def __init__(self):
      self.c = http.client.HTTPConnection(endpoint)

   def GetContainers(self, id):
      self.c.request("POST", "", envelope % id, headers = {"SOAPACTION": "urn:schemas-upnp-org:service:ContentDirectory:1#Browse"})
      resp = self.c.getresponse()
      data = resp.read().decode('utf-8')
      dom = parseString(data)
      data_dom = self.getDataElement(dom)
      containers = data_dom.documentElement.getElementsByTagName('container')
      items = data_dom.documentElement.getElementsByTagName('item')
      c = self.convertContainer(containers)
      i = self.convertItems(items)
      return (c, i)

   def getDataElement(self, dom):
      text = dom.documentElement.childNodes[0].childNodes[0].childNodes[0].childNodes[0].nodeValue
      data_dom = parseString(text)
      return data_dom
   def convertContainer(self, container):
      result = []
      for c in container:
         title = getTitle(c)
         id = c.getAttribute('id')
         child = c.getAttribute('childCount')
         result.append({'title':title, 'id':id, 'childs':child})
      return result
   def convertItems(self, items):
      result = []
      for i in items:
         id = i.getAttribute('id')
         title = getTitle(i)
         link = getUrl(i)
         dur = i.getElementsByTagName('res')[0].getAttribute('duration')
         result.append({ 'title':title, 'link':link, 'duration': dur, 'id':id })
      return result
def getDLNAItems(id='64'):
   try:
      client = DLNAClient()
      c, i = client.GetContainers(id)
      return c,i
   except:
      return [],[]
if __name__ == "__main__":
   print(str(getDLNAItems('64$2$0')))
