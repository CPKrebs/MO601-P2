CROSS_COMPILER=riscv64-linux-gnu-

CROSS_CFLAGS = -g -march=rv32im -std=gnu99 -mabi=ilp32 -nostartfiles -nostdinc -nostdlib 


TESTS = $(patsubst %.c,%,$(wildcard *.c))
		

all: build $(TESTS) 

build:
	mkdir -p ../assemble

# Compile programs
$(TESTS):
	$(CROSS_COMPILER)gcc -g -march=rv32im -std=gnu99 -mabi=ilp32 crt.S $@.c -o $@.riscv  $(CROSS_CFLAGS) 
	$(CROSS_COMPILER)objdump -d $@.riscv  > ../assemble/$@

# Clean executables and backup files
clean: 
	rm -f ../assemble/*
	rm -f *.riscv
	rm -f *.log

# Use rules
help:
	@$(ECHO) -e "\nRules:\n"
	@$(ECHO) -e "help: \tShow this help"
	@$(ECHO) -e "clean: \tRemove generated files"


.PHONY: build all
