#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para cálculo de recomendaciones
'''
from datastore import *

total_recommendations = 30

def get_recommendations(values):
    request_queue = Queue.Queue()
    values = filter(None, values)
    threads = []
    recommendations = []

    if len(values) > 0:
        rec_per_group = total_recommendations/len(values)

    for i in range(len(values)):
        threads.append( Thread(target = data_handler.retrieve_recommendations,
                              args = [values[i], rec_per_group, request_queue]) )
        threads[i].start()

    for thread in threads:
        thread.join()

    while not request_queue.empty():
        local_recommendations = request_queue.get()
        recommendations = list(set().union(recommendations, local_recommendations))

    recommendations = list(set(recommendations) - set(values))
    return recommendations
