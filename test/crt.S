.text
.globl _start
.equ memory_size, 0x20000000

_start:
  lui sp,0x500
  jal main
  lui t0, 0x20000
  #jalr t0, 0x0
  ebreak

.bss
.align 8
.skip 4096
kstacktop:

.section .tbss
tls_start:
