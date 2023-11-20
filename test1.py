class A:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def pint_info(self):
        """
        WTF?
        :return:
        """
        pass

class B(A):
    def __init__(self, id: int, name: str, val: float):
        A.__init__(self, id, name)
        self.val = val


b = B(1, "Grisha", 1.0)


b.pint_info()
# print(f'{b.id=} {b.name=} {b.val=}')


