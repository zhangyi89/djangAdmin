class Foo(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __iter__(self):
        yield self.name
        for i in range(1, self.age+1):
            print(i)
        yield "结束"


obj_list = [Foo("lucy", 18), Foo("jack", 19)]


for obj in obj_list:
    for item in obj:
        print(item)
