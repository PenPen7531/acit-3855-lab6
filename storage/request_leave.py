# Jeffrey Wang
# A01228943

from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

TIME = datetime.time(0,0)
class RequestLeave(Base):
    """ Request Leave """

    __tablename__ = "Request_Leave"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    employee_id = Column(String(250), nullable=False)
    days_off = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    hours = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    

    def __init__(self, trace_id, employee_id, days_off, start_date, end_date, hours, reason):
        """ Initializes a leave request obj """
        self.trace_id = trace_id
        self.employee_id = employee_id
        self.days_off = days_off
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.start_date = datetime.datetime.combine(datetime.datetime.strptime(start_date, '%Y-%m-%d'), TIME)
        self.end_date = datetime.datetime.combine(datetime.datetime.strptime(end_date, '%Y-%m-%d'), TIME)
        self.hours = hours
        self.reason = reason



    def to_dict(self):
        """ Dictionary Representation of a leave request """
        dict = {}
        dict['trace_id'] = self.trace_id
        dict['id'] = self.id
        dict['employee_id'] = self.employee_id
        dict['days_off'] = self.days_off
        dict['date_created'] = self.date_created
        dict['start_date'] = self.start_date
        dict['end_date'] = self.end_date
        dict['hours_off'] = self.hours
        dict['reason'] = self.reason

        return dict
