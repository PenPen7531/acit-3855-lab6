from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


# Makes time midnight. Used for dates that do not need to record time
TIME = datetime.time(0,0)

# Declarative code
class Employee(Base):
    """ Employees """

    # Specifies table name
    __tablename__ = "Employees"

    # Specifies columns
    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    employee_id = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    manager_code = Column(Integer, nullable=False)
    phone_number = Column(Integer, nullable=False)
    position = Column(String(50), nullable=False)
    salary = Column(Integer, nullable=False)


    def __init__(self, trace_id, employee_id, address, birth_date, first_name, 
                 last_name, manager_code, phone_number, position, salary):
        """ Initializes Employee class """
        self.trace_id = trace_id
        self.employee_id = employee_id
        self.address = address

        # Combines the input of the date and adds the midnight time constant. Needed to add date to DB
        self.birth_date = datetime.datetime.combine(datetime.datetime.strptime(birth_date, '%Y-%m-%d'), TIME)
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.first_name = first_name
        self.last_name = last_name
        self.manager_code = manager_code
        self.phone_number = phone_number
        self.position = position
        self.salary = salary


    def to_dict(self):
        """ Dictionary Representation of employee """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['employee_id'] = self.employee_id
        dict['address'] = self.address
        dict['birth_date'] = self.birth_date
        dict['date_created'] = self.date_created
        dict['first_name'] = self.first_name
        dict['last_name'] = self.last_name
        dict['manager_code'] = self.manager_code
        dict['phone_number'] = self.phone_number
        dict['position'] = self.position
        dict['salary'] = self.salary

        return dict
