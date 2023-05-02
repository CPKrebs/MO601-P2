CROSS_COMPILER="riscv64-unknown-linux-gnu-"

CROSS_CFLAGS = -nostdinc -nostdlib -nostartfiles -lgcc -march=rv32ima -mabi=ilp32


TESTS = $(patsubst %.c,%,$(wildcard *.c))
		

all: $(TESTS) 


# Compile programs
$(TESTS):
	$(CROSS_COMPILER)gcc crt.S $@.c -o test/$@  $(CROSS_CFLAGS) 
	$(CROSS_COMPILER)objdump -d test/$@ > test/$@

# Clean executables and backup files
clean: 
	rm -f test/*.dumb

# Use rules
help:
	@$(ECHO) -e "\nRules:\n"
	@$(ECHO) -e "help: \tShow this help"
	@$(ECHO) -e "clean: \tRemove generated files"


.PHONY: build all
