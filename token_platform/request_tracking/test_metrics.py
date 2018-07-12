from tests.test_utils import BaseTestClass

from request_tracking.metrics import metric
from router import ROUTER


class TestMetricsName(BaseTestClass):

    def test_metrics_name(self):
        ROUTER_KEY = []
        for key, value in ROUTER.items():
            if key == 'root' or key == 'metrics':
                continue
            key_upper = key.upper()
            key_upper = key_upper.replace('-', '_')
            for k, v in value.items():
                if k != 'url':
                    resource_name = f'{k}_{key_upper}'
                    ROUTER_KEY.append(resource_name)

        assert len(metric) == len(ROUTER_KEY)

        for item in ROUTER_KEY:
            assert item in metric
