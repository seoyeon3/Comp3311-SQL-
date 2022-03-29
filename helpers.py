# COMP3311 21T3 Ass2 ... Python helper functions
# add here any functions to share between Python scripts 
# you must submit this even if you add nothing
import re

def getProgram(db,code):
  cur = db.cursor()
  cur.execute("select * from Programs where code = %s",[code])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getStream(db,code):
  cur = db.cursor()
  cur.execute("select * from Streams where code = %s",[code])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getStudent(db,zid):
  cur = db.cursor()
  qry = """
  select p.*, c.name
  from   People p
         join Students s on s.id = p.id
         join Countries c on p.origin = c.id
  where  p.id = %s
  """
  cur.execute(qry,[zid])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info


#my own function

def getProgramInfo(db,code): #function that print program information
  cur = db.cursor()
  qry = """
  select code, p_name, p_uoc, p_dur, og_name from q2_program 
  where code = %s
  """
  cur.execute(qry,[code])
  _code = 'first'
  for tup in cur.fetchall():
    code, p_name, p_uoc, p_dur, og_name = tup
    year = p_dur / 12
    if (_code == 'first'):
      print(f'{code} {p_name}, {p_uoc} UOC, {year} years') 
      print(f'- offered by {og_name}') 
      _code = code
    
  print("Academic Requirements:")  

def getStreamInfo(db,stream):
  cur = db.cursor()
  qry = """
  select code, str_name, org from q2_stream
  where code = %s
  """
  cur.execute(qry,[stream])
  _code = 'first'
  for tup in cur.fetchall():
    code, str_name, org = tup
    if (_code == 'first'):
      print(f'{code} {str_name}') 
      print(f'- offered by {org}') 
      _code = code
    
  print("Academic Requirements:")  

def get_minmax_uoc(min,max,name,aog_def):
  if min == None and max == None: #min and max are not exist
    print(f'{name}')
    

  elif min == max: #min and max both are same
    if aog_def == "FREE####":
      print(f'{min} UOC courses of Free Electives')
    elif aog_def == "GEN#####":   
      print(f'{min} UOC of General Education')
    else:  
      print(f'{min} UOC courses from {name}')

  elif min == None and max != None: #only max exists
    if aog_def == "FREE####":
       print(f'up to {max} UOC courses of Free Electives')
    elif aog_def == "GEN#####":
      print(f'up to {max} UOC of General Education')
    else:   
      print(f'up to {max} UOC courses from {name}')

  elif min != None and max == None: #only min exists
    if aog_def == "FREE####":
      print(f'at least {min} UOC of Free Electives')
    elif aog_def == "GEN#####":
      print(f'at least {min} UOC of General Education')
    else:   
      print(f'at least {min} UOC courses from {name}')       

  elif min != None and max != None: #min and max both exist
    if aog_def == "FREE####":
      print(f'between {min} and {max} UOC of Free Electives')
    elif aog_def == "GEN#####":
      print(f'between {min} and {max} UOC of General Eduaction')
    else:
      print(f'between {min} and {max} UOC courses from {name}')

def getAlternative(db,code,i):
  code[i]=re.sub('{|}','',code[i]) #to remove {}
  substr=re.split(';',code[i])
  for i in range(len(substr)):
    s_name = sub_name(db,substr[i]) #return subject name
    if i == 0:
      print(f'- {substr[i]} {s_name}')
      
    else: 
      print(f'  or {substr[i]} {s_name}') 
      

def sub_name(db,code):
  cur = db.cursor()
  qry = """
  select name from subjects 
  where subjects.code = %s
  """
  cur.execute(qry,[code])
  s_name = cur.fetchone()
  if s_name == None:
    s_name = '???'
  else:
    s_name = str(s_name)

    match = re.search("\"", s_name)       
    if match: #if "
      s_name = re.match("(\(\")(.*)(\",\))",s_name)
    else:
      s_name = re.match("(\(')(.*)(',\))",s_name)
    s_name = s_name.group(2)
  return s_name

