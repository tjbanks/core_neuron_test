from bmtk.utils.sim_setup import build_env_bionet
from bmtk.builder import NetworkBuilder
from bmtk.simulator import bionet
import os, sys
import numpy as np
import synapses
import warnings
import h5py
import synapses
import matplotlib.pyplot as plt
import pdb
from neuron import h
from neuron import coreneuron
import reports
coreneuron.enable = True


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

    sim = bionet.BioSimulator.from_config(conf, network=graph)

    # This calls insert_mechs() on each cell to use its gid as a seed
    # to the random number generator, so that each cell gets a different
    # random seed for the point-conductance noise
    cells = graph.get_local_cells()
    for cell in cells:
        cells[cell].hobj.insert_mechs(cells[cell].gid)
        pass
    
    voltage_gids = [1,0]
    reports.voltage_record(voltage_gids) 

    reports.spike_record()
    sim.run()

    reports.save_voltage()
    reports.save_spikes()


    bionet.nrn.quit_execution()

run('/home/gjgpb9/coreneuron_test/config.json')