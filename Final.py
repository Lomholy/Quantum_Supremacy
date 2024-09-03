# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from supremacy import helpers

# This is your team name
CREATOR = "Quantum_supremacy"

def tank_ai(tank, info, game_map):
    """
    Function to control tanks.
    """
    tank.stop()
    tank.set_heading(tank.heading + 3)


def ship_ai(ship, info, game_map):
    """
    Function to control ships.
    """
    if not ship.stopped:
        if ship.stuck:
            if ship.get_distance(ship.owner.x, ship.owner.y) > 80:
                ship.convert_to_base()
            else:
                ship.set_heading(ship.heading + np.random.random() * 360.0)


def jet_ai(jet, info, game_map):
    """
    Function to control jets.
    """
    if "target" in info:
        jet.goto(*info["target"])
    else:
        jet.set_heading(jet.heading + 1.5 * np.random.random())


class PlayerAi:
    """
    This is the AI bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = CREATOR  # Mandatory attribute
        self.ntanks = {}
        self.nships = {}

    def run(self, t: float, dt: float, info: dict, game_map: np.ndarray):
        """
        This is the main function that will be called by the game engine.
        """

        # Get information about my team
        myinfo = info[self.team]

        # Iterate through all my bases and process build queue
        for base in myinfo["bases"]:
            # Bookkeeping
            uid = base.uid
            if uid not in self.ntanks:
                self.ntanks[uid] = 0
                self.nships[uid] = 0

            # Firstly, each base should build a mine if it has less than 3 mines
            if base.mines < 2:
                if base.crystal > base.cost("mine"):
                    base.build_mine()
            elif self.nships[uid] > 2:
                if base.crystal > base.cost("mine"):
                    base.build_mine()
            # If we have enough mines, pick something at random
            else:
                if self.nships[uid] < 4:
                    if base.crystal > base.cost("ship"):
                        ship = base.build_ship(heading=360*np.random.random())
                        self.nships[uid] += 1
                elif self.ntanks[uid] < 4:
                    if base.crystal > base.cost("tank"):
                        tank = base.build_tank(heading=360*np.random.random())
                        self.ntanks[uid] += 1
                elif base.crystal > base.cost("jet"):
                    jet = base.build_jet(heading=360*np.random.random())

        # Try to find an enemy target
        # If there are multiple teams in the info, find the first team that is not mine
        targets=[]
        dmsc_name = ""
        for name in info:
            if "DMSC" in name:
                dmsc_name = name
                break
        if len(info) > 1:
            for name in info:
                if name != self.team:
                    # Target ships & bases
                    if "bases" in info[name]:
                        target = 0
                        
                        try :
                            t = info[dmsc_name]["bases"][target]
                        except :
                            t = info[name]["bases"][target]
                        myinfo["target"] = [t.x, t.y]
                        break
                    

        # Control all my vehicles
        helpers.control_vehicles(
            info=myinfo, game_map=game_map, tank=tank_ai, ship=ship_ai, jet=jet_ai
        )
    def get_closest_base(self, bases, x, y):
        closest = None
        for base in bases:
            if closest is None or base.get_distance(x, y) < closest.get_distance(x, y):
                closest = base
        return closest
