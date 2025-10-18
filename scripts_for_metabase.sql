-- Актуальное время
SELECT CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Moscow'::text AS moscow_time;

-- Тренд по показам карточек
select 
	DATE_TRUNC('hour', created_at) as "Час",
	COUNT(*) as "Кол-во товаров"
from positions
group by DATE_TRUNC('hour', created_at)
order by DATE_TRUNC('hour', created_at);

-- Тренд по доле присутствия
with city_cnt as (
	select count(distinct city) as var_1
	from positions
),
query_cnt as (
	select count(distinct query) as var_2
	from positions
)
select 
	DATE_TRUNC('hour', created_at) as "Час",
	COUNT(*)::numeric / (MIN(var_1) * MIN(var_2) * 200) as "Доля присутствия" -- 200 карточек товаров на 2 страницах выдачи
from positions, city_cnt, query_cnt
group by DATE_TRUNC('hour', created_at)
order by DATE_TRUNC('hour', created_at);

-- Тренд по средней цене
select 
	DATE_TRUNC('hour', created_at) as "Час",
	avg(price)::int as "Средняя цена"
from positions
group by DATE_TRUNC('hour', created_at)
order by DATE_TRUNC('hour', created_at);

-- Динамика показов и средней цены
select 
	to_char(created_at, 'DD-MM-YYYY') as "День",
	count(*) as "Кол-во показов",
	avg(price) as "Ср. цена товара"
from positions
where true
and {{created_at}}
and {{city}}
group by to_char(created_at, 'DD-MM-YYYY')
order by to_char(created_at, 'DD-MM-YYYY');

-- Доля брендов в показах
select 
	brand as "Бренд",
	count(*) as "Кол-во показов"
from positions
where true
and {{created_at}}
and {{city}}
group by brand;

-- Средняя позиция бренда
select 
	avg(position)::int
from positions
where true
and {{created_at}}
and {{city}}
and brand = 'Feliamo'; --'JOYCITY'

-- Средняя цена бренда
select 
	avg(price)::int
from positions
where true
and {{created_at}}
and {{city}}
and brand = 'Feliamo'; --'JOYCITY'

-- Сводная таблица (средняя позиция товара по запросам)
with t as(
	select 
		brand || ' ' ||name as "Товар",
		query as "Запрос",
		position as "Позиция",
		date(created_at) as "День"
	from positions
	where true
	and {{created_at}}
	and {{city}}
),
t1 as (
	SELECT
		"Товар", "Запрос",
		avg("Позиция") over(partition by "Товар", "Запрос" order by "День") as "Средняя позиция"
 	FROM t
)
select 
	"Товар", 
	"Запрос",
	avg("Средняя позиция")::int as "Средняя позиция"
from t1
group by 1,2