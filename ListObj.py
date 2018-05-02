class ListObj:
    def __init__(self):
        self.location = None
        self.interest = None
        self.once = False
        pass


def create_button(type,title,payload=None,url=None, ratio="compact"):
    try:
        button_dic = {}
        button_dic["type"]=type
        button_dic["title"]=title
        button_dic["payload"]=payload
        button_dic["url"] = url
        button_dic["webview_height_ratio"] = ratio
        return button_dic
    except Exception as e:
        pass