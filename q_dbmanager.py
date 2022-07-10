import logging

from selection.algorithms.qtable.link_database import ManageDB
from selection.cost_evaluation import CostEvaluation
from selection.dbms.hana_dbms import HanaDatabaseConnector
from selection.dbms.postgres_dbms import PostgresDatabaseConnector

DBMSYSTEMS = {"postgres": PostgresDatabaseConnector, "hana": HanaDatabaseConnector}


class QDBManager(ManageDB):
    def __init__(self, ):
        ManageDB.__init__(self)
        self.database_connector = None
        self.db_system = 'postgres'
        self.cost_evaluation = None
        self.index_bit_dict = {}
        self.bit_index_dict = {None}
        self.workload = None
        self.if_storage_counts = True


    def getSel(self, query, index):
        return self.cost_evaluation.get_selectivity(query, index)

 
    def getCost(self, state, action = None, cost_estimation="whatif", relevant=True):
        assert (cost_estimation == "whatif" or cost_estimation == "actual_runtimes")
        flag = None
        if action:
            indexes, flag = self.action_to_index(action, state)
        else:
            indexes = self.str_to_index(state)

        return self.get_cost_with_indexes(indexes, cost_estimation, relevant,flag)


    def get_cost_with_indexes(self, indexes, cost_estimation="whatif", relevant=True,flag = None):
        old_estimation = self.cost_evaluation.cost_estimation
        self.cost_evaluation.cost_estimation = cost_estimation
        if relevant:
            cost = self.cost_evaluation.calculate_cost(self.workload, indexes, self.if_storage_counts)
        else:
            init_cost = self.cost_evaluation.calculate_cost(self.workload, [], self.if_storage_counts)
            delta_cost = 0
            for i in range(len(indexes)):
                delta_cost += flag[i] * (init_cost - self.cost_evaluation.calculate_cost(self.workload, [indexes[i]],
                                                                  self.if_storage_counts))
            cost = delta_cost #+ init_cost
        self.cost_evaluation.cost_estimation = old_estimation

        return cost

  
    def _simulate_and_evaluate_cost(self, workload, indexes):
        cost = self.cost_evaluation.calculate_cost(workload, indexes, store_size=True)
        return round(cost, 2)

 
    def setup_db_connector(self, database_connector):
        self.database_connector = database_connector
        self.cost_evaluation = CostEvaluation(database_connector)



    def setup_connector_and_evaluation(self, database_connector, cost_evaluation):
        self.database_connector = database_connector
        self.cost_evaluation = cost_evaluation


    def setup_index_bit_map(self, index_bit_dict, bit_index_dict):
        self.index_bit_dict = index_bit_dict
        self.bit_index_dict = bit_index_dict


    def setup_workload(self, workload):
        self.workload = workload

  
    def str_to_index(self, bit_str):
        index_list = []
        for i in range(1, len(bit_str) + 1):
            if bit_str[-i] == '1':
                if (i - 1) in self.bit_index_dict:
                    index_list.append(self.bit_index_dict[i - 1])
        return index_list


    def action_to_index(self, action, bit_str):
        index_list, flag = [], []
        for i in range(0, len(bit_str)):
            if action[i] == '1':
                index_list.append(self.bit_index_dict[i])
                if bit_str[i] == '0':
                    flag.append(1)
                else:
                    flag.append(-1)
              
        return index_list, flag
