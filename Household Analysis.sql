use hces_2022_2023;
#Creating a table for Household_master.csv


CREATE TABLE household_master (
    fsu_serial_no INT,
    sector INT,
    state INT,
    nss_region INT,
    district INT,
    stratum INT,
    sub_stratum INT,
    panel INT,
    sub_sample INT,
    fod_sub_region INT,
    sample_su_no DOUBLE,
    sample_sub_division_no TEXT,
    second_stage_stratum_no INT,
    sample_hhld_no INT,
    multiplier INT,
    E2 DOUBLE,
    E3 DOUBLE,
    E1 DOUBLE,
    P2 DOUBLE,
    P3 DOUBLE,
    household_size DOUBLE,
    total_monthly_expenditure DOUBLE,
    final_weight DOUBLE,
    mpce DOUBLE,
    winsor_scale_factor DOUBLE,
    mpce_quintile INT
);


#loading the data into the household_master table

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/household_master.csv'
INTO TABLE household_master
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(fsu_serial_no, sector, state, nss_region, district, stratum, sub_stratum,
 panel, sub_sample, fod_sub_region, @sample_su_no, @sample_sub_division_no,
 second_stage_stratum_no, sample_hhld_no, multiplier, E2, E3, E1, P2, P3,
 household_size, total_monthly_expenditure, final_weight, mpce,
 winsor_scale_factor, mpce_quintile)
SET
  sample_su_no = NULLIF(@sample_su_no, ''),
  sample_sub_division_no = NULLIF(@sample_sub_division_no, '');

#creating a table for household_category_spend
CREATE TABLE household_category_spend (
    fsu_serial_no INT,
    sector INT,
    state INT,
    nss_region INT,
    district INT,
    stratum INT,
    sub_stratum INT,
    panel INT,
    sub_sample INT,
    fod_sub_region INT,
    sample_su_no DOUBLE,
    sample_sub_division_no TEXT,
    second_stage_stratum_no INT,
    sample_hhld_no INT,
    category VARCHAR(100),
    category_spend DOUBLE,
    mpce_quintile INT,
    final_weight DOUBLE,
    winsor_scale_factor DOUBLE
);

#loading the data into household_category_spend
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/household_category_spend.csv'
INTO TABLE household_category_spend
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(fsu_serial_no, sector, state, nss_region, district, stratum, sub_stratum,
 panel, sub_sample, fod_sub_region, @sample_su_no, @sample_sub_division_no,
 second_stage_stratum_no, sample_hhld_no, category, category_spend,
 mpce_quintile, final_weight, winsor_scale_factor)
SET
  sample_su_no = NULLIF(@sample_su_no, ''),
  sample_sub_division_no = NULLIF(@sample_sub_division_no, '');
  
  #checking the data in table household_category_spend
  SELECT COUNT(*) FROM household_category_spend;
 
#creating a table category_share_by_quintile
CREATE TABLE category_share_by_quintile (
    sector INT,
    mpce_quintile INT,
    `Conveyance, Services, Entertainment & Rent` DOUBLE,
    `Durable Goods` DOUBLE,
    `Education & Institutional Medical` DOUBLE,
    `Food, Beverages & Tobacco` DOUBLE,
    `Fuel & Light` DOUBLE,
    `Household Consumables & Toiletries` DOUBLE,
    `Misc. Goods, Services & Medical (Non-Hosp.)` DOUBLE,
    `Pan, Tobacco & Intoxicants` DOUBLE
);

#loading the data into category_share_by_quintile


LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/category_share_by_quintile.csv'
INTO TABLE category_share_by_quintile
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(sector, mpce_quintile,
 `Conveyance, Services, Entertainment & Rent`,
 `Durable Goods`,
 `Education & Institutional Medical`,
 `Food, Beverages & Tobacco`,
 `Fuel & Light`,
 `Household Consumables & Toiletries`,
 `Misc. Goods, Services & Medical (Non-Hosp.)`,
 `Pan, Tobacco & Intoxicants`);
 #checking for data in category_share_by_quintile
 select * from category_share_by_quintile;
 

# Analysing the data
 
#1. show only rural households (sector = 1)
SELECT fsu_serial_no, sector, mpce, mpce_quintile
FROM household_master
WHERE sector = 1
LIMIT 10;

#2. Basic aggregate functions: overall stats on MPCE
SELECT
    COUNT(*)      AS total_households,
    AVG(mpce)      AS average_mpce,
    MIN(mpce)      AS lowest_mpce,
    MAX(mpce)      AS highest_mpce
FROM household_master;

#3.GROUP BY: average MPCE for rural vs urban
SELECT
    sector,
    AVG(mpce) AS average_mpce,
    COUNT(*)  AS number_of_households
FROM household_master
GROUP BY sector;

#4.GROUP BY with ORDER BY: total spend per category, highest first
SELECT
    category,
    SUM(category_spend) AS total_spend,
    AVG(category_spend) AS average_spend_per_household
FROM household_category_spend
GROUP BY category
ORDER BY total_spend DESC;

#5.find the 10 households with the highest MPCE
SELECT
    fsu_serial_no, sector, mpce
FROM household_master
ORDER BY mpce DESC
LIMIT 10;

#6.GROUP BY two columns: average MPCE by sector AND quintile together
SELECT
    sector,
    mpce_quintile,
    AVG(mpce) AS average_mpce
FROM household_master
GROUP BY sector, mpce_quintile
ORDER BY sector, mpce_quintile;
 
 #7.Simple JOIN: combine household info with their category spending
# (joining on the 3 columns that together identify a household)
SELECT
    hm.sector,
    hm.mpce,
    hcs.category,
    hcs.category_spend
FROM household_master hm
JOIN household_category_spend hcs
    ON hm.fsu_serial_no = hcs.fsu_serial_no
    AND hm.second_stage_stratum_no = hcs.second_stage_stratum_no
    AND hm.sample_hhld_no = hcs.sample_hhld_no
LIMIT 10;

#8.Households that spend above the national average MPCE
SELECT
    fsu_serial_no, sector, mpce
FROM household_master
WHERE mpce > (SELECT AVG(mpce) FROM household_master)
LIMIT 10;
 
 
#9.Ranking States by average mpce
SELECT
    state,
    AVG(mpce) AS average_mpce,
    RANK() OVER (ORDER BY AVG(mpce) DESC) AS mpce_rank
FROM household_master
GROUP BY state
ORDER BY mpce_rank;
 
 #10.Compare category spend share: poorest (Q1) vs richest (Q5) rural households
SELECT
    mpce_quintile,
    `Food, Beverages & Tobacco`      AS food_share,
    `Durable Goods`                  AS durable_goods_share,
    `Education & Institutional Medical` AS education_medical_share,
    `Fuel & Light`                   AS fuel_light_share
FROM category_share_by_quintile
WHERE sector = 1
  AND mpce_quintile IN (1, 5)
ORDER BY mpce_quintile;


#11.-- Compare category spend share: poorest (Q1) vs richest (Q5) urban households
SELECT
    mpce_quintile,
    `Food, Beverages & Tobacco`         AS food_share,
    `Durable Goods`                     AS durable_goods_share,
    `Education & Institutional Medical` AS education_medical_share,
    `Fuel & Light`                      AS fuel_light_share
FROM category_share_by_quintile
WHERE sector = 2
  AND mpce_quintile IN (1, 5)
ORDER BY mpce_quintile;
 