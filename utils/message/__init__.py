import importlib
from django.conf import settings


def send_message(email, name, subject, body):
    """
    短息、邮件、微信
    :param to: 接收者邮箱
    :param name: 接受者姓名
    :param subject: 主题
    :param body: 内容
    :return:
    """
    for cls_path in settings.MESSAGE_CLASSES:
        # cls_path 是字符串
        module_path, class_name = cls_path.rsplit(".", 1)
        m = importlib.import_module(module_path)
        obj = getattr(m, class_name)("z2369717781@126.com", "ZY", "zhangyi1229")
        # obj = getattr(m, class_name)("m394559@126.com", "ww", "WOshiniba")
        obj.send(subject, body, email, name)
