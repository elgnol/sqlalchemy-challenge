# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_d><br/>"
        f"/api/v1.0/<start_d>/<end_d>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date,func.max(Measurement.prcp)).group_by(Measurement.date).order_by(Measurement.date).filter(Measurement.date > "2016-08-22").all()
    session.close()
    
    precip_year = {}
    for date, prcp in results:
        precip_year[date] = prcp
    return jsonify(precip_year)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date).filter(Measurement.date > "2016-08-22").filter(Measurement.station == "USC00519281")
    session.close()
    
    temp_list = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict[date] = tobs
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start_d>")
def start_date(start_d):
    start = dt.date.fromisoformat(start_d)-dt.timedelta(days=1)
    if start>=dt.date(2009,12,31) and start<dt.date(2017,8,23):
        session = Session(engine)
        results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>start).one()
        session.close()
            
        return jsonify({'Min':results[0],'Max':results[1],'Average':round(results[2],1)})
    else:
        return jsonify({'ERROR' : f'The date inputed: {start_d} is not a valid date or not in format YYYY-MM-DD'})
    
@app.route("/api/v1.0/<start_d>/<end_d>")
def start_end(start_d, end_d):
    try:
        start = dt.date.fromisoformat(start_d)-dt.timedelta(days=1)
        if start<dt.date(2009,12,31) or start>=dt.date(2017,8,23):
            return jsonify({"error": f"Date input: {start_d} is not in the available date range 2010-01-01 to 2017-08-23"}), 404
        try:
            end = dt.date.fromisoformat(end_d)+dt.timedelta(days=1)
            if end<=start: 
                return jsonify({"error": f"Date input: {end_d} is before start date"}), 404
            if end>dt.date(2017,8,24): 
                return jsonify({"error": f"Date input: {end_d} is not in the available date range 2010-01-01 to 2017-08-23"}), 404
            
            session = Session(engine)
            results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>start).filter(Measurement.date<end).one()
            session.close()
            
            return jsonify({'Min':results[0],'Max':results[1],'Average':round(results[2],1)})
        except ValueError:
            return jsonify({"error": f"Date input: {end_d} is not a valid date in isoformat YYYY-MM-DD"}), 404
    except ValueError:
        return jsonify({"error": f"Date input: {start_d} is not a valid date in isoformat YYYY-MM-DD"}), 404

if __name__ == '__main__':
    app.run(debug=True)    