def stream_name(db,code):
  cur = db.cursor()
  qry = """
  select name from streams 
  where streams.code = %s
  """
  cur.execute(qry,[code])
  str_name = cur.fetchone()
  if str_name == None:
    str_name = '???'
  else:
    str_name = str(str_name)
    str_name = re.sub("'|,|\(|\)","",str_name) #to remove ' , ()
  return str_name

def getProgramReq(db,code):
  cur = db.cursor()
  qry = """
  select aog_definition, aog_type, aog_name, aog_defby, r_min ,r_max from q2_program
  where code = %s
  """
  cur.execute(qry,[code])
  for tup in cur.fetchall():
    codes, type, aog_name, aog_defby, min, max = tup
    _code=codes.split(",") #seperate codes into a code
    str_count = 0 

    if aog_defby == "enumerated": 
      _code=codes.split(",")
      str_count = 0

      if type == "stream":  #if the type is stream
        str_count = str_count + 1
        print(f'{str_count} stream(s) from {aog_name}')
        for i in range(len(_code)): 
          streamName = stream_name(db,_code[i]) #return stream_name
          print(f'- {_code[i]} {streamName}')

      if type == "subject":
        if len(_code) == 1: #if there is only one course
          print(aog_name)
        else:   #if theres more than one courses 
           print(f'all courses from {aog_name}')

        for i in range(len(_code)):
          match = re.search("^{", _code[i])       
          if match: #if alternative course e.g.MATH1131 MATH1231
            getAlternative(db,_code,i)

          else: #not alternative course
            s_name = sub_name(db,_code[i])
            print(f'- {_code[i]} {s_name}') 


    else: #pattern
      if codes == "GEN#####":
        get_minmax_uoc(min,max,aog_name,codes)

      else: #pattern but not general course
        get_minmax_uoc(min,max,aog_name,codes)
        print(codes)
        

def getStreamReq(db,stream): #function that print about academic requirements
  cur = db.cursor()
  qry = """
  select code, r_name, r_min, r_max, aog_type, aog_defby, aog_def from q2_stream
  where code = %s
  """
  cur.execute(qry,[stream])
  for tup in cur.fetchall():
    code, r_name, r_min, r_max, aog_type, aog_defby, aog_def = tup
    get_minmax_uoc(r_min,r_max,r_name,aog_def)
    if aog_defby == "enumerated": 
      course = re.split(',',aog_def)
      for i in range(len(course)):
        match = re.search("^{", course[i])  
        if match:
          getAlternative(db,course,i)
        else:
          s_name = sub_name(db,course[i]) #return subject name
          print(f'- {course[i]} {s_name}')
          
    elif aog_defby == "pattern":
      if aog_def != "FREE####":
        print(f'- courses matching {aog_def}')  


#Q3 functions


def getStudentInf (db,zid):
  cur = db.cursor()
  qry = """
  select * from studentInfo
  where zid = %s
  """
  cur.execute(qry,[zid])
  for tup in cur.fetchall():
    zid, family, given,  prg_code, prg_title, str_code, str_title = tup
    print(f'{zid} {family}, {given}')
    print(f'  {prg_code} {prg_title}')
    print(f'  {str_code} {str_title}')
    
           
def getCurrentUOC(db, type, rule, uoc,UncoreUOC):
  
  UncoreType = ['FE','PE','GE']
  if type in UncoreType:
    value = UncoreUOC.get(rule)
    if value == None:
      UncoreUOC[rule] = uoc
    else:
      UncoreUOC[rule] = UncoreUOC[rule] + uoc
  return UncoreUOC
  

