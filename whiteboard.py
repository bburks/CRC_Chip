import csv
#import crc_models as cm



# Program to define the use of super()
# function in multiple inheritance
class Person:
    def __init__(self, age):
        self.age = age

    def show_person_class(self):
        print('running from Person')

    def get_age(self):
        self.show_person_class()
        return self.age

    def how_old_are_you(self):
        self.show_person_class()
        return self.get_age()


# class GFG2 inherits the GFG1
class Child(Person):
    def __init__(self, age):
        super().__init__(age)

    def show_child_class(self):
        print('running from Child')

    def get_age(self):
        self.show_child_class()
        return self.age



# main function
if __name__ == '__main__':

	# created the object gfg
    kid = Child(10)

	# calling the function sub_GFG3() from class GHG3
	# which inherits both GFG1 and GFG2 classes
    print(kid.get_age())
    print(kid.how_old_are_you())
