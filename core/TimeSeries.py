from typing import List, Dict

import numpy as np
import sys

from core.Prediction import Prediction


class TimeSeries:
    def __init__(self, **kwargs):
        self.predictions = []  # List[Prediction]
        self.__parse_kwargs__(**kwargs)

    def __parse_kwargs__(self, **kwargs):
        def __extract_values__(values):
            if isinstance(values, str):
                return [float(x) for x in values.split(" ")]
            elif isinstance(values, List):
                return [float(x) for x in values]
            else:
                RuntimeError("Values class not recognized. {}".format(values))
                sys.exit(-2)

        self.forecasting_window = int(kwargs.pop("forecasting_window", 1))
        self.minimum_observations = int(kwargs.pop("minimum_observations", 1))

        self.observations = __extract_values__(kwargs.pop("observations", []))

        predicted_values = __extract_values__(kwargs.pop("predicted_values", []))
        predicted_stddev = __extract_values__(kwargs.pop("predicted_stddev", []))
        assert len(predicted_values) == len(predicted_stddev), \
            "The length of predicted values ({}) and of the stddev ({}) are not equal.".format(
                len(predicted_values), len(predicted_stddev))
        self.predictions = [Prediction(predicted_values[i], predicted_stddev[i])
                            for i in np.arange(len(predicted_values))]

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __type_checks__(self):
        assert isinstance(self.predictions, List[Prediction]), "prediction attribute must be of type List[Prediction]"

    def __length_checks__(self):
        assert len(self.observations) == len(self.predictions), \
            "The number of observations ({}) and predictions ({}) do not match.".format(
                len(self.observations), len(self.predictions))

    def to_csv(self) -> Dict:
        self.__type_checks__()
        self.__length_checks__()

        return {
            "observations": " ".join(str(x) for x in self.observations),
            "predicted_values": " ".join(str(x.value) for x in self.predictions),
            "predicted_stddev": " ".join(str(x.stddev) for x in self.predictions),
            **{key: self.__getattribute__(key) for key in self.__dict__.keys() - {"observations", "predictions"}}
        }

    def estimation_errors(self) -> List:
        self.__type_checks__()
        self.__length_checks__()

        return [float(self.predictions[i].value - self.observations[i])
                for i in np.arange(self.minimum_observations, len(self.observations))]

    def estimation_errors_area(self) -> float:
        return np.asscalar(np.sum(self.estimation_errors()))

    def under_estimation_errors(self) -> List:
        return [float(x) for x in self.estimation_errors() if x < 0]

    def under_estimation_errors_area(self) -> float:
        return np.asscalar(np.sum(self.under_estimation_errors()))

    def over_estimation_errors(self) -> List:
        return [float(x) for x in self.estimation_errors() if x > 0]

    def over_estimation_errors_area(self) -> float:
        return np.asscalar(np.sum(self.over_estimation_errors()))

    def estimation_percentage_errors(self) -> List:
        self.__type_checks__()
        self.__length_checks__()

        return [float(np.abs(1 - self.predictions[i].value / self.observations[i]) * 100)
                for i in np.arange(self.minimum_observations, len(self.observations))]

    def rmse(self) -> float:
        return np.sqrt(np.mean([np.power(x, 2) for x in self.estimation_errors()]))

    def has_one_under_estimation_error(self) -> bool:
        return len(self.under_estimation_errors()) > 0