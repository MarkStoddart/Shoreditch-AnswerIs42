###########
### AI Controller with HTTP abstracted away
###
### DB is a wrapper for whatever storage is backing the AI
### Use this for storage across games
###
### game contains a "storage" object which is a dict which will be
### persisted after returning
###
###########

from game import RESOURCES, GENERATOR_COST, GENERATOR_IMPROVEMENT_COST, PR_COST, MAX_RESOURCE_GENERATORS, MAX_IMPROVED_RESOURCE_GENERATORS

def start_game(db, game):
	# A new game is starting
	print "Starting a game"

def start_turn(db, game, actions):
	# Start of a turn
	# We have to end the turn with game.end_turn() when we're done
	# alhough we only get 15 seconds to act before our turn is ended by force
	
	# actions is a dict of things which have happened since my last turn,
	# where the keys are player ids, and the values are lists of actions taken,
	# each action is a dict which has an 'action' key (which can be 'purchase-pr', 'trade', etc.)

	def trade_for(requirements):
		# This just figures out how much I can give away without harming the minimum requirements
		# then offers everything extra I have for everything I need.
		# It's very dumb, you should replace it
		request = {}
		offer = {}

		for resource in RESOURCES:
			if resource in requirements and requirements[resource] > game.resources[resource]:
				request[resource] = requirements[resource] - game.resources[resource]
			else:
				to_offer = game.resources[resource] - requirements.get(resource, 0)
				if to_offer > 0:
					offer[resource] = to_offer

		return game.trade(offer, request)

	### First try to trade for resources I need

	if sum(game.generators.values()) < MAX_RESOURCE_GENERATORS:
		# Can build generators - try to trade for them
		if trade_for(GENERATOR_COST):
			taking_turn = True

	if sum(game.improved_generators.values()) < MAX_IMPROVED_RESOURCE_GENERATORS:
		# Can improve one of our existing ones
		if trade_for(GENERATOR_IMPROVEMENT_COST):
			taking_turn = True

	trade_for(PR_COST)

	# Then spend the resources

	while game.can_purchase_generator() and game.turn:
		generator_type = game.purchase_generator()
		print "Purchased %s" % generator_type

	while game.can_upgrade_generator() and game.turn:
		generator_type = game.upgrade_generator()
		print "Upgraded %s" % generator_type
		# Random chance to win a generator when upgrading.
		if random.randint(1, 10) == 5:
			generator_type = game.purchase_generator()
			print "Free %s" % generator_type

	while game.can_purchase_pr() and game.turn:
		game.purchase_pr()
		print "Purchased PR"

	if game.turn:
		game.end_turn()

def time_up(db, game):
	# We have ran out of time for this turn, it has been forced to end
	pass

def end_game(db, game, error=None):
	if error:
		print "Something went wrong! %s" % error
	else:
		print "Game over"

def incoming_trade(db, game, player, offering, requesting):
	# As long as I'm gaining at least one resource more than I'm giving away, I'll accept
	if sum(offering.values()) > sum(requesting.values()):
		return True
	return False