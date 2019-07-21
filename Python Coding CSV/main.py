"""
Module to read data from CSV files and HTML file
to populate an SQL database

"""



import csv
import sqlite3
from bs4 import BeautifulSoup
from database import DATABASE_NAME

# define your functions to read data here
def read_csv(csv_file):

    with open(csv_file, 'r', encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Creating a list with dictionary of each row
        csv_data = [row for row in reader]

    return csv_data

# Builds query for each tb
def query_builder(table, column_names):

    ## Creating a query to insert values
    ##
    ##
    query = "insert into %s(" % table

    for column in column_names:
        if column == column_names[-1]:
            query += column + ') values ('

        else:
            query += column + ', '

    for column in column_names:
        if ((table == "companies" or table == "positions") and column == "id"):
            query += "NULL, "

        elif column == column_names[-1]:
            query += '"{' + column + '}");'

        else:
            query += '"{' + column + '}", '
    #
    #
    # Query building complete only formatting remains

    return query

# Inserts data into the three tables
def insert_data(table, query, csv_data = None, lsOne=None, lsTwo=None):

    for i in range(len(csv_data)):

        if table == "companies":
            # This is the value which will be used to search for id to connect one db to another db
            # (in this case people with companies)
            foreign_key_slot = ' '.join(csv_data[i]['contact'].split(', ')).split()

            cur.execute("select id from people where first_name = '"
                        + foreign_key_slot[1] + "' and last_name= '"
                        + foreign_key_slot[0] + "'")

            # Tuple consists of one id from people table
            person_id = cur.fetchone()[0]

            query_cmd = query.format(name=csv_data[i]['company'],
                                     url=csv_data[i]['url'],
                                     contact=person_id)

            cur.execute(query_cmd)
            db.commit()

            cur.execute("select id from companies where contact = '%d'" % person_id)

            print(cur.fetchone()[0])

            if cur.fetchone()[0] != None:
                # Creating a dictionary of location as key and id from companies table
                location[csv_data[i]['location']] = cur.fetchone()[0]

                # Creating a dictionary of company name as key and id from companies table
                company_id[csv_data[i]['company']] = cur.fetchone()[0]

        if table == 'people':
            query_cmd = query.format(id=csv_data[i]['person_ID'],
                                     first_name=csv_data[i]['first'],
                                     middle_name=csv_data[i]['middle'],
                                     last_name=csv_data[i]['last'],
                                     email=csv_data[i]['email'],
                                     phone=csv_data[i]['phone'])

            cur.execute(query_cmd)
            db.commit()

    if table == 'positions':
        for i in range(len(lsOne)):

            query_cmd = query.format(title=lsOne[i],
                                     location=location[lsTwo[i]],
                                     company=company_id[lsTwo[i]])

            cur.execute(query_cmd)
            db.commit()

# Function to get data from index.html
def fetch_from_html():

    index_soup = BeautifulSoup(open("index.html"), "html.parser")
    jobs_div = index_soup.find_all('div', attrs={"class":"card-header"})

    # Get positions from index.html
    positions=[j.find('h5',attrs={'class':'card-title'}).text  for j in jobs_div]

    # Get orgranisations with those positions from index.html
    organisations=[j.find('div', attrs={"class":"company"}).text for j in jobs_div]

    return positions, organisations

def generate_csv():

    writer_dict = {}

    with open('output.csv', 'w') as file:
        field_names = ['Company Name', 'Job Title', 'Location', 'First Name', 'Last Name', 'email']
        writer = csv.DictWriter(file, fieldnames=field_names)

        cur.execute("Select * from positions")
        positions = cur.fetchall()

        cur.execute("Select * from people")
        people = cur.fetchall()

        cur.execute("Select * from companies")
        companies = cur.fetchall()


        for i in range(len(positions)):
            # Use these variables for optimisation or leave it
            contact = positions[i][3] - 1
            company = companies[contact][3] - 1

            writer_dict['Company Name'] = companies[contact][1]
            writer_dict['Job Title'] = positions[i][1]
            writer_dict['Location'] = positions[i][2]
            writer_dict['First Name'] = people[company][1]
            writer_dict['Last Name'] = people[company][3]
            writer_dict['email'] = people[company][4]

        print(positions)

if __name__=='__main__':
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()

    tables = ['people', 'companies', 'positions']

    # Go inside insert_data(..."companies.csv"...) to learn about this var
    company_id = {}
    location = {}

    # p is positions, o is organisations
    p, o = fetch_from_html()

    for table in tables:
        # Gets column name from table in db
        cur.execute('select * from %s' % table)
        column_names = [tables[0] for tables in cur.description]

        # There is no positions.csv
        if table != "positions":
            csv_data = read_csv(table + ".csv")

        query = query_builder(table, column_names)
        # print(column_names)
        # print(csv_data)
        # print(query)
        # try:
        insert_data(table, query, csv_data, p, o)
        # except Exception:
        #     print()
        #     db.close()
        #     break
    generate_csv()
    db.close()
    # Add your 'main' code here to call your functions
