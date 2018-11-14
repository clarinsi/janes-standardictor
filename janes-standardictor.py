#!/usr/bin/python
#-*-coding:utf8-*-
import sys
import re
import numpy as np
import os
import warnings
reldir=os.path.dirname(os.path.realpath(__file__))+'/'

def annotation_iterator(path):
  text=open(path).read().decode('utf8')[9:-4]
  for instance in text.split('###\n\n###janes.')[:-1]:
    lines=instance.split('\n')
    genre=lines[0].split('.')[0]
    id=lines[0][:-3]
    technical=lines[1].strip()[2:]
    linguistic=lines[2].strip()[2:]
    if technical=='' and linguistic=='':
      continue
    if technical not in ['0','1','2','3'] or linguistic not in ['0','1','2','3']:
      sys.stderr.write('### Bad value in '+path+'!\n'+instance)
      continue
    technical=int(technical)
    linguistic=int(linguistic)
    if technical==0 or linguistic==0:
      continue
    text='\n'.join(lines[3:])
    if '\n\n' in text:
      sys.stderr.write('### Double newline in '+path+'!\n'+instance)
    yield genre,id,technical,linguistic,text

def text_cleaner(text):
  #hashtags=re.compile(r'#\w+',re.UNICODE)
  #mentions=re.compile(r'@\w+',re.UNICODE)
  #urls=re.compile(r'https?://[.a-zA-Z0-9/_-]+')
  #smileys=re.compile(r':\-?[)(DPp]')
  all=re.compile(r'https?://[.a-zA-Z0-9/_-]+|[#@]\w+|[:;]\-?[)(DPp]+')
  return all.sub('#REP#',text).replace('#LINK#','#REP#').replace('...',u'…')

def alphanum_tokens(text):
  return re.findall(r'[^\W_]+',text.replace('#REP#',' '),re.UNICODE)

def alpha_tokens(text):
  alpha=re.compile(r'^[^\W\d_]+$',re.UNICODE)
  tokens=[]
  for token in alphanum_tokens(text):
    if alpha.match(token)!=None:
      tokens.append(token)
  return tokens

def punc_space_ratio(text):
  punc=len(re.findall(r'[.,!?:;]',text))
  if punc==0:
    return 0.
  else:
    return 1.*len(re.findall(r'[.,!?:;](\s|$)',text))/punc

def space_punc_ratio(text):
  punc=len(re.findall(r'[.,!?:;]',text))
  if punc==0:
    return 0.
  else:
    return 1.*len(re.findall(r'\s[.,!?:;]',text))/punc

def ucase_char_ratio(text):
  ucase=0.
  case=0.
  for char in text.replace('#REP#',''):
    if char.lower()!=char.upper():
      case+=1
      if char!=char.lower():
        ucase+=1
  if case==0.:
    return 0.
  else:
    return ucase/case

def ucase_token_ratio(text):
  ucase=0.
  case=0.
  for token in alpha_tokens(text):
    if token.upper()==token:
      ucase+=1
    case+=1
  if case==0.:
    return 0.
  else:
    return ucase/case

def tcase_token_ratio(text):
  tcase=0.
  case=0.
  for token in alpha_tokens(text):
    if token.title()==token:
      tcase+=1
    case+=1
  if case==0:
    return 0.
  else:
    return tcase/case

def punc_ratio(text):
  punc=0.
  punc_chars='.,:;_-!?'
  for char in text:
    if char in punc_chars:
      punc+=1
  return punc/len(text)

def sentpunc_ucase_ratio(text):
  ucase=0.
  case=0
  for sentpunc in re.findall(r'[.!?]\s+[^\W\d_]',text.replace('#REP#',' '),re.UNICODE):
    if sentpunc.upper()==sentpunc:
      ucase+=1
    case+=1
  if case==0:
    return 0.
  else:
    return ucase/case

def parstart_ucase_ratio(text):
  ucase=0.
  case=0.
  for paragraph in text.strip().split('\n'):
    if len(paragraph)==0:
      continue
    if paragraph[0].upper()!=paragraph[0].lower():
      case+=1
      if paragraph[0].upper()==paragraph[0]:
        ucase+=1
  if case==0:
    return 0
  else:
    return ucase/case

def parend_sentpunc_ratio(text):
  sentpunc=0.
  par=0.
  for paragraph in text.strip().split('\n'):
    if len(paragraph)==0:
      continue
    if paragraph[-1] in u'.!?…':
      sentpunc+=1
    par+=1
  return sentpunc/par

def alpha_ratio(text):
  text=text.replace('#REP#','')
  if len(text)==0:
    return 0.
  else:
    return 1.*len(re.findall(r'[^\W\d_]',text,re.UNICODE))/len(text)

