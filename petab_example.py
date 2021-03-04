""" This file just runs the code from: 

    https://pyabc.readthedocs.io/en/latest/examples/petab_yaml2sbml.html

    you'll need additional packages to run it, that are not included in the 
    requirements.txt file. As it requires some additional libraries, so before 
    installing the packages, ensure you have: 

    >>> sudo apt install libatlas-base-dev swig

    More installation instructions for AMICI here: 

    https://amici.readthedocs.io/en/latest/python_installation.html#amici-python-installation

    >>> pip install pyabc[petab,amici,yaml2sbml]


"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

import pyabc
import pyabc.petab
import amici.petab_import

pyabc.settings.set_figure_params('pyabc')  # for beautified plots

# folders
dir_in = 'data/'
dir_out = 'out/'
os.makedirs(dir_out, exist_ok=True)

import shutil
import yaml2sbml
import petab

#  check yaml file
model_name = 'cr'
yaml_file = dir_in + model_name + '.yml'
yaml2sbml.validate_yaml(yaml_file)

with open(yaml_file, 'r') as f:
    print(f.read())

# convert to petab
petab_dir = dir_out + model_name + '_petab/'
measurement_file = model_name + '_measurement_table.tsv'
yaml2sbml.yaml2petab(
    yaml_file, output_dir=petab_dir, sbml_name=model_name,
    petab_yaml_name='cr_petab.yml',
    measurement_table_name=measurement_file)

# copy measurement table over
_ = shutil.copyfile(
    dir_in + measurement_file, petab_dir + measurement_file)

petab_yaml_file = petab_dir + 'cr_petab.yml'
# check petab files


petab_problem = petab.Problem.from_yaml(petab_yaml_file)

# compile the petab problem to an AMICI ODE model
amici_dir = dir_out + model_name + '_amici'
if amici_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(amici_dir))
model = amici.petab_import.import_petab_problem(
    petab_problem, model_output_dir=amici_dir, verbose=False)

# the solver to numerically solve the ODE
solver = model.getSolver()

# import everything to pyABC
importer = pyabc.petab.AmiciPetabImporter(petab_problem, model, solver)

# extract what we need from the importer
prior = importer.create_prior()
model = importer.create_model()
kernel = importer.create_kernel()

print(model(importer.get_nominal_parameters()))

print(prior)

sampler = pyabc.MulticoreEvalParallelSampler()

temperature = pyabc.Temperature()
acceptor = pyabc.StochasticAcceptor()

abc = pyabc.ABCSMC(model, prior, kernel,
                   eps=temperature,
                   acceptor=acceptor,
                   sampler=sampler,
                   population_size=100)
# AMICI knows the data, thus we don't pass them here
abc.new(pyabc.create_sqlite_db_id(), {})
h = abc.run()

pyabc.visualization.plot_kde_matrix_highlevel(
    h, limits=importer.get_bounds(),
    refval=importer.get_nominal_parameters(), refval_color='grey',
    names=importer.get_parameter_names(),
)

plt.savefig('./out/orig_petab.png')