-- 13. Names of all people who starred in a movie in which Kevin Bacon also starred
SELECT p.name FROM people p JOIN stars s ON p.id = s.person_id WHERE s.movie_id IN (SELECT s2.movie_id FROM stars s2 JOIN people p2 ON s2.person_id = p2.id WHERE p2.name = 'Kevin Bacon' AND p2.birth = 1958) AND p.id NOT IN (SELECT id FROM people WHERE name = 'Kevin Bacon' AND birth = 1958);
