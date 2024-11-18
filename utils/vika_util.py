import requests
from flask import current_app as app
class VikaClient:
    def __init__(self):
        self.api_token = app.config['VIKA_API_TOKEN']
        self.space_id = app.config['VIKA_SPACE_ID']

    # 创建数据表
    def create_datasheet(self, name, description="", folder_id=None, pre_node_id=None, fields=None):
        url = f"https://vika.cn/fusion/v1/spaces/{self.space_id}/datasheets"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "name": name,
            "description": description,
            "folderId": folder_id,
            "preNodeId": pre_node_id,
            "fields": fields if fields else []
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
    def insert_records(self, datasheet_id, records):
        """
        向指定的数据表中插入记录
        
        Args:
            datasheet_id (str): 数据表ID
            records (list): 要插入的记录列表，每个记录是一个包含 fields 的字典
                例如：[
                    {
                        "fields": {
                            "姓名": "张三",
                            "年龄": 25,
                            "日期": "2024-01-01"
                        }
                    }
                ]
        
        Returns:
            dict: API 响应结果
        """
        url = f"https://vika.cn/fusion/v1/datasheets/{datasheet_id}/records"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "records": records
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
    def delete_records(self, datasheet_id, record_ids):
        """
        删除指定数据表中的记录
        
        Args:
            datasheet_id (str): 数据表ID
            record_ids (list): 要删除的记录ID列表
                例如：["recADeOmeoJHg", "recfCpveDCZYO"]
        
        Returns:
            dict: API 响应结果
        
        Raises:
            requests.exceptions.HTTPError: 当API请求失败时抛出异常
        """
        # 将记录ID列表转换为逗号分隔的字符串
        record_ids_str = ','.join(record_ids)
        url = f"https://vika.cn/fusion/v1/datasheets/{datasheet_id}/records"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # 添加记录ID作为查询参数
        params = {
            "recordIds": record_ids_str
        }
        
        response = requests.delete(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
    def get_records(self, datasheet_id, **kwargs):
        """
        获取数据表中的记录
        
        Args:
            datasheet_id (str): 数据表ID
            **kwargs: 可选的查询参数
                - viewId (str): 视图ID
                - fields (list): 需要返回的字段列表，例如 ["姓名", "年龄"]
                - filterByFormula (str): 筛选公式，例如 'OR(find("真空", {主要卖点}) > 0)'
                - maxRecords (int): 返回记录的最大数量
                - pageSize (int): 每页记录数量，默认 100
                - pageNum (int): 页码，默认 1
                - sort (list): 排序规则，例如 [{"field": "年龄", "order": "desc"}]
        
        Returns:
            dict: API 响应结果，包含查询到的记录数据（已过滤掉空记录）
        
        Raises:
            requests.exceptions.HTTPError: 当API请求失败时抛出异常
        """
        url = f"https://vika.cn/fusion/v1/datasheets/{datasheet_id}/records"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # 构建查询参数
        params = {}
        
        # 添加视图ID
        if 'viewId' in kwargs:
            params['viewId'] = kwargs['viewId']
            
        # 添加字段列表
        if 'fields' in kwargs:
            params['fields'] = kwargs['fields']
            
        # 添加筛选公式
        if 'filterByFormula' in kwargs:
            params['filterByFormula'] = kwargs['filterByFormula']
            
        # 添加最大记录数
        if 'maxRecords' in kwargs:
            params['maxRecords'] = kwargs['maxRecords']
            
        # 添加分页参数
        if 'pageSize' in kwargs:
            params['pageSize'] = kwargs['pageSize']
        if 'pageNum' in kwargs:
            params['pageNum'] = kwargs['pageNum']
            
        # 添加排序规则
        if 'sort' in kwargs:
            params['sort'] = kwargs['sort']
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            # 过滤掉空记录
            if result['success'] and 'records' in result['data']:
                result['data']['records'] = [
                    record for record in result['data']['records'] 
                    if record['fields']  # 只保留fields不为空的记录
                ]
                # 更新总记录数
                result['data']['total'] = len(result['data']['records'])
            return result
        else:
            response.raise_for_status()
            
