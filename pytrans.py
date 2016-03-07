#!/usr/bin/python
# -*- coding: utf-8 -*

import sys

class color:
   PURPLE = '\033[95m'
   GRAY = '\033[30m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

if __name__ == "__main__":
    word_list=sys.argv[1:]
    import requests
    import xml.etree.ElementTree as ET
    url_base='http://dict-co.iciba.com/api/dictionary.php?key=628A9B23F5595B6F44E4DBEB870CEF0B&w='

    for i in word_list:
        url=url_base+i
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
                print(child.text)
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
            # else:
            #     print child.tag, child.text