def getRemainingForFail(db,zid):
  cur = db.cursor()
  qry = """
  select * from transcript
  where zid = %s
  """
  cur.execute(qry,[zid])
  failGrades = ['AF','FL','UF']
  failCourse = dict()
  for tup in cur.fetchall():
    zid, coursecode, term, coursetitle, mark, grade, uoc, type, rule = tup
    if grade in failGrades: #if fail
      value = failCourse.get(coursecode)
      if value == None:
        failCourse[coursecode] = 1
    else:  
      if coursecode in failCourse.keys(): #if course was fail
        del failCourse[coursecode] #delete coursecode key bc now it pass the course
  return failCourse



def GetallCourse (db, zid):
  cur = db.cursor()
  qry = """
  select definition from all_rulename
  where zid = %s
  and type = 'CC'
  """
  all = []
  cur.execute(qry,[zid])
  for tup in cur.fetchall():
    codes, = tup
    _code = re.split(',',codes)
    for i in range(len(_code)):
      all.append(_code[i])
  return all

def GetcompletedCourse(db,zid):
  cur = db.cursor()
  qry = """
  select coursecode from completed_courses
  where zid = %s
  """
  completed = []
  cur.execute(qry,[zid])
  for tup in cur.fetchall():
    Coursecode, = tup
    completed.append(Coursecode)
  return completed

def remaining(db,zid):
  all = GetallCourse(db,zid)
  completed = GetcompletedCourse(db,zid)
  failCourse = getRemainingForFail(db,zid)
  for i in range (len(all)):
    for j in range (len(completed)):
      match = re.search(completed[j],all[i])
      if match:
        if completed[j] not in failCourse.keys():
          all[i] = "done"        
  return all


def GetRemaining (db, zid):
  print("\nRemaining to complete degree:")
  a = remaining(db,zid)
  for i in range(len(a)):
    if a[i] != "done":
      match = re.search("^{", a[i])  
      if match:
        getAlternative(db,a,i)
      else:
        s_name = sub_name(db,a[i]) #return subject name
        print(f'- {a[i]} {s_name}')
  

def getRemainUOC(db,zid):
  cur = db.cursor()
  qry = """
  select zid, coursecode, term, grade, uoc, type, rule, min, max 
  from WithAllRule
  where zid = %s
  """
  cur.execute(qry,[zid])
  _uoc = dict()
  failGrades = ['AF','FL','UF']

  for tup in cur.fetchall():
    zid, coursecode, term, grade, uoc, type, rule, min, max = tup
    if grade in failGrades:
      uoc = 0
    if type == 'PE' or type == 'GE':
      value = _uoc.get(rule)
      if value == None:
        _uoc[rule] = uoc
      else:
        _uoc[rule] = _uoc[rule] + uoc
  print(_uoc)
  


def free_gen_elec_MinMax(db,zid):
  cur = db.cursor()
  qry = """
  select * from all_gen_free_elec
  where zid = %s
  """
  cur.execute(qry,[zid])
  rules = []
  min_uoc = dict()
  max_uoc =dict()
  for tup in cur.fetchall():
    zid, rule, type, min, max = tup
    min_uoc[rule] = min
    max_uoc[rule] = max
    rules.append(rule)
  return min_uoc, max_uoc, rules
    


def check_free_exist(db,zid):
  cur = db.cursor()
  qry = """
  select * from all_gen_free_elec where type = 'FE'
  and zid = %s
  """
  cur.execute(qry,[zid])
  free = cur.fetchone()
  if free == None:
    return 0
  else:
    return 1  
  


def CheckExceedUOC(UncoreUOC, rule, _min, _max, uoc):
  exceed = 0
  value = UncoreUOC.get(rule)
  if value!= None:
    if _max[rule] == None: #max doesn't exist
      if UncoreUOC[rule] > _min[rule]: #compare with min
        uoc = 0
        exceed =  1
    else: #max exist
      if UncoreUOC[rule] > _max[rule]: #compare with max
        uoc = 0
        exceed = 1
        
  return exceed, uoc


