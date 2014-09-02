import re
import math
import operator
import random
import sys
from threading import Thread
import datetime
import calendar

games_to_play = 0
current_rank = 25
current_subrank = 0
stars_left = 0

games_played_today = 0

stars_per_level = [1,
                   5, 5, 5, 5, 5,
                   5, 5, 5, 5, 5,
                   4, 4, 4, 4, 4,
                   3, 3, 3, 3, 3,
                   2, 2, 2, 2, 2]

def total_stars():
    global stars_per_level
    sum = 0
    for k in stars_per_level:
        sum += k 
    return sum

# todo:

# break out by class
# import into a db for better parsing

# use/loss summary graph
# output rank for a graph

# done: progress indicator based on estimated games
# done: "are you on track" based on current win rate

# incorporate first/second stats
# games per day stats

# stars per day

# done: overall meta

# do we want to use this as an exercise for test-driven development?
# and proper object (e.g. not using globals)
# maybe!

file = "september2014.md"

wins = {}
played = {}
played_5 = {}
wins_5 = {}
ranks = {}
ranks_5 = {}

active_deck = ""
active_day = ""
old_active_day = ""

# overall

def pretty_stats(groups):
    w = groups[0]
    t = groups[1]
    if t == 0:
        return
    pct = groups[2]
    wsi = groups[3]
    rank = groups[4]
    pretty = str(w).rjust(4) + "/" + str(t).ljust(4) + "  "
    pretty += str(pct).rjust(5) + "%" #+ "  " + str(wsi).rjust(5)
    pretty += " " + str(rank).rjust(10)
    return pretty

# later add rank stats

def get_stats_overall_5():
    global wins_5, played_5, ranks_5
    n_total = 0
    n_wins = 0
    n_ranks = 0
    for deck, records in played_5.iteritems():
        for k, v in played_5[deck].iteritems():
            n_total += v
        if deck in wins:
            for k, v in wins_5[deck].iteritems():
                n_wins += v
        for k, v in ranks_5[deck].iteritems():
            n_ranks += v
    if n_total == 0:
        return 0, 0, 0, 0, 0
    return n_wins, n_total, round(float(n_wins)/n_total*100, 2), round(wilson(n_total, n_wins), 3), round(float(n_ranks)/n_total, 2)

def get_stats_overall():
    global wins, played, ranks
    n_total = 0
    n_wins = 0
    n_ranks = 0
    for deck, records in played.iteritems():
        for k, v in played[deck].iteritems():
            n_total += v
        if deck in wins:
            for k, v in wins[deck].iteritems():
                n_wins += v
        for k, v in ranks[deck].iteritems():
            n_ranks += v
    if n_total == 0:
        return 0, 0, 0, 0, 0
    return n_wins, n_total, round(float(n_wins)/n_total*100, 2), round(wilson(n_total, n_wins), 3), round(float(n_ranks)/n_total, 2)

# calculate stars remaining based on current_rank
def stars_remaining():
    global current_rank, current_subrank, stars_per_level
    global stars_left, active_deck
    
    if current_rank == 0: # already legendary
        return
    
    ts = total_stars()

    stars_left = 0

    for i in range(0, current_rank):
        stars_left += stars_per_level[i]
    
    stars_left += stars_per_level[current_rank] - current_subrank
    
    stars_earned = ts - stars_left
    
    print
    print "Rank %d.%d: currently earned" % (current_rank, current_subrank)+ str(stars_earned).rjust(3), "stars; " + str(round(float(stars_earned)/ts*100,2)).rjust(5) + "% to Legend;"+  str(stars_left).rjust(3), "stars left;", 
    print games_played_today, "games played today."
#    print games_to_play, "games to play today."

    print
    sys.stdout.flush()
    winrate = get_stats_overall()[2]/100
    deck_winrate = get_stats(active_deck)[2]/100

    games_played = get_stats_overall()[1]

    winrate_5 = get_stats_overall_5()[2]/100

    gul = games_until_legend(winrate)
    gul_deck = games_until_legend(deck_winrate)

    gul_5 = games_until_legend(winrate_5)

    sys.stdout.flush()

    print str("Estimating %d games until Legend at overall win rate. (%.2f%%)" % (gul, (winrate*100))).ljust(65), "%.2f%% of the way there" % (float(100*games_played)/(games_played+gul))

