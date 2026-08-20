#!/usr/bin/python3

from functools import wraps

def x():
  print("goodbye")

def y():
  print("hello")
      
def my_decorator(func):
  @wraps(func)
  def z(abc):
    abc=func(abc)
    if(abc=='zzz'):
      x()
    else:
      y()
  return z

#my_decorator takes a function+its argument-names and
#create a new function with same name and argument-names
#argument-names and values are avilable to decorator as well as new function
#wraps gives __name__ of func to returned function (z())

@my_decorator
def greet(abc):
   print(abc)
   return abc

print(greet.__name__)
greet(abc='zzz')
greet(abc='zz')
