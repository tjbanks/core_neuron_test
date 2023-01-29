from bmtk.simulator import bionet
from bmtk.utils.sim_setup import build_env_bionet
from bmtk.builder import NetworkBuilder
import os, sys
import numpy as np
import synapses
import warnings
import h5py
import synapses
import matplotlib.pyplot as plt

import reports

from corebmtk import CoreBioSimulator


def run(config_file):

    warnings.simplefilter(action='ignore', category=FutureWarning)
    synapses.load()

    conf = bionet.Config.from_json(config_file, validate=True)
    conf.build_env()

    graph = bionet.BioNetwork.from_config(conf)

    # This fixes the morphology error in LFP calculation
    pop = graph._node_populations['biophysical']
    for node in pop.get_nodes():
        node._node._node_type_props['morphology'] = node.model_template[1]

    sim = CoreBioSimulator.from_config(conf, network=graph, gpu=False)

    # This calls insert_mechs() on each cell to use its gid as a seed
    # to the random number generator, so that each cell gets a different
    # random seed for the point-conductance noise
    cells = graph.get_local_cells()
    for cell in cells:
        cells[cell].hobj.insert_mechs(cells[cell].gid)
    
    voltage_gids = [1,0]
    reports.voltage_record(voltage_gids)
    
    sim.run()

    reports.save_voltage()

    bionet.nrn.quit_execution()

    

run('./config.json')