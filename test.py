from neuron import h
from neuron.units import ms, mV
from neuron import coreneuron
coreneuron.gpu = False
import matplotlib.pyplot as plt

h.load_file('stdrun.hoc')
h.load_file('feng_PN_cells.hoc')

# setup model
cell = h.PN_C()

ic = h.IClamp(cell.soma[0](.5))
ic.delay = 5
ic.dur = 30
ic.amp = 0.3


# make sure to enable cache efficiency
h.cvode.cache_efficient(1)
h.nrnmpi_init()

pc = h.ParallelContext()
pc.set_gid2node(pc.id()+1, pc.id())
myobj = h.NetCon(cell.soma[0](0.5)._ref_v, None, sec=cell.soma[0])
pc.cell(pc.id()+1, myobj)

coreneuron.verbose = 3
h.stdinit()
h.tstop=100
corenrn_all_spike_t = h.Vector()
corenrn_all_spike_gids = h.Vector()
pc.spike_record(-1, corenrn_all_spike_t, corenrn_all_spike_gids)
t = h.Vector().record(h._ref_t)
v = h.Vector().record(cell.soma[0](0.5)._ref_v)
h.finitialize(-65 * mV)
coreneuron.enable = True
#h.continuerun(h.tstop) #runs with normal neuron sim
pc.psolve(h.tstop)  #runs using core neuron sim


plt.plot(t,v)
plt.savefig("test.png")
