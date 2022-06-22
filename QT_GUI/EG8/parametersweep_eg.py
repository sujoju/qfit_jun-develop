import numpy as np
import scqubits as scq

class ParameterSweep_EG():
    def __init__(self) -> None:
        self.hilbertspace_default_values = {
            "resonator": {
                "E_osc": 4.5,
                "l_osc": 0.0,
                "truncated_dim": 4,
                "id_str": "resonator"
            },
            "tmon1": {
                "EJmax": 40.0,
                "EC": 0.2,
                "d": 0.1,
                "flux": 0.23,
                "ng": 0.3,
                "ncut": 40,
                "truncated_dim": 3,
                "id_str": "tmon1"
            },
            "tmon2": {
                "EJmax": 15.0,
                "EC": 0.15,
                "d": 0.2,
                "flux": 0.0,
                "ng": 0.0,
                "ncut": 30,
                "truncated_dim": 3,
                "id_str": "tmon2"
            },
            "g1": 0.1,
            "g2": 0.2
        }
        self.parametersweep_defaults = {
            "ng": {"min": -0.5, "max": 0.5}
        }
        self.parametersweep_default_values = {
            "num_sample": 21,
            "area_ratio": 1.2
        }
        test_values = {
            "ng": 0.4
        }
        sweep = "ng"

        self.tmon1 = None 
        self.tmon2 = None 
        self.resonator = None
        self.hilbertspace = None 
        self.parametersweep = None
        self.noisy_data = None

        self.create_hilbertspace(self.hilbertspace_default_values)
        self.create_parametersweep(5)
        self.create_noisy_data(self.parametersweep, sweep, test_values)

    # function that defines how Hilbert space components are updated
    def update_hilbertspace(self, ng):
        # self.tmon1.flux = flux
        # self.tmon2.flux = self.parametersweep_default_values["area_ratio"] * flux
        self.tmon2.ng = ng

    def create_hilbertspace(self, subsys_values):
        self.tmon1 = scq.TunableTransmon(**subsys_values["tmon1"])
        self.tmon2 = scq.TunableTransmon(**subsys_values["tmon2"])
        self.resonator = scq.Oscillator(
            **subsys_values["resonator"])

        self.hilbertspace = scq.HilbertSpace(
            [self.tmon1, self.tmon2, self.resonator])

        g1 = self.hilbertspace_default_values["g1"]
        g2 = self.hilbertspace_default_values["g2"]

        self.hilbertspace.add_interaction(
            g_strength=g1,
            op1=self.tmon1.n_operator,
            op2=self.resonator.creation_operator,
            add_hc=True,
            id_str="tmon1-resonator"
        )

        self.hilbertspace.add_interaction(
            g_strength=g2,
            op1=self.tmon2.n_operator,
            op2=self.resonator.creation_operator,
            add_hc=True,
            id_str="tmon2-resonator"
        )

    def create_parametersweep(self, evals):
        paramvals_by_name = {}
        for param, param_dict in self.parametersweep_defaults.items():
            param_min = param_dict["min"]
            param_max = param_dict["max"]
            num_sample = self.parametersweep_default_values["num_sample"]
            param_vals = np.linspace(param_min, param_max, num_sample)
            paramvals_by_name[param] = param_vals

        self.parametersweep = scq.ParameterSweep(
            hilbertspace=self.hilbertspace,
            paramvals_by_name=paramvals_by_name,
            update_hilbertspace=self.update_hilbertspace,
            evals_count=evals
        )
    
    def create_noisy_data(self, parametersweep, sweep, default_values):
        model_data = parametersweep["evals"]
        for param, value in default_values.items():
            if param != sweep:
                model_data = model_data[param:value]
        self.noisy_data = model_data + 0.2 * \
            np.random.normal(size=model_data.shape)
        # self.noisy_data_x = parametersweep.param_info[sweep]