#!/usr/bin/python3
# COMP3311 21T3 Ass2 ... print a transcript for a given student

import sys
import psycopg2
import re
from helpers import getStudent

#total_uoc:counting towards the degree (from subjects you passed)
#UOC: counted in the WAM (from all subjects attempted)
#Note that UOC is for all courses passed
#UOC-for-WAM is for all courses attempted. 즉, 지금까지 한 모든 코스의 uoc를 사용해 wam을 계산함 

# define any local helper functions here

def transcript(id):
  cur = db.cursor()
  qry = """
  select * from q1 
  where student = %s
  """
  uoc_wam = 0
  _mark = 0
  ach_uoc = 0
  cur.execute(qry,[id])
  _first = "first"
  for tup in cur.fetchall():
    _id, CourseCode, Term, CourseTitle, Mark, Grade, UOC, family, given =tup
    uoc_changed = UOC

    if(_first == "first"): #to print name only one times
      print(f'{_id} {family}, {given}')
      _first = "not_first"

    if Mark == None: #change null mark to -
      Mark = '  -'  


    failGrades = ['AF','FL','UF']
    nothingGrades = ['AS','AW','PW','RD','NF','LE','PE','WD','WJ',None]  
    gradesForWams = ['HD','DN','CR','PS','AF','FL','UF']

    if Grade in failGrades:
      uoc_changed = '  fail'
      print(f'{CourseCode} {Term} {CourseTitle:<32s}{Mark:>3} {Grade:2s} {uoc_changed}')
    elif Grade in nothingGrades :
      if Grade == None:
        Grade = '' #what do we need to print out for Grade if it is none I just leave it as ''
      print(f'{CourseCode} {Term} {CourseTitle:<32s}{Mark:>3} {Grade:2s}')

    else:     #'A','B', 'C', 'D', 'HD','DN','CR','PS','XE','T','SY','EC','NC'
      print(f"{CourseCode} {Term} {CourseTitle:<32s}{Mark:>3} {Grade:2s}  {UOC:2d}uoc")
      ach_uoc = ach_uoc + UOC #calculate achived uoc



    if Grade in gradesForWams:
      if(Grade == 'AF'):
        Mark = 0 #treat AF mark as zero
      _mark = _mark + Mark * UOC  #calculate sum mark
      uoc_wam = uoc_wam + UOC  #calculate uoc for wam
    
  wam = round(_mark/uoc_wam,1)
  #print(f'UOC = {ach_uoc}, WAM = {_mark}/{uoc_wam} = {wam}')
  print(f'UOC = {ach_uoc}, WAM = {wam}')
  


###given codes


### set up some globals

usage = f"Usage: {sys.argv[0]} zID"
db = None

### process command-line args

argc = len(sys.argv)
if argc < 2:
  print(usage)
  exit(1)
zid = sys.argv[1]
if zid[0] == 'z':
  zid = zid[1:8]
digits = re.compile("^\d{7}$")
if not digits.match(zid):
  print(f"Invalid student ID {zid}")
  exit(1)

# manipulate database

try:
  db = psycopg2.connect("dbname=mymyunsw")
  stuInfo = getStudent(db,zid)
  if not stuInfo:
    print(f"Invalid student ID {zid}")
    exit()

  transcript(zid) #return the transcript for corresponding student

  # print(stuInfo) # debug
  #print(zid)
  # Print transcript for Student
  # ... add your code here ...


except Exception as err:
  print("DB error: ", err)
finally:
  if db:
    db.close()

