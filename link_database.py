import random
import psycopg2


class ManageDB:
    def __init__(self):
        self.conn = psycopg2.connect("dbname={}".format("qlearning"))
        # self.cost_evaluation = CostEvaluation(self.conn)


    def create_qtable(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE QTABLE \
               (State TEXT, \
               act_qvalue JSONB NOT NULL);")
        print("Table created successfully")
        self.conn.commit()


    def del_qtable(self):
        cursor = self.conn.cursor()
        cursor.execute("drop table if exists QTABLE;")
        print("Table delated successfully")
        self.conn.commit()


    def update_qvalue(self, state, action, value):
        cursor = self.conn.cursor()
        change_sql = '''
                    with change as ( 
                          select ('{'||index-1||',value}')::text[] as path 
                          from QTABLE 
                               ,jsonb_array_elements(act_qvalue) with ordinality arr(rightnow, index) 
                          where rightnow->>'action' = ''' + "'" + action + "'" + '''
                                and State = ''' + "'" + state + "'" + ''' 
                    ) 
                    update QTABLE 
                        set act_qvalue = jsonb_set(act_qvalue, change.path, ''' + "'" + str(value) + "'" + ''', false) 
                        from change 
                        where State = ''' + "'" + state + "'" + ''';
                    '''
        cursor.execute(change_sql)
        self.conn.commit()

    def update_state(self, state_before, state_after, action):
        cursor = self.conn.cursor()
        change_sql = '''
                    with change as ( 
                          select ('{'||index-1||',next_state}')::text[] as path 
                          from QTABLE 
                               ,jsonb_array_elements(act_qvalue) with ordinality arr(rightnow, index) 
                          where rightnow->>'action' = ''' + action + '''
                                and State = ''' + state_before + ''' 
                    ) 
                    update QTABLE 
                        set act_qvalue = jsonb_set(act_qvalue, change.path, ''' + state_after + ''', false) 
                        from change 
                        where State = ''' + state_before + ''';
                    '''
        cursor.execute(change_sql)
        self.conn.commit()

值
    def get_qvalue(self, state, action):
        cursor = self.conn.cursor()
        get_sql = '''
                  select r->>'value'
                  from QTABLE q, jsonb_array_elements(q.act_qvalue) r
                  where q.State = ''' + "'" + state + "'" + ''' and r->>'action' = ''' + "'" + action + "'" + ''' 
                  '''
        cursor.execute(get_sql)
        rows = cursor.fetchall()
        for row in rows:
            return float(row[0])


    def get_maxqvalue(self, state):
        cursor = self.conn.cursor()
        get_sql = '''
                      select r->>'action', r->>'value'
                      from QTABLE q, jsonb_array_elements(q.act_qvalue) r
                      where q.State = ''' + "'" + state + "'" + '''
                      '''
        cursor.execute(get_sql)
        rows = cursor.fetchall()
        a = []
        v = []
        if len(rows) == 0:
            return ['', 0]
        else:
            for row in rows:
                a.append(row[0])
                v.append(float(row[1]))
            Max = max(v)
            choosebox = []
            for n in range(len(v)):
                if v[n] == Max:
                    choosebox.append(n)
            # print("Max:",Max, "choosebox:", choosebox)
            choose = random.choice(choosebox)
            return [a[choose], Max]


    def check_state_exist(self, state):
        cursor = self.conn.cursor()
        cursor.execute("select State from QTABLE")
        rows = cursor.fetchall()
        stor_state = []
        for row in rows:
            stor_state.append(row[0])

        if state not in stor_state:
            insert_sql = '''
                        INSERT INTO QTABLE (State, act_qvalue) 
                        VALUES (''' + "'" + state + "'" + ''', 
                                    '[]'
                                );
                        '''
            cursor.execute(insert_sql)
            self.conn.commit()


    def check_action_exist(self, state, action):
        cursor = self.conn.cursor()
        get_sql = '''
                              select r->>'action'
                              from QTABLE q, jsonb_array_elements(q.act_qvalue) r
                              where q.State = ''' + "'" + state + "'" + '''
                              '''
        cursor.execute(get_sql)
        self.conn.commit()
        rows = cursor.fetchall()
        v = []
        for row in rows:
            v.append(row[0])
        flag = 0
        if action not in v:
            flag = 1
        return flag


    def insert_action(self, state, action, value, state_new):
        cursor = self.conn.cursor()
        sql_str = '''update QTABLE 
               set act_qvalue = act_qvalue || '{\"action\": \"''' + action + '''\", 
                                                \"next_state\": \"''' + state_new + '''\", 
                                                \"value\": ''' + str(value) + '''}'::jsonb
               where State = ''' + "'" + state + "'" + ''';                                         
            '''
        cursor.execute(
            sql_str
        )
        self.conn.commit()




        return

    def show_table(self):
        cursor = self.conn.cursor()
        get_sql = '''
                  select * from QTABLE      
                  '''
        cursor.execute(get_sql)
        rows = cursor.fetchall()
        for row in rows:
            print(row)


if __name__ == "__main__":

    manager = ManageDB()
    manager.del_qtable()
    manager.create_qtable()

    s1 = "0010011001"
    manager.check_state_exist(s1)
    s2 = "00"
    manager.check_state_exist(s2)
    s3 = "0"
    manager.check_state_exist(s3)
    manager.check_state_exist(s2)


    f = manager.check_action_exist("00", "01")
    print(f)
    manager.insert_action("00", "01", 10, "01")
    manager.show_table()
    manager.insert_action("00", "11", -2, "11")
    manager.show_table()
    f = manager.check_action_exist("00", "01")
    print(f)
    
    print(manager.get_maxqvalue("0"))
    print(manager.get_maxqvalue("00"))
    print(manager.get_qvalue("00", "11"))

    manager.insert_action("0010011001", "0110011110", 1.3, "0100000111")

