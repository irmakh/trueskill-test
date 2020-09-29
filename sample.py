from __future__ import print_function
import trueskill

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

orc = Player()
orc.skill = (25.0, 25.0/3.0)

hurda = Player()
hurda.skill = (25.0, 25.0/3.0)

#ermac = Player()
#ermac.skill = (25.0, 25.0/3.0)

# The two players play a game.  Orc wins, Hurda is
# lost.  The actual numerical values of the
# ranks don't matter, they could be (1, 2) or (1, 2) or
# (23, 45).  All that matters is that a smaller rank beats a
# larger one, and equal ranks indicate draws.

orc.rank = 1
hurda.rank = 2
#ermac.rank = 2


# Do the computation to find each player's new skill estimate.

trueskill.AdjustPlayers([orc, hurda])

# Print the results.

print(" Orc: mu={0[0]:.3f}  sigma={0[1]:.3f}".format(orc.skill))
print(" Hurda: mu={0[0]:.3f}  sigma={0[1]:.3f}".format(hurda.skill))
#print(" Ermac: mu={0[0]:.3f}  sigma={0[1]:.3f}".format(ermac.skill))