def completed (db,zid):
  failGrades = ['AF','FL','UF']
  UncoreUOC = dict() 
  _min, _max, rules = free_gen_elec_MinMax(db,zid) #여기서 print해줌
  total_uoc = 0
  cur = db.cursor()
  qry = """
  select * from transcript
  where zid = %s
  """
  cur.execute(qry,[zid])
  for tup in cur.fetchall():
    zid, coursecode, term, coursetitle, mark, grade, uoc, type, rule = tup
    if mark == None: #change null mark to -
      mark = '  -'  

    if grade in failGrades:
      uoc = 0 #if fail, uoc = 0
      print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}   fail does not count')
    
    else: #not fail grade
      if rule != '':
        match = re.search('\+', rule)  
        if match:
          _rules = re.split(' \+ ', rule)
          getCurrentUOC(db, type, _rules[0], uoc, UncoreUOC)
          getCurrentUOC(db, type, _rules[1], uoc, UncoreUOC)
          #CheckExceedUOC(UncoreUOC, rules[0], _min, _max, uoc)
          #CheckExceedUOC(UncoreUOC, rules[1], _min, _max, uoc)
          print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc towards {rule}')
        else: #no multiple rule
          getCurrentUOC(db, type, rule, uoc, UncoreUOC)
          _uoc = uoc #save uoc before uoc turn to zero
          exceed, uoc = CheckExceedUOC(UncoreUOC, rule, _min, _max, uoc)
          if exceed == 1:
            UncoreUOC[rule] = UncoreUOC[rule] - _uoc
            print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc does not satisfy any rule')
          else:
            print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc towards {rule}')
      
      else: #rule exist
        free = check_free_exist(db,zid)
        if free == 0:
          uoc = 0 #if no rule, uoc = 0 
          print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc does not satisfy any rule')
        else: #free = 1
          rule = "Free Electives"
          type = 'FE'
          getCurrentUOC(db, type, rule, uoc, UncoreUOC)
          print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc towards {rule}')

    total_uoc = total_uoc + uoc
  print(f'UOC = {total_uoc} so far')
  GetRemaining (db, zid)


  for i in range(len(rules)):

    match = re.search('Free|General',rules[i])
    if match:
      if rules[i] == 'General Education':
        name = rules[i]
      else: #free
        name = 'Free Electives'
        UncoreUOC[rules[i]] = UncoreUOC['Free Electives']
      prep = 'of'
    else: #not Free/Gen  
      name = rules[i]
      match2 = re.search('Course', rules[i])
      if match2:
        prep = 'from'
      else:  
        prep = 'courses from'
    
    min = _min[rules[i]]
    max = _max[rules[i]]  

    value = UncoreUOC.get(rules[i])
    if value == None: #there's no complete course but remaining
      
      if min != None and max == None: #only min exist
        print(f'at least {min} UOC {prep} {name}')

      elif min == None and max != None: #only max exist
        print(f'up to {max} UOC {prep} {name}')
        
      elif min != None and max != None:
        if min == max:
          print(f'{min} UOC {prep} {name}')
        else:  
          print(f'between {min} and {max} UOC {prep} {name}')

    else: #there's complete course and also remaining

      if min != None and max == None: #only min exist
        diff = min - UncoreUOC[rules[i]]
        if diff != 0:
          print(f'at least {diff} UOC {prep} {name}')
          #gen free 처리 해줘야 함


      if min == None and max != None: #only max exist
        diff = max - UncoreUOC[rules[i]]
        if diff != 0:
          print(f'up to {diff} UOC {prep} {name}')


      if min != None and max != None: #min and max exist
        if min == max:
          diff = min - UncoreUOC[rules[i]]
          if diff != 0:
            print(f'{diff} UOC {prep} {name}')

        else:
          diff1 = min - UncoreUOC[rules[i]]
          diff2 = max - UncoreUOC[rules[i]]
          if diff2 == 0:
            a =  3
          elif diff1 != 0 and diff2 != 0: 
            a=1
          else:   
            print(f'between {diff1} and {diff2} UOC {prep} {name}')



  #print("\n\n") 
  #print(_min)
  #print(_max)
  #print(UncoreUOC)        

            