def alphanum_token_ratio(text):
  alphanum=0.
  any=0.
  for token in alphanum_tokens(text):
    if re.search(r'\d',token)!=None and re.search(r'[^\W_]',token)!=None:
      alphanum+=1
    any+=1
  if alphanum==0:
    return 0.
  else:
    return alphanum/any

def weirdbracket_ratio(text):
  weird=0.
  bracket=0.
  for index,char in enumerate(text):
    if char in '()[]':
      bracket+=1
      if index+1!=len(text):
        if char in '([' and text[index+1]==' ':
          weird+=1
      if index!=0:
        if char in ')]' and text[index-1]==' ':
          weird+=1
  if bracket==0:
    return 0.
  else:
    return weird/bracket

def weirdquote_ratio(text):
  quote_count=text.count('"')
  if quote_count==0:
    return 0.
  else:
    return 1.*(len(re.findall(r'\S"\S',text))+len(re.findall(r'\s"\s',text)))/quote_count

def smiley(text):
  return len(re.compile(r'[:;]\-?[)(DPp]+').findall(text))

def char_repeat(text,num):
  return len(re.findall(r'(.)\1{'+str(num-1)+',}',text))

def alpha_repeat(text,num):
  return len(re.findall(r'([^\W\d_])\1{'+str(num-1)+',}',text,re.UNICODE))

def char_length(text):
  return len(text.replace('#REP#',''))

def token_rep_ratio(text):
  rep=0.
  all=0.
  prev=''
  for token in alpha_tokens(text):
    if prev==token:
      rep+=1
    all+=1
  if all==0:
    return 0.
  else:
    return rep/all

def cons_alpha_ratio(text):
  cons=0.
  all=0.
  for token in alpha_tokens(text):
    if re.search(r'[aeiou]',token.lower())==None:
      cons+=1
    all+=1
  if all==0:
    return 0.
  else:
    return cons/all

def vow_cons_ratio(text):
  vow=0.
  all=0.
  for char in text.replace('#REP#',''):
    if char.lower()!=char.upper():
      if char in 'aeiou':
        vow+=1
      all+=1
  if all==0:
    return 0.
  else:
    return vow/all

def alphabet_ratio(text):
  alph=0.
  all=0.
  alphabet=u'abcdefghijklmnoprstuvzščž'
  for char in text.replace('#REP#',''):
    if char.lower()!=char.upper():
      if char in alphabet:
        alph+=1
      all+=1
  if all==0:
    return 0.
  else:
    return alph/all

def short_token_ratio(text,thresh):
  short=0.
  all=0.
  for token in alpha_tokens(text):
    if len(token)<=thresh:
      short+=1
    all+=1
  if all==0:
    return 0.
  else:
    return short/all

#?character n-gram repetitions
# consonant bigram and trigram ratios
#?distance between expected and observed consontant n-gram distributions
# transformations (al|el|il-u, ) to be applied to tokens and sought in the lexicon (reku rekel, delu delal)
# tujejezični elementi
# splitting an long OOV around the middle and looking for the components in the lexicon

feature_names=['punc_space_ratio','space_punc_ratio','ucase_char_ratio','ucase_token_ratio','tcase_token_ratio','punc_ratio',
'sentpunc_ucase_ratio','parstart_ucase_ratio','parend_sentpunc_ratio','alpha_ratio','alphanum_token_ratio',
'weirdbracket_ratio','weirdquote_ratio','smiley','char_repeat_2','char_repeat_3','alpha_repeat_2','alpha_repeat_3',
'token_rep_ratio','cons_alpha_ratio','vow_cons_ratio','alphabet_ratio','short_token_ratio']

def string_features(text):
  clean_text=text_cleaner(text)
  features=[]
  features.append(punc_space_ratio(clean_text))#0
  features.append(space_punc_ratio(clean_text))#1
  features.append(ucase_char_ratio(clean_text))#2
  features.append(ucase_token_ratio(clean_text))#3
  features.append(tcase_token_ratio(clean_text))#4
  features.append(punc_ratio(clean_text))#5
  features.append(sentpunc_ucase_ratio(clean_text))#6
  features.append(parstart_ucase_ratio(clean_text))#7
  features.append(parend_sentpunc_ratio(clean_text))#8
  features.append(alpha_ratio(clean_text))#9
  features.append(alphanum_token_ratio(clean_text))#10
  features.append(weirdbracket_ratio(clean_text))#11
  features.append(weirdquote_ratio(clean_text))#12
  features.append(smiley(text))#13
  features.append(char_repeat(clean_text,2))#14
  features.append(char_repeat(clean_text,3))#15
  features.append(alpha_repeat(clean_text,2))#16
  features.append(alpha_repeat(clean_text,3))#17
  #features.append(char_length(clean_text))#18
  features.append(token_rep_ratio(clean_text))#18
  features.append(cons_alpha_ratio(clean_text))#19
  features.append(vow_cons_ratio(clean_text))#20
  features.append(alphabet_ratio(clean_text))#21
  features.append(short_token_ratio(clean_text,3))#22
  return features

