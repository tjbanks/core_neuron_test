from abc import abstractmethod
import time

from bmtk.simulator import bionet
from bmtk.simulator.bionet.io_tools import io
from bmtk.simulator.bionet import modules as mods
import bmtk.simulator.utils.simulation_reports as reports
import h5py
import neuron
from neuron import coreneuron
from neuron import h
from neuron.units import mV

coreneuron.enable = True
coreneuron.gpu = True

pc = h.ParallelContext()    # object to access MPI methods

class CoreMod():

    def __init__(self,*args,**kwargs):
        pass

    @abstractmethod
    def initialize(self,*args,**kwargs):
        pass

    @abstractmethod
    def finalize(self,*args,**kwargs):
        pass

class CoreSpikesMod(CoreMod):

    def __init__(self,*args,**kwargs):
        self.corenrn_all_spike_t = h.Vector()
        self.corenrn_all_spike_gids = h.Vector()
        self.spikes_file = kwargs.get('spikes_file')
        
    def initialize(self,*args,**kwargs):
        pc.spike_record(-1, self.corenrn_all_spike_t, self.corenrn_all_spike_gids )

    def finalize(self,*args,**kwargs):
        np_corenrn_all_spike_t = self.corenrn_all_spike_t.to_python()
        np_corenrn_all_spike_gids = self.corenrn_all_spike_gids.to_python()
        
        fp = h5py.File(self.spikes_file, "w")
        grp = fp.create_group('spikes/biophysical')
        grp.create_dataset('node_ids',data=list(np_corenrn_all_spike_gids))
        grp.create_dataset('timestamps',data=list(np_corenrn_all_spike_t))
        fp.close()


class CoreBioSimulator(bionet.BioSimulator):
    """
    A sub class implementation of bionet.BioSimulator compatible with CoreNeuron

    Use:
    Replace 
        sim = bionet.BioSimulator.from_config(conf, network=graph)
    With
        sim = CoreBioSimulator.from_config(conf, network=graph)
    """

    def __init__(self, network, dt, tstop, v_init, celsius, nsteps_block, start_from_state=False):
        super(CoreBioSimulator, self).__init__(network, dt, tstop, v_init, celsius, nsteps_block, start_from_state=False)

        io.log_info('Running core neuron sim')
        coreneuron.verbose = 3 # 3 equals debug mode      

        self.config = None
        self.enable_core_mods = True
        self._core_mods = []  

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

    def _init_mods(self):
        if not self.enable_core_mods:
            return

        for mod in self._core_mods:
           mod.initialize(self)

    def _finalize_mods(self):
        if not self.enable_core_mods:
            return

        for mod in self._core_mods:
            mod.finalize(self)


    def run(self):
        """
        Run the simulation
        """
        
        self._init_mods()

        self.start_time = h.startsw()
        s_time = time.time()
        pc.timeout(0)
         
        pc.barrier()  # wait for all hosts to get to this point
        io.log_info('Running simulation for {:.3f} ms with the time step {:.3f} ms'.format(self.tstop, self.dt))
        io.log_info('Starting timestep: {} at t_sim: {:.3f} ms'.format(self.tstep, h.t))
        io.log_info('Block save every {} steps'.format(self.nsteps_block))

        h.finitialize(self.v_init * mV)           
        pc.psolve(h.tstop)            
        pc.barrier()
        
        self._finalize_mods()
        pc.barrier()

        end_time = time.time()
        sim_time = self.__elapsed_time(end_time - s_time)
        io.log_info('Simulation completed in {} '.format(sim_time))

    @classmethod
    def from_config(cls, config, network, set_recordings=True, enable_core_mods=True):
        sim = super(CoreBioSimulator, cls).from_config(config, network, set_recordings=True)
        sim.enable_core_mods = enable_core_mods
        sim.config = config

        sim_reports = reports.from_config(config)
        for report in sim_reports:
            mod = None
            if isinstance(report, reports.SpikesReport):
                mod = CoreSpikesMod(**report.params)

            if mod:
                sim._core_mods.append(mod)
            
        return sim