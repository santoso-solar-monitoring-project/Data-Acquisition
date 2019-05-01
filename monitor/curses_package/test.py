from cursesClient import CursesClient
from multiprocessing import Process, Manager, Lock
import time

manager = Manager()
command = manager.list("")
data = manager.list([])
curses_lock = Lock()

client = CursesClient()
process = Process(target=client.run, daemon=True, args=(command,data,curses_lock))

process.start()
for i in range(10):
	data.clear()
	with curses_lock:
		data.append(str(time.time()%10))
	time.sleep(1)
process.join()
