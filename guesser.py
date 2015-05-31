# -*- coding: utf-8 -*-
"""
This guesses the gender breakdown among authors in the Harvard Library
Bibliographic Dataset: http://openmetadata.lib.harvard.edu/bibdata ,
which is provided by the Harvard Library under its Bibliographic Dataset Use
Terms and includes data made available by, among others, OCLC Online Computer
Library Center, Inc. and the Library of Congress.

Thank you to Harvard and OCLC for the data!

This method has some clear problems, including:
* The gender guesser library supports only US, UK, Argentine, and Uruguayan
  names, and we are assuming all authors are American (this is certainly
  incorrect).
* Names are not necessarily clearly gendered, and even names which strongly
  correlate with one gender may be used by people of another.
* People's gender may not match others' beliefs about it.
* People's gender may not fit within a male/female binary.
* This script arose out of a question about author gender in library
  collections generally; Harvard is certainly not representative.
* Some fields conventionally use initials rather than first names, and
  therefore cannot be gender-guessed; this almost certainly skews the
  result nonrandomly.
* Some works have more authors than the MARC format can readily accommodate.
* I'm not bothering to examine the 700 field anyway, pending decisions about
  how to count works with multiple authors.
* Not all cultures have a "Last, First" naming pattern.
* I haven't bothered to invest time cleaning up incorrect codings in the
  MARC fields under consideration (and cataloging standards are clearly
  inconsistent).
* A large fraction of works are produced by corporate and/or missing authors.

"""
import argparse
import glob
import os
import psycopg2

from pymarc import MARCReader
from gender_detector import GenderDetector

def find_forename(field_string):
    names = field_string.split(',')

    # Sometimes 100a contains the full name; sometimes it just
    # has a last name. We're not going to bother looking for the first
    # name elsewhere. We're going to look for names of the form
    # "Lastname, First Middle Whatever" and ignore others. Sorry,
    # dataset.
    if len(names) > 1:
        forenames = names[1].strip()
        # If there are multiple forenames (e.g. first and middle),
        # split them apart; we'll only deal with the first.
        if ' ' in forenames:
            forename = forenames.split(' ')[0]
        else:
            forename = forenames

        forename = forename.replace('.', '')
    else:
        forename = None

    return forename

def get_data(record, name_field):
    try:
        forename = find_forename(name_field)
    except:
        forename = None

    if forename:
        gender = detector.guess(forename)
    else:
        gender = None

    try:
        pub_date = record['260']['c']
        pub_date = pub_date.replace(
            '[', '').replace(
            ']', '').replace(
            '?', '').replace(
            'c', '').replace(
            '.', '')
        pub_date = int(pub_date)
    except:
        pub_date = None

    return forename, pub_date, gender

# Set up command-line argument to grab filename.
parser = argparse.ArgumentParser()
parser.add_argument('filename',
    help='path/from/script/to/filename (wildcards ok)')
args = parser.parse_args()
filename = args.filename

# Set up detector.
detector = GenderDetector('us')

# Set up database. Important: postgresql creates databases with utf-8 encoding
# by default - that's good, because we're going to need it for the
# international author names we're about to harvest.
conn = psycopg2.connect("dbname=joanharvard user=joanharvard")
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS test")
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, year integer, name varchar, gender varchar);")

# Find files.
current_dir = os.path.dirname(os.path.realpath(__file__))
files = glob.glob(os.path.join(current_dir, filename))

total_records = 0
processed_records = 0
# Process files.
for f in files:
    with open(f, 'r') as records:
        reader = MARCReader(records, utf8_handling='replace')
        for record in reader:
            try:
                str100a = record['100']['a']
                name, year, gender = get_data(record, str100a)
                cur.execute("INSERT INTO test (year, name, gender) VALUES (%s, %s, %s)",
                    (year, name, gender))
                processed_records += 1
            except:
                pass

            total_records += 1

# Count the number of guessably male or female names.
cur.execute("SELECT * FROM test WHERE gender='female';")
num_female = cur.rowcount

cur.execute("SELECT * FROM test WHERE gender='male';")
num_male = cur.rowcount

# This prints information about the % of WORKS with male/female authors,
# not the % of AUTHORS - no attempt made to count distinct authors.
# As this is python 2, you need to coerce the ints to floats, or when you
# do the division you'll end up with an int value you didn't expect.
print "Percent of collection whose primary author names are...\n" \
      "-------------------------------------------------------"
print "   ...female: %s" % round(float(num_female*100)/total_records, 1)
print "   ...male: %s\n" % round(float(num_male*100)/total_records, 1)
try:
    print "There are %s times as many male names as female names.\n" \
        % round(float(num_male)/num_female, 1)
except ZeroDivisionError:
    print "Whoops, no women, hence no ratio"

# Persist the db changes.
conn.commit()

# Clean up.
cur.close()
conn.close()

# Open/access the records
# Initialize database
# Loop through the records. For each:
# Get authors' names (all of them)
# For name in names:
# Add to db
# detector.guess('Marcos') # => 'male'
# Add gender to db
# Add year of publication to db
# don't bother to disambiguate at this stage because we want to support date range queries
# Run db queries: overall percents (count distinct), plus binned percents by year range

# Run this first on a smaller sample, just in case
