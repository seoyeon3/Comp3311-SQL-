-- COMP3311 21T3 Ass2 ... extra database definitions
-- add any views or functions you need into this file
-- note: it must load without error into a freshly created mymyunsw database
-- you must submit this even if you add nothing to it

-- Q1
create or replace view q1(student,CourseCode, Term, CourseTitle, Mark, Grade, UOC, family, given) 
as
select e.student, s.code, t.code, s.name, e.mark, e.grade, s.uoc, p.family, p.given
from course_enrolments e join courses c on (e.course = c.id)
join terms t on (c.term = t.id)
join subjects s on (c.subject = s.id)
join people p on (p.id = e.student)
order by e.student, t.starting, s.code
;


-- Q2

create or replace view q2_program(code, p_name, p_uoc, p_dur, og_name, aog_name, aog_type, aog_defby, aog_definition,r_min ,r_max)
as
select p.code, p.name, p.uoc, p.duration, ou.longname, aog.name, aog.type, aog.defby, aog.definition,r.min_req, r.max_req
from programs p join orgunits ou on (p.offeredby = ou.id)
join program_rules pr on (p.id = pr.program)
join rules r on (pr.rule = r.id)
join academic_object_groups aog on (r.ao_group = aog.id)
;

create or replace view q2_stream(code, str_name, org, r_name, r_min ,r_max, aog_type, aog_defby, aog_def)
as
select s.code, s.name, ou.longname, r.name, r.min_req, r.max_req, aog.type, aog.defby, aog.definition 
from streams s join orgunits ou on (s.offeredby = ou.id) 
join stream_rules sr on (s.id=sr.stream)
join rules r on (sr.rule=r.id)
join academic_object_groups aog on (r.ao_group=aog.id)
;

-- Q3 

--copy academic_object_groups to update the table and use for Q3
create table aog
as 
table academic_object_groups
;

--to delete all the # in the deifnition field from academic_object_groups table
UPDATE aog SET definition = replace(definition, '###', '');
UPDATE aog SET definition = replace(definition, '##', '');
UPDATE aog SET definition = replace(definition, '#', '');


create or replace view pgEnrolwithTerm(zid, partof,pg_code,term_code, term_starting)
as
select pg_e.student, pg_e.id, pg_e.program, t.code, t.starting
from program_enrolments pg_e 
join terms t on (t.id = pg_e.term)
order by student, t.starting desc
;

create or replace view lastPgEnrol
as
select distinct on (zid) zid as zid, partof, pg_code, term_code from pgEnrolwithTerm order by zid   
;

create or replace view studentInfo(zid, family_name, given_name, pg_code, pg, st_code, st)
as
select l.zid, p.family, p.given, l.pg_code, pg.name, st.code, st.name
from lastPgEnrol l
join people p on (p.id = l.zid)
join programs pg on (l.pg_code = pg.id)
join stream_enrolments st_e on (st_e.partof = l.partof)
join streams st on (st.id = st_e.stream)
order by l.zid
;


create or replace view completed_courses(zid, CourseCode, Term, starting, CourseTitle, Mark, Grade, UOC) 
as
select s.id, sb.code, t.code , t.starting, sb.name, c_e.mark, c_e.grade, sb.uoc from students s 
join course_enrolments c_e on (s.id = c_e.student)
join courses c on (c.id = c_e.course)
join subjects sb on (c.subject = sb.id)
join terms t on (t.id = c.term)
--order by s.id, t.code, sb.code
order by s.id, t.starting, sb.code
;

create or replace view stream_rulename 
as
select l.zid, r.name, r.type, r.id, aog.definition, aog.defby, r.min_req, r.max_req
from lastPgEnrol l 
join stream_enrolments st_e on (st_e.partof = l.partof)
join stream_rules st_r on (st_r.stream = st_e.stream)
join rules r on (st_r.rule = r.id)
join aog on (aog.id = r.ao_group)
order by l.zid
;

create or replace view program_rulename 
as
select l.zid, r.name, r.type, r.id, aog.definition, aog.defby, r.min_req, r.max_req
from  lastPgEnrol l 
join program_rules pg_r on l.pg_code = pg_r.program
join rules r on r.id = pg_r.rule
join (select * from aog where type = 'subject')aog on (aog.id = r.ao_group)
order by l.zid
;


create or replace view all_rulename 
as
select * from stream_rulename
union all
select * from program_rulename
order by zID;
;

-- match course with rulename which doesn't include #
create or replace view ruleWithoutHash
as
select c.zid, c.coursecode, c.term, c.starting, c.coursetitle, c.mark, c.grade,c.uoc, a.name, a.type, a.min_req, a.max_req
from completed_courses c
left join all_rulename a 
on c.zid = a.zid and a.definition ILIKE '%' || c.coursecode || '%'
order by c.zid
;

--match course with rulename which include # but not gen rule
create or replace view ruleWithHash 
as
select a.zid, a.coursecode, a.term, a.starting, a.coursetitle, a.mark, a.grade, a.uoc, b.name, b.type, b.min_req, b.max_req
from (select * from ruleWithoutHash  
where grade <> 'AF' and grade <> 'FL' and grade <> 'UF' and grade <> 'E' and grade <>'F'
AND name is null)  a
left join (select * from all_rulename where defby = 'pattern') b
on a.zid = b.zid and b.definition ilike '%' || substring(a.coursecode,1, length(a.coursecode)-3) || '%'
;



--match all the gen course with the Gen rule 
create or replace view courseWithGenRule
as
select a.zid, a.coursecode, a.term, a.starting, a.coursetitle, a.mark, a.grade, a.uoc, b.name, b.type, b.min_req, b.max_req
from (select * from ruleWithoutHash  
where grade <> 'AF' and grade <> 'FL' and grade <> 'UF' and grade <> 'E' and grade <>'F'
AND name is null
AND coursecode ilike '%' || 'GEN' || '%') a
join 
(select * from all_rulename where definition = 'GEN') b
on a.zid = b.zid
;


--match course with all rulename 
create or replace view WithAllRule (zid, coursecode,term, starting, coursetitle, mark, grade, uoc, type, rule, min, max)
as
select c.zid, c.coursecode, c.term, c.starting, c.coursetitle, c.mark, c.grade, c.uoc, concat(c.type, a.type, g.type), concat(c.name, a.name, g.name), concat(c.min_req, a.min_req, g.min_req), concat(c.max_req, a.max_req, g.max_req)
from ruleWithoutHash c
left join ruleWithHash a
on c.zid = a.zid and a.coursecode = c.coursecode and a.term = c.term
left join courseWithGenRule g
on c.zid = g.zid and g.coursecode = c.coursecode and g.term = c.term
;



--add +  to dicstint and final transcript
create or replace view transcript
as
SELECT zid, coursecode, term, coursetitle, mark, grade, uoc, type,
array_to_string(array_agg(distinct "rule" order by rule desc),' + ') AS rule
FROM WithAllRule
GROUP BY zid, coursecode, term, starting, coursetitle, mark, grade, uoc, type
order by zid, starting, coursecode
;



create or replace view all_gen_free_elec
as
select zid, name, type, min_req, max_req  from all_rulename where type != 'CC'
;