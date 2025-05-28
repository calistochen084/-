#import
import matplotlib.pyplot as plt
import numpy as np
import sys

#load data
def load_data(path, instance_id):
    '''
    Parameters
    ----------
    path：str
        实例文件路径
    instance_id: int
        实例id

    :return:
    -------
    coord : list within array
        节点坐标
    demand : list
        客户需求量
    vehicle_cap : int
        货车最大载荷
    num_customer : int
        服务者数量
    num_vehicle : int
        车的数量
    '''

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    #找到所有实例位置
    instance_indices = [i for i, line in enumerate(lines) if line.strip().startswith("instance")]

    #确定当前获取实例的位置
    start_id = instance_indices[instance_id]
    end_id = instance_indices[instance_id+1] if instance_id+1 < len(instance_indices) else len(lines)
    instance_lines = lines[start_id : end_id]

    #把当前实例打平成单词列表
    vrp_list = [word for line in instance_lines for word in line.split()]
    # print(vrp_list)

    vrp_coord = vrp_list[vrp_list.index("NODE_COORD_SECTION")+1 : vrp_list.index("DEMAND_SECTION")]
    vrp_demand = vrp_list[vrp_list.index("DEMAND_SECTION")+1 : ]
    vehicle_cap = int(vrp_list[vrp_list.index("CAPACITY")+2])
    num_vehicle = int(vrp_list[vrp_list.index("instance")+3])


    coord, demand = [], []

    for i in range(int(len(vrp_coord)/3)):
        coord.append(np.array([int(vrp_coord[3*i+1]), int(vrp_coord[3*i+2])]))
        demand.append(int(vrp_demand[2*i+1]))
    num_customer = i
    return coord, demand, vehicle_cap, num_customer, num_vehicle

#--------可视化----------#
#画箭头
def Plt_arrow(x_begin, y_begin, x_end, y_end, color):
    plt.arrow(x_begin,y_begin,x_end-x_begin,y_end-y_begin,
              #length_include_head=True,         #增加的长度包括箭头的部分
              head_width=1, head_length=1, fc = color, ec =color)

#连接节点
def Route(x0, y0, coords, plt, color):
    # Plt_arrow(x0, y0, car[0][0], car[0][1], color)  #Depot指向路径起点
    Plt_arrow(x0, y0, coords[0][0], coords[0][1], color)

    # for i in range(len(car)-1):
    #     Plt_arrow(car[i][0], car[i][1], car[i+1][0], car[i+1][1],
    #               color)
    # Plt_arrow(car[-1][0], car[-1][1], x0, y0, color)  #路径终点指向Depot
    for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
        Plt_arrow(x1, y1, x2, y2, color)
    Plt_arrow(coords[-1][0], coords[-1][1], x0, y0, color)


#退火过程可视化
def Plot_Obj(obj_list, path, instance_id):
    plt.rcParams['font.sans-serif'] = ['SimHei']  #中文显示
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(np.arange(1, len(obj_list)+1), obj_list)
    plt.xlabel("Iterations") #坐标轴
    plt.ylabel("Obj_Value")
    plt.grid()
    plt.xlim(1, len(obj_list)+1)
    plt.savefig(path + f'_iter_{instance_id}.png')

#路径图可视化
def Draw_Map(coord, cars, path, instance_id):
    x = [i[0] for i in coord]
    y = [i[1] for i in coord]
    colors = ['lime','cyan','blueviolet','fuchsia','orange','blue',
    'darkgreen','chocolate','slategray','gold','grey','peru',
    'darkslategray','indigo','navy']
    plt.figure()
    plt.xlabel('x')
    plt.ylabel('y')
    for m,a in enumerate(cars):
        if not a: continue
        b = []
        # for i in range(len(a)):
        #     b.append([])
        # k = 0
        # for j in range(len(a)):
        #     b[k].append(x[a[j]])
        #     b[k].append(y[a[j]])
        #     k += 1
        # Route(x[0], y[0], b, plt, colors[m])
        coords = [(x[n], y[n]) for n in a]
        Route(x[0], y[0], coords, plt, colors[m])
    plt.scatter(x, y, color='k', marker='o', label='Location')
    plt.scatter(x[0], y[0], s=500, color='r', marker='*', label='Center')
    plt.legend()
    plt.savefig(path + f'_routes_{instance_id}.png')
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法： python script.py [instance_id]")
    else:
        instance_id = int(sys.argv[1])
        coord, demand, vehicle_cap, num_vehicle, num_customer = load_data("./CVRP-test-5.txt", instance_id)
        print(f"coord：{coord}\ndemand:{demand}\nvehicle_cap:{vehicle_cap}\n"
              f"num_vehicle:{num_vehicle}\nnum_cus:{num_customer}")