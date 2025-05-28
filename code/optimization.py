#------导入库--------#
import numpy as np
import math
import time
import random
import copy
#----导入工具库-------#
import utils

#-------定义类-------#
class Sol():
    '''
    nodes_seq     #需求节点seq_no有序排列集合，对应TSP的解
    obj           #目标值
    routes        #车辆路径集合，对应CVPR的解
    '''
    def __init__(self):
        self.node_seq = None
        self.obj = None
        self.route = None

class SA():
    '''
    best_sol                 全局最优解，值类型为Sol()
    history_best_sol         每一代历史最优解
    T0                       初始温度
    Te                       终止温度
    '''
    def __init__(self, T0=300, Te=0.01, delta_T=0.95):
        self.best_sol = None
        self.history_best_sol = None
        self.T0 = T0
        self.Te = Te
        self.delta_T = delta_T

#------模拟退火------#

#计算距离矩阵
def getDistance(coord):
    n = len(coord)
    distance = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            distance[i, j] = np.linalg.norm(coord[i] - coord[j])
            distance[j, i] = distance[i, j]
    return distance


#随机生成初始解
def Initial_Sol(node_seq, demand, vehicle_cap, M):
    """
    生成一个按照固定车辆数 M、且保证不超载的初始解 node_seq。

    参数
    ----
    node_seq    : 原始节点列表 [1,2,...,n]
    demand      : 各节点需求
    vehicle_cap : 单车容量
    M           : 固定车辆数

    返回
    ----
    一个新的 node_seq，使得用 Cal_Obj 分割时 num_vehicle <= M。
    """
    # 随机打乱原始客户顺序
    seq = node_seq.copy()
    random.seed(1)
    random.shuffle(seq)

    # 准备 M 辆车的“空”路径和剩余容量
    routes = [[] for _ in range(M)]
    remain = [vehicle_cap] * M

    # 贪心分配：每个客户给第一个能装下它的车辆
    for cust in seq:
        for i in range(M):
            if remain[i] >= demand[cust]:
                routes[i].append(cust)
                remain[i] -= demand[cust]
                break

    # 展平 routes → node_seq
    new_seq = []
    for r in routes:
        new_seq.extend(r)
    return new_seq



#计算总距离
def Cal_Obj(node_seq, vehicle_cap, demand, Distance, max_vehicle, penalty=1e6):
    """
    node_seq: 客户访问顺序
    max_vehicle: 固定要用的车辆数 M
    penalty:    超过车辆数时的惩罚系数
    """
    vehicle_routes = []
    route = []
    remained_cap = vehicle_cap
    total_dist = 0
    #—— 1. 按容量切分路径 ——#
    for node in node_seq:
        if remained_cap >= demand[node]:
            route.append(node)
            remained_cap -= demand[node]
        else:
            vehicle_routes.append(route)
            route = [node]
            remained_cap = vehicle_cap - demand[node]
    vehicle_routes.append(route)

    num_vehicle = len(vehicle_routes)

    #—— 2. 计算各条路径距离 ——#
    for rt in vehicle_routes:
        # depot→第一个客户
        total_dist += Distance[0, rt[0]]
        # 客户间
        for i in range(len(rt)-1):
            total_dist += Distance[rt[i], rt[i+1]]
        # 最后一个客户→depot
        total_dist += Distance[rt[-1], 0]

    #—— 3. 处理车辆数不等于 M 的情况 ——#
    if num_vehicle > max_vehicle:
        # 超出车辆数，直接大惩罚
        total_dist += penalty * (num_vehicle - max_vehicle)
    elif num_vehicle < max_vehicle:
        # 少用车辆时，补空路径（不改变总距离，只为了输出格式统一）
        for _ in range(max_vehicle - num_vehicle):
            vehicle_routes.append([])

    return num_vehicle, vehicle_routes, total_dist

#邻域算子
def Create_Actions(n):
    actionList = []
    for i in range(n-1):
        for j in range(i+1, n):
            actionList.append([1, i, j])  #1-交换算子
    for i in range(n-1):
        for j in range(i+1, n):
            if abs(i - j) > 2:
                actionList.append([2, i, j]) #2-逆转算子
    return actionList

#生成邻域
def Do_Action(nodes_seq, action):
    p = nodes_seq
    if action[0] == 1:  # 执行交换操作
        q = p.copy()
        q[action[1]] = p[action[2]]
        q[action[2]] = p[action[1]]
    if action[0] == 2:  # 执行逆转操作
        q = p.copy()
        if action[1] < action[2]:
            reversion = p[action[1]:action[2] + 1]
            reversion.reverse()
            q[action[1]:action[2] + 1] = reversion
        else:
            reversion = p[action[2]:action[1] + 1]
            reversion.reverse()
            q[action[2]:action[1] + 1] = reversion
    return q

