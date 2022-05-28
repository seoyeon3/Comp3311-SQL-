#!/usr/bin/python3
# COMP3311 21T3 Ass2 ... progression check for a given student

import sys
import psycopg2
import re
from helpers import getStudent, getProgram, getStream, getStudentInf, completed, progWithThree, studentInfoFor3, pgCheck
# define any local helper functions here

### set up some globals

usage = f"Usage: {sys.argv[0]} zID [Program Stream]"
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
  print("Invalid student ID")
  exit(1)

progCode = None
strmCode = None

if argc == 4:
  progCode = sys.argv[2]
  strmCode = sys.argv[3]
  #print(progCode)
  #print(strmCode)


# manipulate database

try:
  db = psycopg2.connect("dbname=mymyunsw")
  stuInfo = getStudent(db,zid)
  #print(stuInfo) # debug
  if not stuInfo:
    print(f"Invalid student id {zid}")
    exit()



  if argc != 4:
    getStudentInf(db,zid) 
    print("\nCompleted:")
    completed (db,zid)

  if progCode:
    progInfo = getProgram(db,progCode)
    if not progInfo:
      print(f"Invalid program code {progCode}")
      exit()
    #print(progInfo)  #debug

  if strmCode:
    strmInfo = getStream(db,strmCode)
    if not strmInfo:
      print(f"Invalid program code {strmCode}")
      exit()
    #print(strmInfo)  #debug


  if argc == 4:

    
    if pgCheck(db,zid,progCode): #if given program code is same with latest program code/ since, 3argument codes are not completed
      getStudentInf(db,zid) 
      print("\nCompleted:")
      completed (db,zid)
    else:
      studentInfoFor3(db, zid, progCode, strmCode)
      print("\nCompleted:")
      progWithThree(db, zid, progCode, strmCode)
    
  # if have a program/stream
  #   show progression check on supplied program/stream
  # else
  #   show progression check on most recent program/stream enrolment
  # ... add your code here ...

except Exception as err:
  print("DB error: ", err)
finally:
  if db:
    db.close()

