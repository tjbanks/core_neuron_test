# core_neuron_test
## to install core neuron

I built my env with python 3.8
```
pip install neuron-nightly
```
or 

build with cmake using the commands **best way to install core neuron is using cmake**

*load a version of MPI this happens to be the one on the lab server*
```
module load mpich-x86_64-nopy

git clone https://github.com/neuronsimulator/nrn
cd nrn
mkdir build
cd build

cmake .. \
 -DNRN_ENABLE_INTERVIEWS=OFF \
 -DNRN_ENABLE_RX3D=OFF \
 -DNRN_ENABLE_CORENEURON=ON\
 -DCORENRN_ENABLE_NMODL=ON \
 -DCMAKE_INSTALL_PREFIX=$HOME/install
 
 cmake --build . --parallel 8 --target install
 ```
Then make sure to set path
```
export PYTHONPATH=$HOME/install/lib/python:$PYTHONPATH
export PATH=$HOME/install/bin:$PATH
```
# Files

core_neuron_example.py - example from the core neuron github

test.py - A test to see if i could simulate one of our cells in core neuron

second_test.py - A test to see if i could use one of our labs synapses in core neuron

bmtk_build.py - builds simple BMTK netowrk

run_bmtk.py - runs a bmtk network with core neuron you need the bmtk from my [GitHub](https://github.com/GregGlickert/bmtk) installed for it to run

reports.py - Where code for voltage recording lives

data_check.py - simple script to generate membrane voltage plot

**When compiling mod files you should not compile the mod files in the components/mechanisms folder core neuron does not read those correctly and it casues a strange error and says there are more cells then actually in sim. Just compile modfiles in base directory**
