test:
	tester/test_compiler /home/benth/programming/c_compiler/main.py --chapter 2 --stage parse

compile:
	gcc return_2.s -o return_2

run:
	python main.py ./return_2.c --debug  

echo:
	./return_2
	echo "$?"