"""
数据加载
"""
import json

def dataload(file_address):
    with open(file_address,'r',encoding='utf-8') as file:
        data = json.load(file)
    return data
    
    
    