def progWithThree(db, zid, progCode, strmCode):
  failGrades = ['AF','FL','UF']
  cur = db.cursor()
  qry1 = """
  create or replace view pg_rule(rule, ruleType, min, max, defby, def)
  as
  select r.name, r.type, r.min_req, r.max_req, aog.defby, aog.definition
  from (select * from program_rules where program = %s) a
  join rules r on r.id = a.rule
  join (select * from aog where type = 'subject')aog on aog.id = r.ao_group 
  """
  cur.execute(qry1,[progCode])

  qry2 = """
  create or replace view st_rule
  as
  select r.name, r.type, r.min_req, r.max_req, aog.defby, aog.definition
  from
  (select * from streams where code = %s) a
  join stream_rules st_r on st_r.stream = a.id
  join rules r on r.id = st_r.rule
  join aog on aog.id = r.ao_group
  """  
  cur.execute(qry2,[strmCode])

  qry3 = """
  create or replace view all_rule
  as
  select * from st_rule
  union all
  select * from pg_rule
  """
  cur.execute(qry3)

  qry4 = """
  select coursecode, term, coursetitle, mark, grade, uoc from completed_courses
  where zid = %s
  """

  qry5= """
  select * from all_rule
  """


  free = 0
  cur.execute(qry5)
  for tup in cur.fetchall():
    rule, r_type, min, max, d_type, df = tup
    #print(tup)
    if r_type == 'FE':
      free = 1
    
 

  total_uoc = 0
  cur.execute(qry4,[zid])
  for tup in cur.fetchall(): #complete course check
    coursecode, term, coursetitle, mark, grade, uoc = tup
    if mark == None: #change null mark to -
      mark = '  -'
    if grade in failGrades:
      uoc = 0 #if fail, uoc = 0
      print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}   fail does not count')
    else: #none fail
      cur.execute(qry5)
      for tup in cur.fetchall(): #rule check
        rule, r_type, min, max, d_type, df = tup  
        match = re.search(coursecode, df)
        if match:
          rulename = rule
          break
        else: #no rulename
          if d_type == 'pattern':
            subs = coursecode[0:5]
            match = re.search(subs, df)
            if match:
               rulename =rule
               break
          else: #pattern also doesn't match    
            if free == 1:
              rulename = 'Free Electives'
            else:  
              rulename = 'does not satisfy any rule' 
      print(f'{coursecode} {term} {coursetitle:<32s}{mark:>3} {grade:2s}  {uoc:2d}uoc towards {rulename}')
    total_uoc = total_uoc + uoc
  print(f'UOC = {total_uoc} so far')    


def studentInfoFor3(db, zid, progCode, strmCode): #if the # of argument is three then use this function to print student's inf
  cur = db.cursor()
  qry1 = """
  select family, given  from people where id = %s
  """
  cur.execute(qry1,[zid])
  family, given = cur.fetchone()
  
  qry2 = """
  select code, name from programs where code = %s
  """
  cur.execute(qry2,[progCode])
  pg_code, pg = cur.fetchone()
  
  qry3 = """
  select code, name from streams where code = %s
  """
  cur.execute(qry3,[strmCode])
  st_code, st  = cur.fetchone()

  print(f'{zid} {family}, {given}')
  print(f'  {pg_code} {pg}')
  print(f'  {st_code} {st}')


def pgCheck(db,zid,progCode): #to check the lastes program code and given program code are same, since, codes for 3 arguments are not completed
  same = 0
  cur = db.cursor()
  qry1 = """
  select pg_code from lastpgenrol 
  where zid = %s
  """
  cur.execute(qry1,[zid])
  for tup in cur.fetchall():
    pg, = tup
  pg = str(pg)
  match = re.search(pg, progCode)       
  if match: #if "
    same = 1
  return same  
  
  




  
  







