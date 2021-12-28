This file contains the info required in addition to overleaf to parse the code.
Here we summarize files organized by type: core, helper, peripheral, and test.



CORE: model, crc_models, simulate, branching_optimizer

model encodes what it means to be and simulate a branching process.

crc_models instantiates (as subclasses of model) specific branching
processes we use in this project.

simulate analyses the biological stretching data and for each of a few test
models simulates analogous data (to csv files). It compares analytics of the
test model data to the biological data.

branching_optimizer implements an MLE optimization to determine
optimal parameters for a branching process model given data. Written to be
flexible but may require adjustment based on what type of data we have. 
Requires some implementation still in order to work with csvs.



HELPER: bio_data_convert, csv_handler, dynamic, graph, visual_handler.

bio_data_convert takes the biological data we were given and converts it
to the format we use in our simulations, which should allow for easier
parameter optimization

csv_handler writes and reads data to and from csv files.

graph and visual_handler help with creating visualizations of data.

dynamic takes a function and caches values to decrease redundant calculations
at the cost of memory. Currently not in use but implementing in 
branching_optimizer will allow for far more generalizable code while 
maintaining fast runtimes. Also, compared to current branching_optimizer 
implementation it should not use more memory.



PERIPHERAL: deterministic_gaussian_optimizer

deterministic_gaussian_optimizer optimizes parameters for a simplified but
inaccurate version of the model, where the behavior of a branching process
is estimated to be the average behavior times a normal distribution with
mean 1, constant variance (where different population types have independent
distributions, even within the same branching process.) It is a disappointment
but still potentially useful due to achieving OK results while allowing for
easy generalization to messier data. If used seriously, may need some serious
work done.



TEST: whiteboard

Do what you want with this. I have been using it to help me understand libraries
and objects that I dont often work with, e.g., csv, scipy, dictionaries.
