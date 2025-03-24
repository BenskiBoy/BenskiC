.PHONY: full_run

test:
	../tester/test_compiler /home/benth/programming/c_compiler/src/main.py --chapter 4 --stage parse

compile:
	gcc return_2.s -o return_2

run:
	python main.py ./return_2.c --debug  

echo:
	./return_2
	echo "$?"

full_run:
	python main.py ./return_2.c -s
	gcc return_2.s -o return_2
	-./return_2 
