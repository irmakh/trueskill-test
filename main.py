import redis
from flask import Flask,request
import trueskill

app = Flask(__name__)
redis = redis.Redis(host='redis', port=6379, db=0)
css = """    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">"""
@app.route('/')
def hello_world():
    players = redis.lrange('players', 0, -1)

    retval = """
<table><th><td><h4>Players</h4></td><td>POINT</td></th>"""
    i = 1
    for player in players:
        pname = str(player).replace("b'","").replace("'","")
        if(redis.exists(pname+'-level')):
            plevel = redis.get(pname+'-level')
        else:
            plevel = 0

        retval += f"<tr><td>{i}</td><td>"+pname+"</td><td>"+str(plevel).replace("b'","").replace("'","")+"</td></tr>"
        i = i+1
    retval += "</table>"
    return css+"""<table>
    <tr><td><a href='/add-player'> Add Player </a></td></tr>
    <tr><td><a href='/add-match'> Add Match </a></td></tr>
    <tr><td><a href='/start-session'> Start a new Session</a></td></tr>

    </table>
    """+retval

@app.route('/clear-players',methods=["GET"])
def clear_players():
    redis.delete("players")
    return f"{css}<a href='/'>Home</a>"



@app.route('/add-player',methods=["GET","POST"])
def add_player():
    if request.method == "POST":
        name = request.form['name']
        redis.lpush('players', name)
        return f"{css}{name} added <a href='/'>Home</a>"
    return css+"""
<form accept-charset=\"UTF-8\" action=\"\" autocomplete=\"off\" method=\"POST\">
	<label for=\"name\">Player Name</label><br />
	<input name=\"name\" type=\"text\" value=\"\" /> <br />
	<button type=\"submit\" value=\"Submit\">Add</button>
</form><a href='/'>Home</a>"""

@app.route('/start-session')
def start_session():
    players = redis.lrange('players', 0, -1)
    for player in players:
        pname = str(player).replace("b'","").replace("'","")
        if(redis.exists(pname+'-level')):
            redis.delete(pname+'-level')
            redis.delete(pname+'-skill')
    redis.delete("players")
    return f"{css}New Session Started <a href='/'>Home</a>"

@app.route('/remove-player')
def remove_player():
    return css+"""Remove Player"""

@app.route('/add-match',methods=["GET","POST"])
def add_match():
    if request.method == "POST":
        class Player(object):
          pass
        results = {'1':'2-0','2':'2-1'}
        p1 = request.form['p1']
        p2 = request.form['p2']
        result = request.form['result']

        p1Obj = Player()
        p1skill = (25.0, 25.0/3.0)
        p2skill = (25.0, 25.0/3.0)
        if(redis.exists(p1+'-skill')):
            p1skill = redis.lrange(p1+'-skill', 0, -1)

            redis.delete(p1+'-skill')
        if(redis.exists(p2+'-skill')):
            p2skill = redis.lrange(p2+'-skill', 0, -1)
            redis.delete(p2+'-skill')
        p1Obj.skill = (float(p1skill[0]), float(p1skill[1]))

        p1Obj.name = p1
        p2Obj = Player()
        p2Obj.skill = (float(p2skill[0]), float(p2skill[1]))
        p2Obj.name = p2
        if(result == '1'):
            p1Obj.rank = 1
            p2Obj.rank = 2
        elif(result == '2'):
            p1Obj.rank = 2
            p2Obj.rank = 1
        winconstant = 1
        if(result == '2'):
            winconstant = 0.7
        calculated = calculate(p1Obj,p2Obj,winconstant)
        p1level = calculated[0].skill[0]-3*calculated[0].skill[1]
        p2level = calculated[1].skill[0]-3*calculated[1].skill[1]

        redis.rpush(p1+'-skill', calculated[0].skill[0])
        redis.rpush(p1+'-skill', calculated[0].skill[1])
        redis.set(p1+'-level', p1level)

        redis.rpush(p2+'-skill', calculated[1].skill[0])
        redis.rpush(p2+'-skill', calculated[1].skill[1])
        redis.set(p2+'-level', p2level)


        return f"{css}{p1} VS {p2} Result: {results[result]} <br> {p1} Level: {p1level} <br> {p2} Level: {p2level}<br /><a href='/'>Home</a>"

    players = redis.lrange('players', 0, -1)
    def create_player_select(name,players):
        selectbox = f"<select name=\"{name}\" style='display:block !important'>"
        for player in players:
            selectbox += "<option value=\""+str(player).replace("b'","").replace("'","")+"\">"+str(player).replace("b'","").replace("'","")+"</option>"
        selectbox +="</select>"
        return selectbox
    return css+"""
<form accept-charset="UTF-8" action="" autocomplete="off" method="POST">
"""+create_player_select('p1',players)+"""
<br />
<h4>VS</h4>
<br />
"""+create_player_select('p2',players)+"""
Result:
<select name="result" style='display:block !important'>
<option value = "1">2-0</option>
 <option value = "2">2-1</option>
 </select>
<button type="submit" value="Submit">Submit</button></form><a href='/'>Home</a>
    """


@app.route('/calculate')
def calculate(p1,p2,winconstant):
    # The output of this program should match the output of the TrueSkill
    # calculator at:
    #
    #   http://atom.research.microsoft.com/trueskill/rankcalculator.aspx
    #
    # (Select game mode "custom", create 2 players each on their own team,
    # check the second "Draw?" box to indicate a tie for second place,
    # then click "Recalculate Skill Level Distribution".  The mu and sigma
    # values in the "after game" section should match what this program
    # prints.

    # The objects we pass to AdjustPlayers can be anything with skill and
    # rank attributes.  We'll create a simple Player class that has
    # nothing else.

    class Player(object):
      pass

    # Create two players.  Assign each of them the default skill.  The
    # player ranking (their "level") is mu-3*sigma, so the default skill
    # value corresponds to a level of 0.



    #ermac = Player()
    #ermac.skill = (25.0, 25.0/3.0)

    # The two players play a game.  Orc wins, Hurda is
    # lost.  The actual numerical values of the
    # ranks don't matter, they could be (1, 2) or (1, 2) or
    # (23, 45).  All that matters is that a smaller rank beats a
    # larger one, and equal ranks indicate draws.

    #ermac.rank = 2


    # Do the computation to find each player's new skill estimate.

    trueskill.AdjustPlayers([p1, p2],winconstant)
    return (p1,p2)
    # Print the results.

    msg = " p1: mu={0[0]:.3f}  sigma={0[1]:.3f} <br>".format(p1.skill)
    msg += " p2: mu={0[0]:.3f}  sigma={0[1]:.3f}".format(p2.skill)
    return msg
@app.route('/visitor')
def visitor():
    redis.incr('visitor')
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Visitor: %s" % (visitor_num)
@app.route('/visitor/reset')
def reset_visitor():
    redis.set('visitor', 0)
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Visitor is reset to %s" % (visitor_num)