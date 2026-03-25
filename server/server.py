import os
import flwr as fl
from flwr.server.strategy import FedProx


def weighted_average(metrics):
    total = sum(num for num, _ in metrics)
    f1_agg = sum(num * m["f1"] for num, m in metrics) / total
    return {"f1": f1_agg}


strategy = FedProx(
    fraction_fit=1.0,
    min_fit_clients=4,
    min_available_clients=4,
    evaluate_metrics_aggregation_fn=weighted_average,
    proximal_mu=0.1,
)

fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=10),
    strategy=strategy,
    certificates=(
        open("/certs/ca.crt",     "rb").read(),
        open("/certs/server.crt", "rb").read(),
        open("/certs/server.key", "rb").read(),
    ),
)
