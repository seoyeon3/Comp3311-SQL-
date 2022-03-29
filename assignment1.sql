-- COMP3311 21T3 Assignment 1

-- Q1: oldest brewery

create or replace view Q1(brewery)
as
select name from breweries where founded = (select min(founded) from breweries)
;

-- Q2: collaboration beers

create or replace view Q2extra(id, beer)
as
select by.beer, b.name from brewed_by by join beers b on (by.beer=b.id)
;

create or replace view Q2(beer)
as
select beer from Q2extra group by id,beer having count(id)>1 order by beer
;

-- Q3: worst beer

create or replace view Q3(worst)
as
select name from beers where rating = (select min(rating) from beers)
;

-- Q4: too strong beer

create or replace view Q4(beer,abv,style,max_abv)
as
select b.name, b.abv,s.name,s.max_abv from beers b join styles s on (b.style = s.id) where b.abv > s.max_abv
;

-- Q5: most common style

--create a view with style id ,style name, style counts
create or replace view Q5extra(style_id,style,counts) 
as 
select be.style, st.name, count(be.style) from beers be join styles st on (be.style = st.id) 
group by be.style, st.name
;

create or replace view Q5(style)
as
select style from Q5extra where counts = (select max(counts) from Q5extra);
;

-- Q6: duplicated style names

--create a view with style name and lower style name
create or replace view Q6extra(name,l_name)
as
select name, lower(name) from styles
;

create or replace view Q6(style1,style2)
as
select s1.name, s2.name
from Q6extra s1 join Q6extra s2 on s1.l_name=s2.l_name
where s1.name<s2.name
;

-- Q7: breweries that make no beers

create or replace view Q7(brewery)
as
select b.name
from breweries b left outer join brewed_by r on (b.id=r.brewery) where r.brewery is null
;

-- Q8: city with the most breweries

--create a view with metro, country, and metro counts 
create or replace view Q8extra(metro,country,m_count)
as
select metro, country, count(metro) from locations group by metro, country
;

create or replace view Q8(city,country)
as
select metro, country from Q8extra where m_count = (select(max(m_count)) from Q8extra)
;

-- Q9: breweries that make more than 5 styles

--create a view with brewery id, brewery name and style id
create or replace view Q9extra(br_id, br_name,sty_id)
as
select by.brewery, br.name, be.style from beers be join brewed_by by on(be.id=by.beer)
join breweries br on(by.brewery=br.id)
;

create or replace view Q9(brewery,nstyles)
as
select br_name, count(distinct(sty_id)) from Q9extra group by br_name having(count(distinct sty_id)) > 5 order by br_name;
;

-- Q10: beers of a certain style

--create a view with beer ID, beer name, brewery name,style name, year, abv 
create or replace view Q10extra (beer_id, beer, brewery, style, year, abv)
as
select be.id, be.name, br.name, sty.name, be.brewed, be.abv
from beers be join styles sty on (be.style=sty.id)
join brewed_by by on (be.id=by.beer)
join breweries  br on (by.brewery=br.id)
order by style, beer
;

--concatenate breweries for the collaboration beer with beer name,brewery name, style name, year and abv columns
create or replace view BeerInfo (beer, brewery, style, year, abv) 
as
select beer, array_to_string(array_agg(brewery order by brewery),  ' + ' ) as brewery,  style, year, abv from Q10extra
group by beer_id , beer ,style, year, abv
;

create or replace function
	q10(_style text) returns setof BeerInfo 
as $$
 declare 
	tuple record;	info BeerInfo;
begin
	for tuple in
		select * from BeerInfo where style=$1
	loop
		info.beer := tuple.beer;
		info.brewery := tuple.brewery;
		info.style := tuple.style;
		info.year := tuple.year;
		info.abv := tuple.abv;
		return next info;
	end loop;
end;
$$ language PLpgSQL;


--Q11: beers with names matching a pattern

create or replace function
        Q11(partial_name text) returns setof text
as $$
declare
    r record; t text;
begin
	for r in
		select * from beerinfo where lower(beer) ~ lower($1) 
        loop
			t:= concat('"',r.beer,'"',', ',r.brewery, ', ', r.style, ', ', r.abv, '% ABV');
			return next t;
        end loop;
end;
$$language plpgsql;

--Q12: breweries and the beers they make

--create a view with brewery name, founded, country, region, metro, town, beer name, style name, year, abv
create or replace view Q12extra (brewery,founded,country,region,metro,town,beer,style,br_year,abv)
as
select br.name, br.founded,lc.country, lc.region, lc.metro, lc.town,be.name,st.name,be.brewed,be.abv
from breweries br join locations lc on(br.located_in = lc.id)
left outer join brewed_by by on (br.id=by.brewery)
left outer join beers be on (by.beer = be.id)
left outer join styles st on (be.style=st.id)
order by br.name,be.brewed,be.name
;

create or replace function 
	Q12(partial_name text) returns setof text
as $$
declare r record; t text;
p text := ''; 
lc_inf text; 
begin
	for r in
		select * from Q12extra where lower(brewery) ~ lower($1)
	loop
		if (p<>r.brewery) then
			lc_inf := r.region || ', ' || r.country;
			t := r.brewery || ', founded ' || r.founded; 
			return next t;
            		
			if ((r.town = '') is false and (r.metro = '') is false) then 
				if ((r.region = '' ) is false) then
					t := 'located in ' || r.town || ', ' || lc_inf;
				end if;
				if ((r.region = '' ) is not false) then
					t := 'located in ' || r.town || ', ' || r.country;
				end if;                        
			end if;
			
			if ((r.town = '') is false and (r.metro = '') is not false) then 
				if ((r.region = '' ) is false) then
					t := 'located in ' || r.town || ', ' || lc_inf;
				end if;
				if ((r.region = '' ) is not false) then
					t := 'located in ' || r.town || ', ' || r.country;
				end if;
			end if;
					
			if ((r.town = '') is  not false and (r.metro = '') is false) then 
				if ((r.region = '' ) is false) then
					t := 'located in ' || r.metro|| ', ' || lc_inf;	
				end if;
				if ((r.region = '' ) is not false) then
					t := 'located in ' || r.metro|| ', ' || r.country;
				end if;    
			end if;    
            return next t;
		end if;
		p := r.brewery;
		if ((r.beer = '') is false) then                   
			t := E'  "' || r.beer || '", ' || r.style || ', ' || r.br_year || ', ' || r.abv || '% ABV';
		end if;
        
		if ((r.beer = '') is not false) then   
			t := ' No known beers';
        end if;
		return next t;
	end loop;
end;
$$ language plpgsql;