#    print str("Estimating %d games until Legend at rank 5+ win rate. (%.2f%%)" % (gul_5, (winrate_5*100))).ljust(65), "%.2f%% of the way there" % (float(100*games_played)/(games_played+gul_5))

    print str("Estimating %d games until Legend at my deck win rate. (%.2f%%)" % (gul_deck, (deck_winrate*100))).ljust(65), "%.2f%% of the way there" % (float(100*games_played)/(games_played+gul_deck))
    sys.stdout.flush()
    for target_winrate in (0.55, 0.6, 0.65):
        gul_target = games_until_legend(target_winrate)
        print str("      Est. %d games until Legend at desired win rate. (%.2f%%)" % (gul_target, (target_winrate*100))).ljust(65), "%.2f%% of the way there" % (float(100*games_played)/(games_played+gul_target))
    
    today = datetime.datetime.now()

    days_this_month = calendar.monthrange(today.year, today.month)[1]
    
    print "Based on the calendar, we should be at least  ".rjust(65), "%.2f%% of the way there" % (today.day * 100 / days_this_month)
        

   
def sim_one(wr, sl, games):
    streak = 0
    n_games = 0
    while sl > 0:
        if sl > 90:
            break
        n_games += 1
        rnd = random.random()
        if rnd <= wr:
            # win
            if sl > 26:
                if streak > 2:
                    sl -= 2
                    streak += 1
                else:
                    sl -= 1
                    streak += 1
            else:
                sl -= 1
                streak += 1
        else:
            streak = 0
            sl += 1
    games += [n_games]
    return
    
# use the deck or global winrate


# Specifically, the formula is #GamesRequired = #StarsRequired / ((Winrate * 2) - 1). At 25 stars from rank 5 to legend, that means:
# this ignores win streaks (and is much faster)
def games_until_legend(winrate=0.7):
    global current_rank, current_subrank, stars_left
    games_required = stars_left / ((winrate*2)-1)
    return games_required

def get_stats(deck):
    global wins, played, ranks
    n_total = 0
    n_wins = 0
    n_ranks = 0
    if deck not in played:
        return 0, 0, 0, 0, 0
    for k, v in played[deck].iteritems():
        n_total += v
    if deck in wins:
        for k, v in wins[deck].iteritems():
            n_wins += v
    for k, v in ranks[deck].iteritems():
        n_ranks += v
    return n_wins, n_total, round(float(n_wins)/n_total*100, 2), round(wilson(n_total, n_wins), 3), round(float(n_ranks)/n_total, 2)
        

# later add rank stats    
def get_stats_matchup(deck, enemy):
    global wins, played, ranks
    n_total = 0
    n_wins = 0
    n_total += played[deck][enemy]
    if deck in wins:
        if enemy in wins[deck]:
            n_wins += wins[deck][enemy]
    return n_wins, n_total, round(float(n_wins)/n_total*100, 2), round(wilson(n_total, n_wins), 3), round(float(ranks[deck][enemy])/n_total, 2)

def increment(d, a, b, by = 1):
    if a not in d:
        d[a] = {}
    if b not in d[a]:
        d[a][b] = 0
    d[a][b] += by

def add_game(groups):
    global wins, played, ranks, active_deck, played_5, wins_5
    global current_rank, current_subrank, games_played_today
    enemy_deck = groups[0]
    position = groups[1]
    outcome = groups[2]
    rank = int(groups[3]) # legend is rank 0
    subrank = int(groups[4]) # legend ranting is 0.242 -- for legend 242
    current_rank = rank
    current_subrank = subrank
    games_played_today += 1

    win = False
    if outcome == "Won":
        win = True

    if rank <= 5:
        increment(played_5, active_deck, enemy_deck)
    increment(played, active_deck, enemy_deck)
    if win == True:
        increment(wins, active_deck, enemy_deck)
        if rank <= 5:
            increment(wins_5, active_deck, enemy_deck)

    increment(ranks, active_deck, enemy_deck, by = rank)
    if rank <= 5:
        increment(ranks_5, active_deck, enemy_deck, by = rank)


