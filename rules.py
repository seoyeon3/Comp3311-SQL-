#!/usr/bin/python3
# COMP3311 21T3 Ass2 ... print list of rules for a program or stream

import sys
import psycopg2
import re
from helpers import getProgram, getStream, getProgramInfo, getStreamInfo, getStreamReq, getProgramReq
# define any local helper functions here

### set up some globals
if len(sys.argv) != 1:
  code = sys.argv[1]


usage = f"Usage: {sys.argv[0]} (ProgramCode|StreamCode)"
db = None

### process command-line args

argc = len(sys.argv)
if argc < 2:
  print(usage)
  exit(1)
code = sys.argv[1]
if len(code) == 4:
  codeOf = "program"
elif len(code) == 6:
  codeOf = "stream"

try:
  db = psycopg2.connect("dbname=mymyunsw")

  if codeOf == "program":     #if argument if program
    progInfo = getProgram(db,code)
    getProgramInfo(db,code)
    getProgramReq(db,code)
    if not progInfo:
      print(f"Invalid program code {code}")
      exit()
    #print(progInfo)  #debug
    # List the rules for Program

    # ... add your code here ...

  elif codeOf == "stream": #if argument is stream
    strmInfo = getStream(db,code)
    getStreamInfo(db,code)
    getStreamReq(db,code)
    #str_req(code)


    if not strmInfo:
      print(f"Invalid stream code {code}")
      exit()
    #print(strmInfo)  #debug
    # List the rules for Stream
    # ... add your code here ...

except Exception as err:
  print(err)
finally:
  if db:
    db.close()



