#------导入库--------#
import sys

import numpy as np
import math
import time
import random
import copy
#----导入工具库-------#
import utils
import optimization

def Run(path, instance_id):
    # 读取数据
    coord, demand, vehicle_cap, num_customer, num_vehicle = utils.load_data(path, instance_id)
    Distance = optimization.getDistance(coord)

    # 参数设置
    sa = optimization.SA(T0=500, Te=0.005, delta_T=0.8)
    Tk = sa.T0
    Te = sa.Te
    delta_T = sa.delta_T

    # 初始化解
    sol = optimization.Sol()
    sol.nodes_seq = list(range(1, num_customer + 1))
    sol.nodes_seq = optimization.Initial_Sol(sol.nodes_seq, demand, vehicle_cap, num_vehicle)  # 随机初始化
    num_vehicle, sol.routes, sol.obj = optimization.Cal_Obj(
        sol.nodes_seq, vehicle_cap, demand, Distance,max_vehicle=num_vehicle
    )
    sa.best_sol = sol
    sa.history_best_obj = [sol.obj]

    # 邻域算子
    actionList = optimization.Create_Actions(num_customer)

    # 内循环长度 = 邻域操作数
    num_Tk = len(actionList)

    while Tk >= Te:
        for i in range(num_Tk):
            new_sol = optimization.Sol()  # 当前解为初始解
            new_sol.nodes_seq = optimization.Do_Action(
                sol.nodes_seq,
                actionList[random.randint(0, num_Tk - 1)]
            )
            num_vehicle, new_sol.routes, new_sol.obj = optimization.Cal_Obj(
                new_sol.nodes_seq, vehicle_cap, demand, Distance,
                max_vehicle=num_vehicle
            )
            delta_f = new_sol.obj - sol.obj

            if delta_f < 0 or math.exp(-delta_f / Tk) > random.random():
                sol = copy.deepcopy(new_sol)

            if sol.obj < sa.best_sol.obj:
                sa.best_sol = copy.deepcopy(sol)

        # 降温策略
        if delta_T < 1:  # 比例退火
            Tk = Tk * delta_T
        else:  # 线性退火
            Tk = Tk - delta_T

        # 记录历史最优解
        sa.history_best_obj.append(sa.best_sol.obj)
        print("temperature: %s, local_obj: %s best_obj: %s" %
              (Tk, sol.obj, sa.best_sol.obj))

    utils.Plot_Obj(sa.history_best_obj, "./output/Obj/Obj", instance_id)
    utils.Draw_Map(coord, sa.best_sol.routes, "./output/Map/Map", instance_id)

if __name__ == "__main__":
    start = time.time()
    Run(r"D:\北理\课程\1320231100陈昱丞\code\data\CVRP-test-5.txt", int(sys.argv[1]))
    end = time.time()
    print("运行时长为:", end - start)