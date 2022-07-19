# AMDRL: A Constraint-guided Dynamic Reinforcement Learning for Index Selection

## Environment Setup

Setup:
* Install Just
  * Postgres 12.06
  * VMware 16.2
  * Python 3.8


## Dataset

Download the real-world datasets and workloads from [TPCH](https://www.tpc.org/tpch/) and [TPCDS](https://www.tpc.org/tpcds/).

We utilize the SF = 10 to implement our experiments.

## AMDRL

There exist four main classes for achieving AMDRL. RL_brain.py achieves the agent construction and training. Link_database.py completes the operations of the in-database Q_table. Model.py designs the constraints for AMDRL. Q_dbmanager.py is responsible for estimating the index configuration.


