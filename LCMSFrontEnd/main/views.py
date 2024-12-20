from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.db import connection
from .forms import SQLInputForm
import traceback
from django.utils.html import format_html

from .db_module import DBModule

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']
    template_name = 'main/logout.html'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)

def home(request):
    return render(request, 'main/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def contact(request):
    return render(request, 'main/contact.html')

pop_tables_queries = [
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (1, 'Open')",
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (2, 'Closed')",
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (3, 'In Progress')",
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (4, 'Resolved')",
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (5, 'Pending')",
        "INSERT INTO CaseFile (Case_ID, Status) VALUES (6, 'High Priority')",

        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (1, 'Alice Cooper', 'LLB', '5 years', 1)", 
        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (2, 'Bob Marley', 'JD', '8 years', 2)", 
        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (3, 'Charlie Brown', 'LLM', '3 years', 3)", 
        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (4, 'Diana Ross', 'LLB', '10 years', 4)", 
        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (5, 'Eve Adams', 'JD', '2 years', 5)",
        "INSERT INTO Lawyer (Lawyer_ID, Name, Education, Experience, Case_ID) VALUES (6, 'John Doe', 'LLB', '5 years', 6)",

        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (1, 'High', 1)",
        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (2, 'Medium', 2)",
        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (3, 'Low', 3)",
        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (4, 'High', 4)",
        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (5, 'High', 5)",
        "INSERT INTO Records (Record_ID, Relevance, Case_ID) VALUES (6, 'Low', 6)",

        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (1, 'Legal Brief', TO_DATE('2023-01-20', 'YYYY-MM-DD'), 'Brief on Case 1', 1)",
        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (2, 'Court Order', TO_DATE('2023-02-15', 'YYYY-MM-DD'), 'Order for Case 2', 2)",
        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (3, 'Evidence', TO_DATE('2023-03-10', 'YYYY-MM-DD'), 'Evidence for Case 3', 3)",
        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (4, 'Motion', TO_DATE('2023-04-05', 'YYYY-MM-DD'), 'Motion for Case 4', 4)",
        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (5, 'Witness Statement', TO_DATE('2023-05-01', 'YYYY-MM-DD'), 'Statement for Case 5', 5)",
        "INSERT INTO CaseDocument (Document_ID, Type, Document_Date, Content, Record_ID) VALUES (6, 'Research', TO_DATE('2023-06-15', 'YYYY-MM-DD'), 'Research for Case 6', 6)",

        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (1, 'Historical data for Case 1')",
        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (2, 'Historical data for Case 2')",
        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (3, 'Historical data for Case 3')",
        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (4, 'Historical data for Case 4')",
        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (5, 'Historical data for Case 5')",
        "INSERT INTO HistoricalLegalRecords (Record_ID, Content) VALUES (6, 'Historical data for Case 6')",

        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (1, TO_DATE('1975-06-20', 'YYYY-MM-DD'), 'Doctor', 'Provided medical testimony', 1)",
        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (2, TO_DATE('1980-09-15', 'YYYY-MM-DD'), 'Witness', 'Saw the incident', 2)",
        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (3, TO_DATE('1990-12-01', 'YYYY-MM-DD'), 'Police Officer', 'Filed the report', 3)",
        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (4, TO_DATE('1985-11-30', 'YYYY-MM-DD'), 'Doctor', 'Evaluated injuries', 4)",
        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (5, TO_DATE('1972-04-10', 'YYYY-MM-DD'), 'Psychologist', 'Provided mental health evaluation', 5)",
        "INSERT INTO ExternalPersons (Person_ID, Date_Of_Birth, Profession, Statements, Record_ID) VALUES (6, TO_DATE('1988-03-22', 'YYYY-MM-DD'), 'Doctor', 'Provided second opinion', 6)",

        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (1, 'Fraud', 'No prior offenses', 'John Doe', 1)",
        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (2, 'Theft', 'Two prior offenses', 'Jane Smith', 2)",
        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (3, 'Assault', 'No prior offenses', 'Emily Johnson', 3)",
        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (4, 'Embezzlement', 'One prior offense', 'Michael Brown', 4)",
        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (5, 'Vandalism', 'Multiple offenses', 'Sarah Williams', 5)",
        "INSERT INTO ClientLegalProfile (ClientLegalID, Charges, CriminalHistory, Name, Record_ID) VALUES (6, 'Forgery', 'No prior offenses', 'Chris Green', 6)",

        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (101, 'Legal fees for case 1', 25, '1500', 1)",
        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (102, 'Consultation fees for case 2', 15, '750', 2)",
        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (103, 'Case documentation fees for case 3', 30, '2000', 3)",
        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (104, 'Court representation fees for case 4', 45, '3000', 4)",
        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (105, 'Research fees for case 5', 10, '500', 5)",
        "INSERT INTO Invoice (Invoice_ID, Content, Billable_Hours, Expenses, Case_ID) VALUES (106, 'Settlement negotiation fees for case 6', 20, '1200', 6)",

        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (1, 'John Doe', 'Asthma', '789 Pine St, Vancouver, BC, Canada, V5K 0A1', 'Doe', TO_DATE('1985-04-12', 'YYYY-MM-DD'), 101)",
        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (2, 'Jane Smith', 'Diabetes', '456 Oak St, Toronto, ON, Canada, M5H 2N2', 'Smith', TO_DATE('1990-07-21', 'YYYY-MM-DD'), 102)",
        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (3, 'Emily Johnson', 'Mental Health Issues', '123 Maple St, Ottawa, ON, Canada, K1A 0B1', 'Johnson', TO_DATE('1978-11-05', 'YYYY-MM-DD'), 103)",
        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (4, 'Michael Brown', 'None', '101 Elm St, Toronto, ON, Canada, M5H 3C2', 'Brown', TO_DATE('2000-02-18', 'YYYY-MM-DD'), 104)",
        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (5, 'Sarah Williams', 'Hypertension', '202 Cedar St, Ottawa, ON, Canada, K1A 0B1', 'Williams', TO_DATE('1995-09-30', 'YYYY-MM-DD'), 105)",
        "INSERT INTO ClientPersonalProfile (Client_ID, Name, MedicalHistory, Address, Family, DOB, Invoice_ID) VALUES (6, 'Chris Green', 'Allergies', '789 Pine St, Vancouver, BC, Canada, V5K 0A1', 'Green', TO_DATE('1992-06-15', 'YYYY-MM-DD'), 106)",

        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (1, TO_DATE('2023-01-15', 'YYYY-MM-DD'), 101)",
        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (2, TO_DATE('2023-05-20', 'YYYY-MM-DD'), 102)",
        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (3, TO_DATE('2023-08-10', 'YYYY-MM-DD'), 103)",
        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (4, TO_DATE('2024-02-25', 'YYYY-MM-DD'), 104)",
        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (5, TO_DATE('2024-03-30', 'YYYY-MM-DD'), 105)",
        "INSERT INTO ImportantDates (Date_ID, Date_Entry, Invoice_ID) VALUES (6, TO_DATE('2024-04-15', 'YYYY-MM-DD'), 106)",

        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (1, 'Court Hearing', 'Downtown Court, 123 Main St, Toronto, ON, Canada, M5H 1X6', TO_DATE('2023-01-20', 'YYYY-MM-DD'), 1)",
        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (2, 'Client Meeting', 'Law Office, 456 King St, Vancouver, BC, Canada, V5K 3N5', TO_DATE('2023-05-25', 'YYYY-MM-DD'), 2)",
        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (3, 'Document Review', 'Library, 789 Pine St, Ottawa, ON, Canada, K1A 0B1', TO_DATE('2023-08-15', 'YYYY-MM-DD'), 3)",
        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (4, 'Negotiation', 'Mediation Center, 101 Elm St, Toronto, ON, Canada, M5H 3C2', TO_DATE('2024-02-28', 'YYYY-MM-DD'), 4)",
        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (5, 'Case Preparation', 'Law Office, 202 Cedar St, Ottawa, ON, Canada, K1A 0B1', TO_DATE('2024-03-31', 'YYYY-MM-DD'), 5)",
        "INSERT INTO Task (Task_ID, Type, Location, Task_Date, Date_ID) VALUES (6, 'Witness Interview', 'Downtown Court, 123 Main St, Toronto, ON, Canada, M5H 1X6', TO_DATE('2024-04-20', 'YYYY-MM-DD'), 6)",
    ]

drop_tables_queries = [
        "DROP TABLE CaseFile CASCADE CONSTRAINTS",
        "DROP TABLE Lawyer CASCADE CONSTRAINTS",
        "DROP TABLE Records CASCADE CONSTRAINTS",
        "DROP TABLE CaseDocument CASCADE CONSTRAINTS",
        "DROP TABLE HistoricalLegalRecords CASCADE CONSTRAINTS",
        "DROP TABLE ExternalPersons CASCADE CONSTRAINTS",
        "DROP TABLE ClientLegalProfile CASCADE CONSTRAINTS",
        "DROP TABLE Invoice CASCADE CONSTRAINTS",
        "DROP TABLE ClientPersonalProfile CASCADE CONSTRAINTS",
        "DROP TABLE ImportantDates CASCADE CONSTRAINTS",
        "DROP TABLE Task CASCADE CONSTRAINTS",
    ]

create_tables_queries = [
         """
        CREATE TABLE CaseFile (
            Case_ID NUMBER PRIMARY KEY, 
            Status VARCHAR2(255) NOT NULL
        )
        """,
        """
        CREATE TABLE Lawyer (
            Lawyer_ID NUMBER PRIMARY KEY,  
            Name VARCHAR2(255) NOT NULL, 
            Education VARCHAR2(255) NOT NULL, 
            Experience VARCHAR2(255) NOT NULL,
            Case_ID NUMBER NOT NULL,
            FOREIGN KEY (Case_ID) REFERENCES CaseFile(Case_ID)
        )
        """,
        """
        CREATE TABLE Records (
            Record_ID NUMBER PRIMARY KEY, 
            Relevance VARCHAR2(255) NOT NULL,
            Case_ID NUMBER NOT NULL,
            FOREIGN KEY (Case_ID) REFERENCES CaseFile(Case_ID)
        )
        """,
        """
        CREATE TABLE CaseDocument (
            Document_ID NUMBER PRIMARY KEY,
            Type VARCHAR2(255) NOT NULL,
            Document_Date DATE NOT NULL,
            Content VARCHAR2(255) NOT NULL,
            Record_ID NUMBER NOT NULL,
            FOREIGN KEY (Record_ID) REFERENCES Records(Record_ID)
        )
        """,
        """
        CREATE TABLE HistoricalLegalRecords (
            Record_ID NUMBER PRIMARY KEY,
            Content VARCHAR2(255) NOT NULL,
            FOREIGN KEY (Record_ID) REFERENCES Records(Record_ID)
        )
        """,
        """
        CREATE TABLE ExternalPersons (
            Person_ID NUMBER PRIMARY KEY,
            Date_Of_Birth DATE NOT NULL,
            Profession VARCHAR2(255) NOT NULL,
            Statements VARCHAR2(255) NOT NULL,
            Record_ID NUMBER NOT NULL,
            FOREIGN KEY (Record_ID) REFERENCES Records(Record_ID)
        )
        """,
        """
        CREATE TABLE ClientLegalProfile (
            ClientLegalID NUMBER PRIMARY KEY,
            Charges VARCHAR2(255) NOT NULL,
            CriminalHistory VARCHAR2(255) NOT NULL,
            Name VARCHAR2(255) NOT NULL,
            Record_ID NUMBER NOT NULL,
            FOREIGN KEY (Record_ID) REFERENCES Records(Record_ID)
        )
        """,
        """
        CREATE TABLE Invoice (
            Invoice_ID NUMBER PRIMARY KEY,
            Content VARCHAR2(255) NOT NULL,
            Billable_Hours NUMBER NOT NULL,
            Expenses VARCHAR2(255) NOT NULL,
            Case_ID NUMBER NOT NULL,
            FOREIGN KEY (Case_ID) REFERENCES CaseFile(Case_ID)
        )
        """,
        """
        CREATE TABLE ClientPersonalProfile (
            Client_ID NUMBER PRIMARY KEY,
            Name VARCHAR2(255) NOT NULL,
            MedicalHistory VARCHAR2(255) NOT NULL,
            Address VARCHAR2(255) NOT NULL,
            Family VARCHAR2(255) NOT NULL,
            DOB DATE NOT NULL,
            Invoice_ID NUMBER NOT NULL,
            FOREIGN KEY (Invoice_ID) REFERENCES Invoice(Invoice_ID)
        )
        """,
        """
        CREATE TABLE ImportantDates (
            Date_ID NUMBER PRIMARY KEY,
            Date_Entry DATE NOT NULL,
            Invoice_ID NUMBER NOT NULL,
            FOREIGN KEY (Invoice_ID) REFERENCES Invoice(Invoice_ID)
        )
        """,
        """
        CREATE TABLE Task (
            Task_ID NUMBER PRIMARY KEY,
            Type VARCHAR2(255) NOT NULL,
            Location VARCHAR2(255) NOT NULL,
            Task_Date DATE NOT NULL,
            Date_ID NUMBER NOT NULL,
            FOREIGN KEY (Date_ID) REFERENCES ImportantDates(Date_ID)
        )
        """,
    ]

# Global variable to store the DBModule instance
db = None

def execute_sql_view(request):
    """
    Handle SQL query execution and rendering the result in the HTML template.
    """
    global db
    form = SQLInputForm()
    result = None
    error = None

    # Establish the connection and SSH tunnel only if not already established
    if db is None:
        try:
            db = DBModule("config.ini")
            db.create_ssh_tunnel()
            db.connect_to_database()
            print("Connection Established!")
        except Exception as e:
            error = f"Error establishing database connection: {e}"
            return render(request, 'main/execute_sql.html', {'form': form, 'result': result, 'error': error})

    if request.method == 'POST':
        form = SQLInputForm(request.POST)
        action = request.POST.get('action', '')

        if action == 'disconnect_oracle':
            try:
                close_db_connection()
                result = "Disconnected from the database."
            except Exception as e:
                error = f"Error disconnecting from DB: {str(e)}"
        if action == 'drop_tables':
            for query in drop_tables_queries:
                result, _ = db.execute_sql(query)
            result = "Tables dropped successfully."
        elif action == 'create_tables':
            for query in create_tables_queries:
                result, _ = db.execute_sql(query)
            result = "Tables created successfully."
        elif action == 'populate_tables':
            for query in pop_tables_queries:
                result, _ = db.execute_sql(query)
            result = "Tables populated successfully."
        elif form.is_valid():
            query = form.cleaned_data['sql_query']
            try:
                if action == 'add_record':
                    table_name = request.POST.get('table_name')
                    record_data = request.POST.get('record_data')
                    try:
                        record_dict = eval(record_data)
                        columns = ', '.join(record_dict.keys())
                        values = ', '.join([f"'{value}'" for value in record_dict.values()])
                        add_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
                        db.execute_sql(add_query)
                        result = f"Record added successfully to table '{table_name}'."
                    except Exception as e:
                        error = f"Error adding record: {str(e)}"

                elif action == 'delete_record':
                    table_name = request.POST.get('table_name')
                    condition = request.POST.get('condition')
                    try:
                        delete_query = f"DELETE FROM {table_name} WHERE {condition}"
                        db.execute_sql(delete_query)
                        result = f"Record(s) deleted successfully from table '{table_name}'."
                    except Exception as e:
                        error = f"Error deleting record: {str(e)}"

                elif action == 'search_record':
                    table_name = request.POST.get('table_name')
                    condition = request.POST.get('condition')
                    try:
                        search_query = f"SELECT * FROM {table_name} WHERE {condition}"
                        search_result, columns = db.execute_sql(search_query)
                        if search_result:
                            # Convert search results into an HTML table
                            table = f'''
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        {"".join(f"<th>{col}</th>" for col in columns)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {"".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in search_result)}
                                </tbody>
                            </table>
                            '''
                            result = format_html(table)
                        else:
                            result = "No matching records found."
                    except Exception as e:
                        error = f"Error searching for record: {str(e)}"

                else:
                    # Regular SQL query execution
                    result, columns = db.execute_sql(query)
                    if isinstance(result, list) and columns:
                        # Convert result into an HTML table
                        table = f'''
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    {"".join(f"<th>{col}</th>" for col in columns)}
                                </tr>
                            </thead>
                            <tbody>
                                {"".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in result)}
                            </tbody>
                        </table>
                        '''
                        result = format_html(table)
            except Exception as e:
                error = f"Error: {str(e)}"
                traceback.print_exc()

    return render(request, 'main/execute_sql.html', {'form': form, 'result': result, 'error': error})


def close_db_connection():
    """
    Close the database connection and SSH tunnel (if open).
    """
    global db
    if db:
        db.close()
        db = None


'''def execute_sql(request):
    # Create a fresh form and set the result to None
    form = SQLInputForm()
    result = None

    if request.method == 'POST':
        # Load config and establish the SSH tunnel and database connection
        config = db_module.load_config()
        try:
            with db_module.create_ssh_tunnel(config) as tunnel:
                print("SSH Tunnel established")

                with db_module.connect_to_database(config) as connection:
                    print("Database connection successful")

                    with connection.cursor() as cursor:
                        # Determine the action (run query, drop tables, etc.)
                        action = request.POST.get('action')

                        if action == 'run_query':
                            # Load the form from the request
                            form = SQLInputForm(request.POST)

                            # If valid, clean the query and try to execute it
                            if form.is_valid():
                                sql_query = form.cleaned_data['sql_query']
                                try:
                                    result = db_module.execute_sql(sql_query, cursor)
                                except Exception as e:
                                    print(f"Error: {str(e)}")
                                    traceback.print_exc()

                        elif action == 'drop_tables':
                            try:
                                for query in drop_tables_queries:
                                    db_module.execute_sql(query, cursor)
                                result = "Tables dropped successfully."
                            except Exception as e:
                                print(f"Error: {str(e)}")
                                traceback.print_exc()

                        elif action == 'create_tables':
                            try:
                                for query in create_tables_queries:
                                    db_module.execute_sql(query, cursor)
                                result = "Tables created successfully."
                            except Exception as e:
                                print(f"Error: {str(e)}")
                                traceback.print_exc()

                        elif action == 'populate_tables':
                            try:
                                for query in pop_tables_queries:
                                    db_module.execute_sql(query, cursor)
                                result = "Tables populated successfully."
                            except Exception as e:
                                print(f"Error: {str(e)}")
                                traceback.print_exc()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            traceback.print_exc()

    # If valid input (no errors), return the form with the valid query in it
    return render(request, 'main/execute_sql.html', {'form': form, 'result': result})'''