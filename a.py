A = None

from b import B

class A:

    def SaySelf():
        print(123)

    def SayOther():
        B.SaySelf()