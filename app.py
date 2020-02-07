import numpy as np

import datetime as dt
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement

Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
        """List all available api routes."""
        return (
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/&lt;start&gt;<br/>" 
            f"/api/v1.0/&lt;start&gt;/&lt;end&gt;" 
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    most_recent_entry = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())[2:-3]
    most_recent_entry = dt.datetime.strptime(most_recent_entry, "%Y-%m-%d")
    one_year_ago = most_recent_entry - dt.timedelta(days=365)
    one_year_ago = dt.datetime.strftime(one_year_ago, "%Y-%m-%d")

    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.station).all()   
    session.close()

    prcp_dict = {}
    for row in results:
        if row[0] not in prcp_dict:
            prcp_dict[row[0]] = {}
        prcp_dict[row[0]][row[1]] = row[2]
    
    return(prcp_dict) 


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).distinct().all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    most_recent_entry = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())[2:-3]
    most_recent_entry = dt.datetime.strptime(most_recent_entry, "%Y-%m-%d")
    one_year_ago = most_recent_entry - dt.timedelta(days=365)
    one_year_ago = dt.datetime.strftime(one_year_ago, "%Y-%m-%d")

    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.station).all()  
    session.close()

    tobs_dict = {}
    for row in results:
        if row[0] not in tobs_dict:
            tobs_dict[row[0]] = {}
        tobs_dict[row[0]][row[1]] = row[2]
    
    return(tobs_dict)


@app.route("/api/v1.0/<start>")
def start(start):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    ############################################################################
    ##### per README only a single output of tmin, tavg, tmax are required #####
    ############################################################################

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    values = results[0]
    keys = ["minimum temperature", "average temperature", "maximum temperature"]
    temp_dict = dict(zip(keys,values))
    session.close()

    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    ############################################################################
    ##### per README only a single output of tmin, tavg, tmax are required #####
    ############################################################################

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    values = results[0]
    keys = ["minimum temperature", "average temperature", "maximum temperature"]
    temp_dict = dict(zip(keys,values))
    session.close()

    return jsonify(temp_dict)
    
    
if __name__ == "__main__":
    app.run(debug=True)