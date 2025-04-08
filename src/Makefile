.PHONY: full_run

test:
	../tester/test_compiler /home/benth/programming/c_compiler/src/main.py --chapter 6 

compile:
	gcc return_2.s -o return_2

run:
	python main.py ./return_2.c --debug  

echo:
	./return_2
	echo "$?"

full_run:
	python main.py ./return_2.c -s --debug
	gcc return_2.s -o return_2
	./return_2 
