-- Keep a log of any SQL queries you execute as you solve the mystery.
SELECT description
FROM crime_scene_reports
WHERE year = 2021 AND month = 7 AND day = 28 AND street = 'Humphrey Street';

SELECT name, transcript
FROM interviews
WHERE year = 2021 AND month = 7 AND day = 28 AND transcript LIKE '%bakery%';

SELECT f.id, a.city, f.hour, f.minute
FROM flights f
JOIN airports a ON f.destination_airport_id = a.id
WHERE f.origin_airport_id = (SELECT id FROM airports WHERE city = 'Fiftyville')
  AND f.year = 2021 AND f.month = 7 AND f.day = 29
ORDER BY f.hour, f.minute
LIMIT 1;

SELECT name FROM people
WHERE license_plate IN (
    -- 1. Left bakery parking lot between 10:15 and 10:25 AM
    SELECT license_plate FROM bakery_security_logs
    WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25 AND activity = 'exit'
)
AND id IN (
    -- 2. Withdrew money from the Leggett Street ATM
    SELECT person_id FROM bank_accounts
    JOIN atm_transactions ON bank_accounts.account_number = atm_transactions.account_number
    WHERE year = 2021 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw'
)
AND phone_number IN (
    -- 3. Made a phone call lasting less than a minute
    SELECT caller FROM phone_calls
    WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60
)
AND passport_number IN (
    -- 4. Was on the earliest flight out next morning
    SELECT passport_number FROM passengers
    WHERE flight_id = 36
);

SELECT name FROM people
WHERE phone_number = (
    SELECT receiver FROM phone_calls
    WHERE year = 2021 AND month = 7 AND day = 28 AND duration < 60
      AND caller = (SELECT phone_number FROM people WHERE name = 'Bruce')
);
