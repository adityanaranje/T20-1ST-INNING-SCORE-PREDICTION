from flask import Flask, render_template, request
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

@app.route('/')
@app.route('/home', methods=['POST','GET'])
def home():
    model = pickle.load(open('model/pipe.pkl','rb'))
    team_avg = pd.read_csv('data/team_average.csv')
    city_avg = pd.read_csv('data/city_average.csv')

    team = list(team_avg['team'])
    bat_avg = list(team_avg['batting_average'])
    bowl_avg = list(team_avg['bowling_average'])
    cities = list(city_avg['city'])
    c_avg = list(city_avg['Average_runs'])
    abr = ['AFG','AUS','BAN','ENG','IND','IRE','NAM','NED','NZ','OMA','PAK','PNG','SCO','RSA','SL','WI']
    pred = 0
    if request.method == "POST":

        pred = 1

        bteam = abr[int(request.form['battingteam'])]

        batting_team = team[int(request.form['battingteam'])]
        bowling_team = team[int(request.form['bowlingteam'])]
        city = cities[int(request.form['city'])]

        try:
            current_score = float(request.form['score'])
            overs = request.form['overs']
            try:
                b = int(overs.split(".")[1])
            except:
                b = 0
            balls = int(overs.split(".")[0])*6+b
            balls_left = 120 - balls
            wickets = int(request.form['wickets'])
            wickets_left = 10 - wickets
            crr = current_score*6/balls
            last_five = int(request.form['last_five'])
        except:
            pred = 2
            error = "Invalid Data Entered"
            return render_template('home.html', teams=team, city=cities, pred=pred,error =error)

        if current_score<last_five:
            pred = 2
            error = "Current Runs Can Not Be Less Than Runs Scored In Last 5 overs"
            return render_template('home.html', teams=team, city=cities, pred=pred,error =error)

        if wickets>10 or wickets<0:
            pred = 2
            error = "Wickets Must Be Between 1-10"
            return render_template('home.html', teams=team, city=cities, pred=pred,error =error)

        if balls/6>20 or balls/6<5:

            pred = 2
            error = "Overs Must Be Between 5-20"
            return render_template('home.html', teams=team, city=cities, pred=pred,error =error)

        if batting_team==bowling_team:
            pred = 2
            error = "Batting Team And Bowling Team Must Be Different"
            return render_template('home.html', teams=team, city=cities, pred=pred,error =error)



        batting_team_avg = bat_avg[team.index(batting_team)]
        bowling_team_avg = bowl_avg[team.index(bowling_team)]
        city_avg = c_avg[cities.index(city)]
        data = pd.DataFrame({'batting_team':[batting_team], 'bowling_team':[bowling_team], 'city':[city],
                            'current_score':[current_score], 'balls_left':[balls_left],'wickets_left':[wickets_left],
                            'crr':[crr],'last_five':[last_five], 'batting_team_avg':[batting_team_avg],
                            'bowling_team_avg':[bowling_team_avg], 'city_avg':[city_avg]})
        predicted = int(model.predict(data))
        
        
        if predicted<current_score:
            predicted =  int(current_score+int(7*balls_left/6))


        if predicted-current_score<=6 and balls>114:
            predicted = predicted+6

        if predicted-current_score>0 and predicted-current_score<20 and wickets<8 and balls>104:
            predicted = predicted+20

        if predicted-current_score>0 and predicted-current_score<25 and wickets<7 and balls>90:
            predicted = predicted+25
            
        if predicted-current_score<35 and wickets<7 and balls<=90 and balls>60:
            predicted = predicted+(35-abs(predicted-current_score))
        
        runs_c = int(current_score+int(crr*balls_left/6))
        runs_6 = int(current_score+int(6*balls_left/6))
        runs_8 = int(current_score+int(8*balls_left/6))
        runs_10 = int(current_score+int(10*balls_left/6))
        runs_12 = int(current_score+int(12*balls_left/6))

        return render_template('home.html', teams=team, city=cities,runs_c=runs_c,runs_6=runs_6,runs_8=runs_8,
        runs_10=runs_10,runs_12=runs_12,predicted=predicted, pred=pred,bteam=bteam,wickets_fall=wickets,current_score=int(current_score),overs=overs)

    return render_template('home.html', teams=team, city=cities)

if __name__ == '__main__':
    app.run(debug=False)
