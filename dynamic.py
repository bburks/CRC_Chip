"""
Flexible class used to avoid repeating computations. Currently only in use to
avoid computing covariance matrices multiple times. Adds a memory cost, as all
prior evaluations of Dynamic object are stored inside itself.


Will have issues if args is mutable. Unsure if possible.
"""


class Dynamic:

    def __init__(self, f):
        self.f = f
        self.saved = dict()
        def dyF(*args):
            args
            if args in self.saved:
                print('time saved!')
                return self.saved.get(args)
            else:
                res = self.f(*args)
                self.saved[args] = res
                return res
        self.dyF = dyF

    def __call__(self, *args):
        return self.dyF(*args)
