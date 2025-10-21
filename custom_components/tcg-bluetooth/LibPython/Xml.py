import xml.etree.ElementTree as ET
import re
import os
from .Dynamic import Dynamic

class Xml:
  def __init__(self, pString:str|ET.Element=None,pStripNS:bool=False):
    if pString is None: return
    if isinstance(pString, ET.Element):
      self.root = pString
    elif isinstance(pString, str):
      pString = re.sub('<\\?[^\\?]*\\?>', '', pString)
      if pStripNS:
        pString = re.sub(r'\sxmlns(:\S+)?="[^"]+"', '', pString)  # Remove xmlns declarations
        pString = re.sub(r'<(/?)(\S+):', r'<\1', pString)         # Remove namespace prefixes in tags
        pString = re.sub(r'(\s)\S+:(\S+=)', r'\1\2', pString)     # Remove namespace prefixes in attributes
      self.root = ET.fromstring(pString)

  def _SplitTag(self, pTag):
    if pTag.startswith('{'):
      ns, local = pTag[1:].split('}', 1)
      return ns, local
    return None, pTag

  def _ElementToDict(self, pElement):
    node = {}
    ns, tag = self._SplitTag(pElement.tag)
    if ns: node['NS'] = ns

    for k, v in pElement.attrib.items():
      node[k] = v #Store attributes as children
    children = list(pElement)
    if children:
      for child in children:
        c_ns, c_tag = self._SplitTag(child.tag)
        child_dict = self._ElementToDict(child)
        if c_tag in node:
          if not isinstance(node[c_tag], list):
            node[c_tag] = [node[c_tag]]
          node[c_tag].append(child_dict)
        else:
          node[c_tag] = child_dict
    else:
      text = pElement.text.strip() if pElement.text else ''
      if text or pElement.attrib or ns:
        if text:
          node['#text'] = text
      else:
        node = text if text else None
    return node

  def ToDynamic(self):
    ns, tag = self._SplitTag(self.root.tag)
    return Dynamic({tag: self._ElementToDict(self.root)})

  def _DictToElement(self, pTag, pDict):
    if isinstance(pDict, list):
      elem = ET.Element(pTag)
      for e in pDict:
        elem.append(self._DictToElement(pTag,e))
      return elem
    if not isinstance(pDict, dict):
      elem = ET.Element(pTag)
      elem.text = str(pDict)
      return elem
    ns = pDict.get("NS")
    full_tag = f"{{{ns}}}{pTag}" if ns else pTag
    elem = ET.Element(full_tag)
    for key, value in pDict.items():
      if key == "NS":
        continue
      elif key.startswith("@"):
        attr_name = key[1:]
        elem.set(attr_name, value)
      elif key == "#text":
        elem.text = value
      else:
        if isinstance(value, list):
          for v in value:
            elem.append(self._DictToElement(key, v))
        else:
          elem.append(self._DictToElement(key, value))
    return elem

  def ToXml(self, pDict:Dynamic, pHeader:str=''):
    if len(pDict) != 1: raise ValueError("Root tag required when dictionary has multiple root keys.")
    _Root = next(iter(pDict))
    root_elem = self._DictToElement(_Root, pDict[_Root])
    return pHeader + ET.tostring(root_elem, encoding="unicode")

  def GetValue(self,pID:str):
    _Node = self.root.find(f'./{pID}')
    if _Node is None: #Maybe stored as an attribute of the parent
      if not os.path.dirname(pID): return None
      _Node = self.root.find(f'./{os.path.dirname(pID)}')
      if _Node is None: return None
      if os.path.basename(pID) in _Node.attrib:
        return _Node.attrib[os.path.basename(pID)]
      return None
    return _Node.text

  def GetChildren(self,pID:str):
    _Children = self.root.find(f'./{pID}')
    if _Children is None: return []
    return [Xml(x) for x in _Children]    