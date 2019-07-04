import csv
import requests
from discord import Webhook, RequestsWebhookAdapter

import global_constants


class SendWebhooks:
    def __init__(self, new_turns):
        assert(not len(new_turns) == 0)
        self.new_turns = new_turns

    def send_all_new_turns(self):
        # pull discord player ids for each steam player name from a local text file
        player_aliases = {}
        for row in parse_alias_file(global_constants.path_to_player_aliases, '|'):
            player_aliases[row[0]] = row[1]

        # pull webhook ids and tokens to reach the channel's webhook bot for each game from a local text file
        game_aliases = {}
        for row in parse_alias_file(global_constants.path_to_game_aliases, '|'):
            game_aliases[row[0]] = {'id': row[1], 'token': row[2]}

        try:
            for turn in self.new_turns:
                player_name = turn[global_constants.player]
                game_name = turn[global_constants.game]
                turn_number = turn[global_constants.turn]

                if player_name in player_aliases:
                    discord_id = player_aliases[player_name]
                else:
                    discord_id = "[name unavailable]"

                if game_name in game_aliases:
                    webhook_id = game_aliases[game_name]['id']
                    webhook_token = game_aliases[game_name]['token']
                else:
                    webhook_id = game_aliases[global_constants.overflow_channel_name]['id']
                    webhook_token = game_aliases[global_constants.overflow_channel_name]['token']

                webhook = Webhook.partial(webhook_id, webhook_token, adapter=RequestsWebhookAdapter())
                webhook.send("<@%s>, take turn #%s in %s" % (discord_id, turn_number, game_name))
        except Exception as error:
            print(error)
            return False
        return True


def parse_alias_file(path, delimiter=','):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            if row:
                yield row
