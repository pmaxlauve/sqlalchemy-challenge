from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import datetime as dt

#get the data from sqlite file
Base = automap_base()
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#set up flask
app = Flask(__name__)

#set up home page
@app.route("/")
def home():
    
    #return all possible api routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#set up precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #open the session
    session=Session(engine)
    
    #create constant to filter the data by date
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    
    #query the precipitation data from the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    
    #convert data from a list of tuples to a dataframe
    df=pd.DataFrame(results, columns=['Date', 'Prcp'])
    df=df.fillna(0)
    
    #create a list of unique dates
    unq_dates=df['Date'].unique()

    #create an empty list to be jsonified later
    all_days = []
    
    #loop over unq_dates to create {key:value} where 'key' is each unique date, and 'value' is a list of precipitation recordings for that date
    for date in unq_dates:
    
        day= df[df['Date']==date]
    
        day_dict= {date: list(day['Prcp'])}
    
        all_days.append(day_dict)
        
    #close the session   
    session.close()
    
    #jsonify all_days
    return jsonify(all_days)
    
    
    
    
    
#set up stations page
@app.route("/api/v1.0/stations")
def stations():
    
    #open the session
    session=Session(engine)
    
    #query to get the station id for all stations
    stations=session.query(Station.station).all()
    
    #convert query to a df and put it into a jsonifiable form
    stations_df=pd.DataFrame(stations, columns=['station'])
    station_dict = [{"Stations": [entry for entry in stations_df['station']]}]
    
    #close session
    session.close()
    
    #jsonify station_dict
    return jsonify(station_dict)


    

    
    
#set up tobs page
@app.route("/api/v1.0/tobs")
def tobs():
    
    #open the session
    session=Session(engine)
    
    #set up query_date constant
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    
    #query date and tobs of given station over the last year
    tempF = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == 'USC00519281').all()
    
    #convert query data to a df
    tempF_df = pd.DataFrame(tempF, columns=['Date', 'Temperature'])
    
    #set up list to jsonify
    all_temps = []
    
    #iterate to fill all_temps with {date: temp} 
    for x in range(len(tempF_df)):
        temp_dict = {tempF_df.iloc[x, 0]: tempF_df.iloc[x, 1]}
        all_temps.append(temp_dict)
        
    #close the session  
    session.close()
    
    #jsonify all_temps
    return jsonify(all_temps)


#set up temp_stats_since page
@app.route("/api/v1.0/<start>")
def temp_stats_since(start):
    
    #start session
    session=Session(engine)
    
    #use split to convert 'start' to the form (yyyy, mm, dd)
    start_split= start.split('-')
    start_date= [int(x) for x in start_split]
    
    #query to get the min, max, and avg temps since the 'start' date
    tempstats=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= dt.date(start_date[0], start_date[1], start_date[2])).all()

    #manually create jsonifiable list
    stat_dict_list=[{'TMIN': tempstats[0][0]},
                   {'TAVG': tempstats[0][2]},
                   {'TMAX': tempstats[0][1]}]
    
    #close the session
    session.close()
    
    #jsonify stat_dict_list
    return jsonify(stat_dict_list)


#set up temp_stats_between page
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_between(start, end):
    
    #open the session
    session=Session(engine)
    
    #use split to convert 'start' to the form (yyyy, mm, dd)
    start_split= start.split('-')
    start_date= [int(x) for x in start_split]
    
    #use split to convert 'end' to the form (yyyy, mm, dd)
    end_split= end.split('-')
    end_date= [int(x) for x in end_split]
    
    #query to get the min, max, and avg temps between "start" and "end"
    tempstats=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= dt.date(start_date[0], start_date[1], start_date[2])).\
        filter(Measurement.date <= dt.date(end_date[0], end_date[1], end_date[2])).all()

    #manually create jsonifiable list
    stat_dict_list=[{'TMIN': tempstats[0][0]},
                   {'TAVG': tempstats[0][2]},
                   {'TMAX': tempstats[0][1]}]
    
    #close the session
    session.close()
    
    #jsonify stat_dict_list
    return jsonify(stat_dict_list)

if __name__ == "__main__":
    app.run(debug=True)


    








