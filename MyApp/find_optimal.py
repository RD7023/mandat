import pandas as pd
import numpy as np
from itertools import product

# ------GLOBAL VARIABLES-----------

no_of_dill = None
no_of_vyb_arr = None
conn_arr = None
mandat_min = None
mandat_max = None
okrug_min = None
okrug_max = None
mandat_all = 22

connections = None
people = None
dil_unique = None


# ----------------------------


def unpack_data(data):
    global no_of_dill, no_of_vyb_arr, \
        conn_arr, mandat_min, \
        mandat_max, okrug_min, okrug_max
    no_of_dill = int(data["noOfDill"])
    no_of_vyb_arr = data["noOfVybArr"]
    conn_arr = data["connArr"]
    mandat_min = int(data["minMandat"])
    mandat_max = int(data["maxMandat"])
    okrug_min = int(data["minOkr"])
    okrug_max = int(data["maxOkr"])


def generate_df():
    generate_people()
    generate_conn()


def generate_people():
    global people
    dill_arr = [i for i in range(1, int(no_of_dill) + 1)]
    people = pd.DataFrame({
        "Дільниця": dill_arr,
        "Виборці": no_of_vyb_arr,
    })
    people = np.array(people).astype(float)


def generate_conn():
    global connections

    dill_arr = [i for i in range(1, int(no_of_dill) + 1)]
    df_conn = []
    df_dill = []
    conn_prev = []
    for d in range(len(dill_arr)):
        dill_conn = conn_arr[d].split(',')
        for c in dill_conn:
            if str(dill_arr[d]) + "," + str(c) not in conn_prev and \
                    str(c) + "," + str(dill_arr[d]) not in conn_prev and \
                    str(dill_arr[d]) != str(c):
                df_dill.append(dill_arr[d])
                df_conn.append(c)
                conn_prev.append(str(c) + "," + str(dill_arr[d]))

    connections = pd.DataFrame({
        "Д1": df_dill,
        "Д2": df_conn,
    })

    connections = np.array(connections).astype(float)


def connect_2(data, first, second, connects):
    table = np.array([])
    people_first = 0
    people_second = 0
    for row in data:
        if row[0] == first:
            people_first = float(row[1])
        else:
            if row[0] == second:
                people_second = float(row[1])
            else:
                table = np.append(table, row)

    new_connections = np.array([])
    index = str(first) + "_" + str(second)
    for row in connects:
        if row[0] == first and (not row[1] == second):
            new_connections = np.append(new_connections, [index, row[1]])
        elif row[0] == second and (not row[1] == first):
            new_connections = np.append(new_connections, [index, row[1]])
        elif row[1] == first and (not row[0] == second):
            new_connections = np.append(new_connections, [row[0], index])
        elif row[1] == second and (not row[0] == first):
            new_connections = np.append(new_connections, [row[0], index])
        elif (row[1] == second and row[0] == first) or (row[1] == first and row[0] == second):
            23
        else:
            new_connections = np.append(new_connections, row)

    new_connections = np.reshape(new_connections, (-1, 2))
    people_connected = people_first + people_second
    table = np.append(table, [index, people_connected])
    table = np.reshape(table, (-1, 2))
    return table, new_connections


def get_max_deviation(table, m_vector):
    avg = sum(table[:, 1].astype(float)/m_vector)/len(table[:, 1])
    dev_vec = ((table[:, 1].astype(float)/m_vector - avg)/avg)*100
    dev_abs = abs(((table[:, 1].astype(float)/m_vector - avg)/avg)*100)
    max_dev = max(dev_abs)
    return max_dev, dev_vec



def get_mandats_vectors(mlen, mmin, mmax):
    mandats = []
    for prod in product(range(mmin, mmax), repeat=mlen):
        if sum(prod) == mandat_all:
            mandats.append(prod)

    return mandats


def get_min_max_deviation(table, m_matrix):
    min_max = 10000
    for vec in m_matrix:
        dev, dev_vec = get_max_deviation(table, vec)
        if dev < min_max:
            min_max = dev
            min_dev_vec = dev_vec
            m_vector = vec

    return m_vector, min_max, min_dev_vec


def get_best_connections(data, connects):
    min_update = 100000
    best_arr = []
    best = {}
    next_step = []

    for row in connects:
        first = row[0]
        second = row[1]
        table, new_connects = connect_2(data, first, second, connects)
        n_step = {}
        n_step['people'] = table
        n_step['connections'] = new_connects
        next_step.append(n_step)
        m_matrix = get_mandats_vectors(len(table), mandat_min, mandat_max+1)
        m_vec, dev, min_dev_vec = get_min_max_deviation(table, m_matrix)
        b_p = [int(float(p)) for p in table[:, 1]]
        dev_okr = [round(d_o, 2) for d_o in 100*(np.array(b_p)-sum(b_p)/len(b_p))/(sum(b_p)/len(b_p))]
        max_dev_okr = max([abs(d) for d in dev_okr])
        update = dev**2

        if update < min_update:
            min_update = update
            best["dil"] = [d.replace('.0', '') for d in table[:, 0]]
            best["people"] = [int(float(p)) for p in table[:, 1]]
            best["mandats"] = m_vec
            best["deviations"] = [round(d, 2) for d in min_dev_vec]
            best["deviations_okrug"] = [round(d_o, 2) for d_o in 100*(np.array(best["people"])-sum(best["people"])/len(best["people"]))/(sum(best["people"])/len(best["people"]))]
            best["deviations_people"] = np.array(best["people"])/np.array(best["mandats"]) - sum(np.array(best["people"])/np.array(best["mandats"]))/len(best["people"])
            best["deviations_people"] = [round(d_p) for d_p in best["deviations_people"]]
            best["deviations_okrug_people"] = np.array(best["people"]) - sum(best['people'])/len(best["people"])
            best["deviations_okrug_people"] = [round(d_o) for d_o in best["deviations_okrug_people"]]
            best["connections"] = new_connects
            best_arr.append(min_update)

    for step in next_step:
        if len(step['people']) > okrug_min:
            step_min_update, step_best, _ = get_best_connections(step['people'], step['connections'])
            if step_min_update < min_update:
                min_update = step_min_update
                best = step_best
                best_arr.append(min_update)
    return min_update, best, best_arr


def get_opt(data):
    unpack_data(data)
    generate_df()

    min_dev, best, best_arr = get_best_connections(people, connections)
    return min_dev, best, best_arr