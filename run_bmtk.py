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

import reports



import time
import neuron
from neuron import coreneuron
from neuron.units import mV
coreneuron.enable = True
coreneuron.gpu = True

from bmtk.simulator.bionet.io_tools import io
from bmtk.simulator.bionet import modules as mods

pc = h.ParallelContext()    # object to access MPI methods


class CoreBioSimulator(bionet.BioSimulator):

    def __elapsed_time(self, time_s):
        if time_s < 120:
            return '{:.4} seconds'.format(time_s)
        elif time_s < 7200:
            mins, secs = divmod(time_s, 60)
            return '{} minutes, {:.4} seconds'.format(mins, secs)
        else:
            mins, secs = divmod(time_s, 60)
            hours, mins = divmod(mins, 60)
            return '{} hours, {} minutes and {:.4} seconds'.format(hours, mins, secs)

    def run(self):
        """Run the simulation:
        if beginning from a blank state, then will use h.run(),
        if continuing from the saved state, then will use h.continuerun() 
        """
        for mod in self._sim_mods:
            if isinstance(mod, mods.ClampReport):
                if mod.variable == "se":
                    mod.initialize(self, self._seclamps)
                elif mod.variable == "ic":
                    mod.initialize(self, self._iclamps)
                elif mod.variable == "f_ic":
                    mod.initialize(self, self._f_iclamps)
            else:
                mod.initialize(self)

        self.start_time = h.startsw()
        s_time = time.time()
        pc.timeout(0)
         
        pc.barrier()  # wait for all hosts to get to this point
        io.log_info('Running simulation for {:.3f} ms with the time step {:.3f} ms'.format(self.tstop, self.dt))
        io.log_info('Starting timestep: {} at t_sim: {:.3f} ms'.format(self.tstep, h.t))
        io.log_info('Block save every {} steps'.format(self.nsteps_block))

        if self._start_from_state:
            h.continuerun(h.tstop)
        else:
            # make sure to enable cache efficiency
            h.cvode.cache_efficient(1) 
            #h.run(h.tstop)        # <- runs simuation: works in parallel
            io.log_info('Running core neuron sim')
            coreneuron.verbose = 3 # 3 equals debug mode
            h.stdinit()
            
            h.finitialize(-70 * mV)
            pc.psolve(h.tstop)
                    
        pc.barrier()

        for mod in self._sim_mods:
            mod.finalize(self)
        pc.barrier()

        end_time = time.time()

        sim_time = self.__elapsed_time(end_time - s_time)
        io.log_info('Simulation completed in {} '.format(sim_time))


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

    sim = CoreBioSimulator.from_config(conf, network=graph)

    # This calls insert_mechs() on each cell to use its gid as a seed
    # to the random number generator, so that each cell gets a different
    # random seed for the point-conductance noise
    cells = graph.get_local_cells()
    for cell in cells:
        cells[cell].hobj.insert_mechs(cells[cell].gid)
    
    voltage_gids = [1,0]
    reports.voltage_record(voltage_gids) 

    reports.spike_record()

    sim.run()

    reports.save_voltage()
    reports.save_spikes()


    bionet.nrn.quit_execution()

run('./config.json')