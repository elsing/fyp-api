
from pebble import concurrent


@concurrent.process(timeout=2)
def mymethod():
    for i in range(1000000):
        print(i)


test = mymethod()

try:
    result = test.result()
except TimeoutError:
    print("Timeout")
except Exception as e:
    print("Error: {}".format(e))