def extend_with_czs(lexicon):
  for token in list(lexicon):
    token=token.replace(u'š','s').replace(u'č','c').replace(u'ž','z')
    lexicon.add(token)

def remove_vocal_oovs(lexicon):
  oov_lexicon=set()
  for token in lexicon:
    for index,char in enumerate(token):
      if char in 'aeiou' and index>0:
        token_mod=token[:index]+token[index+1:]
        if token_mod not in lexicon:
          oov_lexicon.add(token_mod)
  return oov_lexicon
#"""
sloleks=set([e.decode('utf8').strip() for e in open(reldir+'sl/sloleks-standard.txt')])
extend_with_czs(sloleks)
sloleks_vocal_oovs=remove_vocal_oovs(sloleks)
kresleks_10=set([e.decode('utf8').strip().split('\t')[1] for e in open(reldir+'sl/kresleks-freq.txt') if int(e.strip().split('\t')[0])>10])
extend_with_czs(kresleks_10)
kresleks_100=set([e.decode('utf8').strip().split('\t')[1] for e in open(reldir+'sl/kresleks-freq.txt') if int(e.strip().split('\t')[0])>100])
extend_with_czs(kresleks_100)
nonstandard=set([e.decode('utf8').strip() for e in open(reldir+'sl/janes-keywords.txt')])
extend_with_czs(nonstandard)
names=set([e.decode('utf8').lower().strip() for e in open(reldir+'sl/sloleks-names.txt')])
#print len(kresleks_100)
#"""
def oov_ratio(text,lexicon):
  oov=0.
  all=0.
  for token in alpha_tokens(text):
    if token.lower() not in lexicon:
      oov+=1
    all+=1
  if all==0:
    return 0.
  else:
    return oov/all

def short_oov_ratio(text,lexicon,thresh):
  oov=0.
  all=0.
  for token in alpha_tokens(text):
    if len(token)<=thresh:
      if token.lower() not in lexicon:
        oov+=1
      all+=1
  if all==0:
    return 0.
  else:
    return oov/all

def lowercased_names_ratio(text,lexicon):
  ln=0.
  all=0
  for token in alpha_tokens(text):
    if token.lower() in lexicon:
      all+=1
      if token.lower()==token:
        ln+=1
  if all==0:
    return 0.
  else:
    return ln/all

feature_names.extend(['oov_ratio_sloleks','oov_ratio_vocal_oovs','short_oov_ratio','oov_ratio_nonstandard','lowercased_names_ratio','oov_ratio_kresleks_10'])

def lexicon_features(text):
  clean_text=text_cleaner(text)
  features=[]
  features.append(oov_ratio(clean_text,sloleks))#23
  features.append(oov_ratio(clean_text,sloleks_vocal_oovs))#24
  features.append(short_oov_ratio(clean_text,sloleks,4))#25
  features.append(oov_ratio(clean_text,nonstandard))#26
  features.append(lowercased_names_ratio(clean_text,names))#27
  features.append(oov_ratio(clean_text,kresleks_10))#28
  return features

def corpus_features(text):
  return []

def all_features(text):
  features=[]
  features.extend(string_features(text))
  features.extend(lexicon_features(text))
  features.extend(corpus_features(text))
  return features

def serialize_example():
  from sklearn.grid_search import GridSearchCV
  from sklearn.svm import SVR
  from sklearn.preprocessing import StandardScaler
  from operator import itemgetter
  from sklearn.externals import joblib
  param_grid = {'C': [0.01,0.1,1,10,100,1000], 'gamma': [1,0.1,0.01,0.001,0.0001], 'kernel': ['rbf']}
  x,yt,yl=load_data('data/')
  sts=StandardScaler()
  x=sts.fit_transform(x)
  joblib.dump(sts,'models/scaler.pkl')
  reg=SVR()
  print '###TECHNICAL###'
  grid_search=GridSearchCV(reg, param_grid=param_grid,scoring='mean_absolute_error',n_jobs=24,cv=10)
  grid_search.fit(x,yt)
  print sorted(grid_search.grid_scores_,key=itemgetter(1),reverse=True)[0:3]
  reg=grid_search.best_estimator_
  reg.fit(x,yt)
  #print reg.dual_coef_
  #print reg.coef_
  joblib.dump(reg,'models/regressor_technical.pkl')
  print '###LINGUISTIC###'
  grid_search=GridSearchCV(reg, param_grid=param_grid,scoring='mean_absolute_error',n_jobs=24,cv=10)
  grid_search.fit(x,yl)
  print sorted(grid_search.grid_scores_,key=itemgetter(1),reverse=True)[0:3]
  reg=grid_search.best_estimator_
  reg.fit(x,yl)
  #print reg.dual_coef_
  #print reg.coef_
  from sklearn.externals import joblib
  joblib.dump(reg,'models/regressor_linguistic.pkl')

