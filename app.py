from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import datetime as dt

Base = automap_base()


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station







app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    df=pd.DataFrame(results, columns=['Date', 'Prcp'])
    df=df.fillna(0)
    unq_dates=df['Date'].unique()


    all_days = []
    for date in unq_dates:
    
        day= df[df['Date']==date]
    
        day_dict= {date: list(day['Prcp'])}
    
        all_days.append(day_dict)
        
        
    session.close()
        
    return jsonify(all_days)
    
    
    
    
    
    
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)

    stations=session.query(Station.station).all()
    stations_df=pd.DataFrame(stations, columns=['station'])
    station_dict = [{"Stations": [entry for entry in stations_df['station']]}]
    
    
    session.close()
    
    return jsonify(station_dict)


    

    
    

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    tempF = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == 'USC00519281').all()

    tempF_df = pd.DataFrame(tempF, columns=['Date', 'Temperature'])
    tempF_df

    all_temps = []

    for x in range(len(tempF_df)):
        temp_dict = {tempF_df.iloc[x, 0]: tempF_df.iloc[x, 1]}
        all_temps.append(temp_dict)
        
        
    session.close()
        
    return jsonify(all_temps)



@app.route("/api/v1.0/<start>")
def temp_stats_since(start):
    
    session=Session(engine)

    start_split= start.split('-')
    start_date= [int(x) for x in start_split]
    tempstats=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= dt.date(start_date[0], start_date[1], start_date[2])).all()


    stat_dict_list=[{'TMIN': tempstats[0][0]},
                   {'TAVG': tempstats[0][2]},
                   {'TMAX': tempstats[0][1]}]

    session.close()
    
    return jsonify(stat_dict_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_between(start, end):
    session=Session(engine)

    start_split= start.split('-')
    start_date= [int(x) for x in start_split]

    end_split= end.split('-')
    end_date= [int(x) for x in end_split]

    tempstats=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= dt.date(start_date[0], start_date[1], start_date[2])).\
        filter(Measurement.date <= dt.date(end_date[0], end_date[1], end_date[2])).all()


    stat_dict_list=[{'TMIN': tempstats[0][0]},
                   {'TAVG': tempstats[0][2]},
                   {'TMAX': tempstats[0][1]}]

    session.close()
    
    return jsonify(stat_dict_list)

    





if __name__ == "__main__":
    app.run(debug=True)


    








