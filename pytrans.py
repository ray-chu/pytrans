#!/usr/bin/python
# -*- coding: utf-8 -*

import sys
import requests
import xml.etree.ElementTree as ET
import curses
import terminalsize
#stdscr = curses.initscr()

class color:
   PURPLE = '\033[95m'
   GRAY = '\033[30m'
   GREY = '\033[37m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

### iciba dictionary
class iciba:
   def __init__(self):
      self.url_base='http://dict-co.iciba.com/api/dictionary.php?key=628A9B23F5595B6F44E4DBEB870CEF0B&w='
      self.source="iciba.com"
   def query(self,word):
      url=self.url_base+word
      response=requests.get(url)
      #### here's most confusing part. 
      #### Although the xml file fetched contains UTF-8 characters, the xml file itself is typically coded as ISO-8859-1 (plain text).
      #### But when using response.text to get the xml file content, python will think the xml itself as an UTF coded content. So by default, python will add a 'u' in front of response.text. (It will change nothing else, since UTF and plain text are same for ascii)
      #### However, if we want to display the UTF charater, we must delete the front 'u'. The reason is python's print function automatically recoginize '\x*' data as UTF-8. If there's a 'u' in front of the word, print cannot recoginize it. For example:
      #### >>> s="中文"
      #### >>> s
      #### '\xe4\xb8\xad\xe6\x96\x87'
      #### >>> print '\xe4\xb8\xad\xe6\x96\x87'
      #### 中文
      #### >>> print u'\xe4\xb8\xad\xe6\x96\x87'
      #### ä¸­æ

      #### So in order to print things out(or send to ET to parse), our first step is to remove the 'u'. That is tell python the content is plain text
      text_codec=response.encoding
      #print response.text.encode(response.encoding)
      root=ET.fromstring(response.text.encode(response.encoding))
      ps_num=1
      pron_link=[]
      pos_num=1
      acceptation_num=1
      sent_num=1
      sent_start=False
      print("")
      for child in root:
         if(child.tag=='key' and child.text):
            print(color.BOLD+child.text+color.END+"    "+color.GREY+"Source: "+self.source+color.END)
         elif(child.tag=='ps' and child.text):
            if(ps_num==1):
               print(color.RED+u"英[ "+child.text+" ]  "+color.END),
            elif(ps_num==2):
               print(color.RED+u"美[ "+child.text+" ]  \n"+color.END)
            ps_num+=1
         elif(child.tag=='pron' and child.text):
            pron_link.append(child.text)
         elif(child.tag=='pos' and child.text):
            print ('- '+color.GREEN+child.text+' '+color.END),
            pos_num+=1
         elif(child.tag=='acceptation' and child.text):
            if(pos_num>1):
               print color.GREEN+child.text[:-1]+color.END
            acceptation_num+=1
         elif(child.tag=='sent'):
            if(sent_start==False):
               print ""
               sent_start=True
            print color.PURPLE+str(sent_num)+'. '+child[0].text[1:-1]+color.END
            print color.CYAN+child[1].text[1:]+color.END
            sent_num+=1




###   youdao dictionary
class youdao:
   def __init__(self):
      self.url_base="http://fanyi.youdao.com/openapi.do?keyfrom=virginia&key=1553878309&type=data&doctype=xml&version=1.1&q="
      self.source="fanyi.youdao.com"
   def query(self,word):
      width, height = terminalsize.get_terminal_size()
      dividing_line="-"*width+'\n'
      print dividing_line
      url=self.url_base+word
      response=requests.get(url)
      text_codec=response.encoding
      #print response.text.encode(response.encoding)
      root=ET.fromstring(response.text.encode(response.encoding))
      ### tags needs to be processed
      ### tags=['errorCode','basic','translation','web']
      ### error code 
      error_code=root.find('errorCode')
      if(error_code.text=='20'):
         print "You are so verbose. Queried string must be shorter than 200."
      elif(error_code.text=='30'):
         print "Life is imperfect. So we simply cannot find the translations for this word."
      elif(error_code.text=='40'):
         print "Which language are you querying? Currently we just support Chinese and English."
      elif(error_code.text=='50'):
         print "Obviously, the developer of this app is a poor guy. He doesn't have a vaild key. And Youdao is very mean."
      if(error_code.text!='0'):
         return
      ### query key
      query_key=root.find('query')
      if(query_key.text):
         print (color.BOLD+query_key.text+color.END+"    "+color.GREY+"Source: "+self.source+color.END)
      else:
         return
      ### basic dictionary
      basic=root.find('basic')
      if(basic is not None):
         uk_phonetic=basic.find('uk-phonetic')
         if(uk_phonetic is not None):
            print(color.RED+u"英[ "+uk_phonetic.text+" ]  "+color.END),
         us_phonetic=basic.find('us-phonetic')
         if(us_phonetic is not None):
            print(color.RED+u"美[ "+us_phonetic.text+" ]")
         print ""
         explains=basic.findall('explains')      
         if(explains is not None):
            for expl in explains:
               exs=expl.findall('ex')
               if(exs is not None):
                  for ex in exs:
                     print ('- '+color.GREEN+ex.text+' '+color.END)
            print ""
      ### Youdao translate
      translation=root.find('translation')
      if(translation is not None):
         print (color.GREY+u"-- 有道翻译 --"+color.END)
         paras=translation.findall('paragraph')
         if(paras is not None):
            for para in paras:
               print ('- '+color.GREEN+para.text+' '+color.END)
            print ""
      ### Web search
      web=root.find('web')
      if(web is not None):
         print (color.GREY+u"-- 网络释义 --"+color.END)
         explains=web.findall('explain')
         if(explains is not None):
            for expl in explains:
               key=expl.find('key')
               if(key is not None):
                  print (key.text+" - "),
               value=expl.find('value')
               if(value is not None):
                  exs=value.findall('ex')
                  if(exs is not None):
                     for ex in exs:
                        print (color.CYAN+ex.text+color.END),
               print ""

                                       
            
if __name__ == "__main__":
    word_list=sys.argv[1:]
    
    ciba_instance=iciba()
    youdao_instance=youdao()
    for i in word_list:
       ciba_instance.query(i)
       youdao_instance.query(i)