def annotate_tweets():
  import sys
  import xml.etree.ElementTree as ET
  from sklearn.preprocessing import StandardScaler
  from sklearn.externals import joblib
  reg_t=joblib.load('models/regressor_technical.pkl')
  reg_l=joblib.load('models/regressor_linguistic.pkl')
  sts=joblib.load('models/scaler.pkl')
  from xml.sax.saxutils import unescape
  for line in open('tviti_2015-04-30.xml'):
    if line.startswith('<tweet '):
      tid=re.search(r' id="(tid.\d+)"',line).group(1)
      text=unescape(re.search(r'<tweet .+?>(.+?)</tweet>',line).group(1).decode('utf8'))
      x=all_features(text)
      x=sts.transform(x)
      yt=reg_t.predict(x)[0]
      yl=reg_l.predict(x)[0]
      print tid, min(max(round(yt,1),1.0),3.0), max(min(round(yl,1),3.0),1.0), text.encode('utf8')
      sys.stdout.flush()

def annotate_comment():
  import sys
  import xml.etree.ElementTree as ET
  from sklearn.externals import joblib
  from sklearn.preprocessing import StandardScaler
  reg_t=joblib.load('models/regressor_technical.pkl')
  reg_l=joblib.load('models/regressor_linguistic.pkl')
  sts=joblib.load('models/scaler.pkl')
  tree = ET.parse('resources/comment/janes.comment.xml')
  root = tree.getroot()
  for news in root:
    for article in news:
      comments=article.find('comments')
      for comment in comments:
        id=comment.attrib['id']
        text=comment.find('text')
        text='\n'.join([e.text for e in text.findall('p') if e.text!=None])
        if len(text)==0:
          continue
        x=all_features(text)
        x=sts.transform(x)
        yt=reg_t.predict(x)[0]
        yl=reg_l.predict(x)[0]
        print id,min(max(round(yt,1),1.0),3.0),min(max(round(yl,1),1.0),3.0),text.encode('utf8').replace('\n',' ')
        sys.stdout.flush()

def annotate_forum():
  import sys
  import xml.etree.ElementTree as ET
  from sklearn.externals import joblib
  from sklearn.preprocessing import StandardScaler
  reg_t=joblib.load('models/regressor_technical.pkl')
  reg_l=joblib.load('models/regressor_linguistic.pkl')
  sts=joblib.load('models/scaler.pkl')
  tree = ET.parse('resources/forum/janes.forum.xml')
  root = tree.getroot()
  for forum in root:
    for thread in forum:
      for post in thread:
        id=post.attrib['id']
        text=post.find('text')
        text='\n'.join([e.text for e in text.findall('p') if e.text!=None and e.text!=''])
        if len(text)==0:
          continue
        x=all_features(text)
        x=sts.transform(x)
        yt=reg_t.predict(x)[0]
        yl=reg_l.predict(x)[0]
        print id,min(max(round(yt,1),1.0),3.0),min(max(round(yl,1),1.0),3.0),text.encode('utf8').replace('\n',' ')
        sys.stdout.flush()

def run(stream,reldir=''):
  from sklearn.externals import joblib
  from sklearn.preprocessing import StandardScaler
  reg_t=joblib.load(os.path.join(reldir,'sl/regressor_technical.pkl'))
  reg_l=joblib.load(os.path.join(reldir,'sl/regressor_linguistic.pkl'))
  sts=joblib.load(os.path.join(reldir,'sl/scaler.pkl'))
  X=[]
  for line in stream:
    x=all_features(line.decode('utf8'))
    x=np.array(x)
    #x=sts.transform(x)
    X.append(x)
  X=np.array(X)
  X=sts.transform(X)
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
  Yt=reg_t.predict(X)
  Yl=reg_l.predict(X)
  return zip(Yt,Yl)

if __name__=='__main__':
  reldir = os.path.dirname(os.path.abspath(__file__))
  import sys
  for yt,yl in run(sys.stdin,reldir):
    sys.stdout.write(str(min(max(round(yt,1),1.0),3.0))+'\t'+str(min(max(round(yl,1),1.0),3.0))+'\n')
