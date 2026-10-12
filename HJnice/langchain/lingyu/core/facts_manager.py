##关键事实

_facts_store : dict[str,dict[str,str]] = {}

class FactsManager:
    def __init__(self,chat_session_id):
        self.chat_session_id = chat_session_id
        if not _facts_store.get(chat_session_id):
            _facts_store[chat_session_id] = {}

    ##获取全部事实
    def get_all_facts(self) ->dict[str,str]:
        return _facts_store.get(self.chat_session_id,{})

    def get_one_fact(self,key) -> str:
        """获取单个事实"""
        return self.get_all_facts().get(key,"")

    def update_fact(self,facts : dict[str,str]) -> None:
        """更新事实
        Args: facts 需要更新的字典"""
        self.get_all_facts().update({k:v for k,v in facts.items() if v})


    def set_one_fact(self,key : str ,val : str) -> None:
        """添加单个事实
        Args:"""
        self.get_all_facts()[key] = val

    def clear_facts(self) -> None:
        _facts_store[self.chat_session_id] = {}
