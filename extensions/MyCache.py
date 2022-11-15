from typing import *
'''
装饰器类的第一种写法：__call__ 这个魔术方法，这个方法可以使类实例化后的对象可以像函数一样被调用，然后在这里直接接受被装饰的函数，
    这种方式在使用装饰器类时，是必须带括号的，也就是装饰器类是要被实例化的。具体实现如下
'''


class Decorator:
    def __init__(self, out_str: str, out_num: int) -> None:
        '''装饰器类同样是一个类，它拥有类的特性，因此我们可以在装饰时设定一些参数，方便在装饰器中做一些特殊操作'''
        self._out_str = out_str # 实例变量前有一个单下划线的作用是隐藏这个属性，使它不被IDE进行代码提示。但强行改变是可行的。对比双下划线的好处是，这个可以被继承。
        self._out_num = out_num
        
    def __call__(self, func: Callable) -> Callable:
        '''使类实例化后的对象可以直接被当做函数调用，入参就是调用使传入的参数，利用这个可以实现装饰器类，入参就是要装饰的函数'''
        def warpper(*args: Any, **kwds: Any) -> Any:
            print(self._out_str * self._out_num)
            res = func(*args, **kwds)
            print(f"func res: {res}")
            print(self._out_str * self._out_num)
            return res
        return warpper
    

@Decorator('1', 12)  # 实际上相当于 ==> test1 = Decorator(False)(test1) 最终被执行时 ==> Decorator(False)(test1)()
def test1() -> str:
    return "hello world"

# 多层装饰，按装饰的距离被装饰函数的距离，从近到远被一次装饰执行
@Decorator('3', 24)
@Decorator('2', 18)
@Decorator('1', 12)
def test2(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    # test1()
    test2(1, 2)