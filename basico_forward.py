import COPASI
import pyabc
import basico

class BasicoModel:
    __name__ = "BasicoModel"

    def __init__(self, sbml_file, max_t=10, output=None, changes=None) -> None:
        """
        """
        self.sbml_file = sbml_file
        self.output = output
        if self.output is None:
            # assume X Y for now, as thats what is in the example
            self.output = ['X', 'Y']

        self.dm = basico.load_model(sbml_file)
        
        # many sbml models do not define realistic units, and 
        # since we compute in particle numbers, we usually do not run
        # for gazillion particles, so set substance unit to 1
        basico.set_model_unit(substance_unit='1', model=self.dm)
        
        self.max_t = max_t

        # allow to override parameters
        if changes is not None: 
            self.apply_parameters(changes)

    def __call__(self, par):
        """Calls the time course and returns the selected result. 

        sets the method to gibson bruck, automatic step size
        """
        self.apply_parameters(par)
        tc = basico.run_time_course(self.max_t, model=self.dm, method='stochastic', automatic=True, use_seed=False).reset_index()
        return {
            "t": tc.Time.to_numpy(), 
            "X": tc[self.output].to_numpy()
        }    

    def apply_parameters(self, par):
        """ Sets the parameters of the model

        param par: | dictionary of parameter name, value entries. Local parameters are assumed to be named something like
                   | `(reaction).local_parameter`. where `reaction` is the name of the reaction, and `local_parameter` the 
                   | local parameter. Otherwise the parameter is expected to be a global one. 
        """
        for key in par.keys():
            if '(' in key: 
                basico.set_reaction_parameters(key, value=par[key], model=self.dm)
            else:
                basico.set_parameters(key, initial_value=par[key], model=self.dm)


if __name__ == '__main__':
    print(f'Using COPASI: {COPASI.__version__}')
    print(f'Using pyabc: {pyabc.__version__}')
    print(f'Using basico: {basico.__version__}')

    model = BasicoModel('./data/brusselator-model.xml')

    obs = model({"rate": 30})

