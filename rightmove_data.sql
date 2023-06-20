SELECT * FROM properties
LIMIT 10;

-- Average rent of a property in London.
SELECT AVG(Price) AS AveragePrice
FROM properties;

-- Highest rent per month.
SELECT *
FROM properties
WHERE Price = (SELECT MAX(Price) FROM properties);

-- Lowest rent per month. (property doesn't match the link, and the value is semi unrealisitic compared to the other lowest values)
SELECT *
FROM properties
WHERE Price = (SELECT MIN(Price) FROM properties);

-- Properties with the lowest rent per month.
SELECT *
FROM properties
ORDER BY Price ASC;

-- Deleting it from the table.
DELETE FROM properties
WHERE Price = 95;

-- Most bedrooms (this has returned incorrect data, not because of the scraping, but because it has been input incorrectly on the website).
SELECT *
FROM properties
WHERE Bedrooms = (SELECT MAX(Bedrooms) FROM properties);

-- We check to see if there are more unrealistic values...
SELECT *
FROM properties
ORDER BY Bedrooms DESC;

-- We remove it from the table.
DELETE FROM properties
WHERE Bedrooms = 1800;

-- Running the orginal query again.
SELECT *
FROM properties
WHERE Bedrooms = (SELECT MAX(Bedrooms) FROM properties);

-- Number of properties by property type.
SELECT Type, COUNT(*) AS PropertyCount
FROM properties
GROUP BY Type;

-- Average rent by property type.
SELECT Type, AVG(Price) AS AverageRent
FROM properties
GROUP BY Type;

-- Show properties located in a specific area.
SELECT *
FROM properties
WHERE Location LIKE '%Westminster%';

-- The average rent per bedroom.
SELECT Bedrooms, ROUND(AVG(Price), 2) AS AverageRentPerBedroom
FROM properties
GROUP BY Bedrooms
ORDER BY Bedrooms ASC;



