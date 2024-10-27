# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')


# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with = engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create a session

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
       return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"/api/v1.0/tobs"
    )

#Convert the query results to a dictionary by using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    dt_year_prior = ((dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d'))
    
    # Retrieve the data and precipitation scores
    year_prior_data  = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= dt_year_prior).all()) 

    # Close Session                                                  
    session.close()

    # Create a dictionary 
    prcp_data = []
    for date, prcp in year_prior_data:
        prior_dict = [f"{date}",f"{prcp} inches"]
        prcp_data.append(prior_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations():    

    # Create Session from pythong to DB
    session = Session(engine) 
    
    # Query for list of stations
    results = session.query(Station.station, Station.name).all()
    
    station_data =[]
    for name, station in results:
        station_dict ={}
        station_dict['Station ID'] = name
        station_dict['Station']= station
        station_data.append(station_dict)

    # Return the JSON representation of your dictionary. 
    return jsonify(station_data)
    

#------------------------------------------------


@app.route("/api/v1.0/tobs")
def tobs(): 
    # Create Session from pythong to DB
    session = Session(engine) 
    
    # Query for lastest date
    lastest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Convert date into a string
    lastest_date_str = dt.datetime.strptime(lastest_date,"%Y-%m-%d")
    
    # Query for one year ago
    year_ago = lastest_date_str - dt.timedelta(days=365)
    # Convert date into a string
    year_ago_str = year_ago.strftime("%Y-%m-%d")

    # Query for the most active station
    most_active_station = session.query(    Measurement.station, 
                                            func.count(Measurement.station)).\
                                            group_by(Measurement.station).\
                                            order_by(func.count(Measurement.station).desc()).first()[0]

    # Query the dates and temperature observations of the most active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime('%Y-%m-%d',Measurement.date)>= year_ago_str).\
        filter(Measurement.station == most_active_station).all()

    tobs_data=[]
    for date, tobs in results:
        tobs_dict ={}
        tobs_dict['Date'] = date
        tobs_dict['Temperature']= tobs
        tobs_data.append(tobs_dict)

    # Return the JSON representation of your dictionary. 
    return jsonify(tobs_data)


#------------------------------------------------


@app.route("/api/v1.0/<start>")

def specified_start(start):
    '''Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start'''
    specified_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    results = list(np.ravel(specified_start))
    return jsonify (results)


@app.route("/api/v1.0/<start>/<end>")
def specified_start_end(start, end):
    '''Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start and end'''
    specified_start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
    results = list(np.ravel(specified_start_end))
    return jsonify (results)



if __name__ == "__main__":
    app.run(debug=True)