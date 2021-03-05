import COPASI
import pyabc
import basico
import petab
import basico_forward
import convert_petab
import os

class PetabModel(basico_forward.BasicoModel):

    def __init__(self, petab_yaml_file, out_dir='./out', max_t=0.1) -> None:
        self.yaml_file = os.path.abspath(petab_yaml_file)
        self.converter = convert_petab.PEtabConverter(
            petab_dir=os.path.dirname(self.yaml_file),
            model_name = os.path.basename(petab_yaml_file), 
            out_dir=out_dir
        )
        self.converter.convert()

        self.observableIds = self.converter.petab.observable_data.observableId.to_list()
        self.observables = [f'Values[{x}]' for x in self.observableIds]
        self.parameters = self.converter.petab.parameter_data.parameterId.to_list()
        super().__init__(self.converter.copasi_file, max_t=max_t, output=self.observables, use_numbers=True, method='hybridode45')


if __name__ == "__main__":
    MAX_T = 10
    model = PetabModel('./data/cr_petab/cr_petab.yml', max_t=MAX_T)
    print(model({'theta1': 0.09, 'theta2': 0.06, 'sigma': 0.5}))
    basico.save_model('out.cps')