def parse(line):
    global active_deck, games_to_play, games_played_today
    global current_rank, current_subrank
    global active_day, old_active_day
    new_session = "# (.*) \((.*)\) \*(.*)\.(.*)\*"
    new_game = "\* (.*), (.*), (.*). \*(.*)\.(.*)\*"
    # anything else is a comment to ignore
    

    
    # check if the line matches new_session or new_game
    # if it matches new session, set the active deck
    se = re.match(new_session, line)
    if se:
        active_deck = se.groups()[0]
        old_active_day = active_day
        active_day = se.groups()[1]
        if active_day != old_active_day:
            games_played_today = 0
        current_rank = int(se.groups()[2])
        current_subrank = int(se.groups()[3])


   
    ge = re.match(new_game, line)
    if ge:
        add_game(ge.groups())

    if line[0] == "*" and not ge:
        if line != "*\n" and line != "* \n":
            print "failed parse", line    
        else:
            games_to_play += 1


def log(file):
    f = open(file, "r")
    lines = f.readlines()
    f.close()
    
    for l in lines:
        parse(l)

def stats():
    print "Deck vs. Matchup".ljust(30), "wins/played", "  pct", " avg. rank".rjust(5)
    sorted_decks = sorted(played.items(), reverse=False,
                          key = lambda (k, v) : v)
    for k, v in sorted_decks:
        print str(k).ljust(30), pretty_stats(get_stats(k))
        # iterate in order, from most played against to least
        sorted_played = sorted(played[k].items(), reverse=True,
                               key=lambda (k, v) : v)

        for kk, vv in sorted_played:
            print " ", str(kk).ljust(28), pretty_stats(get_stats_matchup(k, kk))
        print
    
    print "All Decks".ljust(30), pretty_stats(get_stats_overall())
    print

    return

def meta():

    meta = {}
    
    total = 0

    global played
    for k, v in played.iteritems():
        for kk, vv in v.iteritems():
            if kk not in meta:
                meta[kk] = 0
            meta[kk] += vv
            total += vv

    print str("Current Meta").ljust(30), str(total).rjust(6)

    others = 0
    
    if total == 0:
        return
    

    sorted_meta = sorted(meta.items(), reverse=True, key = lambda (k, v) : v)
    for a, b in sorted_meta:
        if b > 1:
            print "  ", str(a).ljust(28), str(b).rjust(5),
            print str(round(100*float(b)/total,2)).rjust(9) + "%"
        else:
            others += b
    
    if others >= 0:
        print "  ", str("Other").ljust(28), str(others).rjust(5),
        print str(round(100*float(others)/total,2)).rjust(9) + "%"

def meta_5():

    meta = {}
    
    total = 0

    global played_5
    for k, v in played_5.iteritems():
        for kk, vv in v.iteritems():
            if kk not in meta:
                meta[kk] = 0
            meta[kk] += vv
            total += vv

    print str("Rank 5+ Meta").ljust(30), str(total).rjust(6)

    others = 0
    
    if total == 0:
        return
    

    sorted_meta = sorted(meta.items(), reverse=True, key = lambda (k, v) : v)
    for a, b in sorted_meta:
        if b > 1:
            print "  ", str(a).ljust(28), str(b).rjust(5),
            print str(round(100*float(b)/total,2)).rjust(9) + "%"
        else:
            others += b
    
    if others >= 0:
        print "  ", str("Other").ljust(28), str(others).rjust(5),
        print str(round(100*float(others)/total,2)).rjust(9) + "%"



log(file)
stats()
meta()
print
meta_5()
stars_remaining()


