test:
	tester/test_compiler /home/benth/programming/c_compiler/main.py --chapter 1

run:
	python main.py ./return_2.c --debug  

echo:
	./return_2
	shell echo "$?"