import os
import time

RG_id = [	"zero","ra","sp","gp","tp",
			"t0","t1","t2",
			"s0","s1",
			"a0","a1","a2","a3","a4","a5","a6","a7",
			"s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11",
			"t3","t4","t5","t6"]

#########################################################
#
#
#					Funções auxiliares
#
#
#########################################################
def print_log (w, PC, inst_hex, rd, Val_rd, rs1, Val_rs1, rs2, Val_rs2, inst, assemble):

	if (Val_rd < 0):	Val_rd = bin(Val_rd + (1<<32))
	else:				Val_rd = bin(Val_rd)

	if (Val_rs1 < 0):	Val_rs1 = bin(Val_rs1 + (1<<32))
	else:				Val_rs1 = bin(Val_rs1)

	if (Val_rs2 < 0):	Val_rs2 = bin(Val_rs2 + (1<<32))
	else:				Val_rs2 = bin(Val_rs2)

	Val_rd = int("".join(str(x) for x in Val_rd), 2)
	Val_rs1 = int("".join(str(x) for x in Val_rs1), 2)
	Val_rs2 = int("".join(str(x) for x in Val_rs2), 2)

	linha = ['PC={:08X} [{}] x{:02d}={:08X} x{:02d}={:08X} x{:02d}={:08X} {}{}\n'.format( \
		PC, inst_hex, rd,Val_rd, rs1,Val_rs1, rs2,Val_rs2, inst, assemble)]

	w.writelines(linha)

#########################################################
#
#
#					riscv
#
#
#########################################################
def riscv(codigos):

	# Inicializa o arquivo de log
	w = open("test/"+ codigos+ '.log', 'w', newline='', encoding='utf-8')

	# Abre o arquivo assemble
	f = open("assemble/"+ codigos)

	# Inicializando o banco de registradores e a memória
	RG = 32*[0]
	Mem = {}

	# Inicializando o contador de programa
	PC = 0

	####################
	#
	#	Carregando as instruções na memória
	#
	####################
	Clock = 0	
	for line in f:
		if (Clock>5):

			line = line.split();

			# Salvando o endereço da primeira instrução
			if ("<_start>:" in line): 
				PC = int(line[0], base=16) - 4

			if len(line)> 2:

				# Identificando o endereço da instrução
				dec = int(line[0][0:-1], base=16)

				# Identificando as instruções 
				Mem[dec] = line[1]
				
		Clock+=1

	####################
	#
	#	Execução
	#
	####################		
	while(True):

		####################
		#
		#	Fetch
		#
		####################	

		PC += 4		

		####################
		#
		#	Decode
		#
		####################

		inst_hex = Mem[PC]									# Lê a string de HEX
		inst_bin = bin(int(inst_hex, 16))					# Converte para binário
		inst_bin = [int(d) for d in str(inst_bin)[2::]]		# Converte em um array
		inst_bin = (32-len(inst_bin))*[0] + inst_bin 		# Completa o array ate 32 bits (caso os bists mais significativos sejam 0)
		

		# Identificando os campos
		opcode = inst_bin[25::]

		rd = inst_bin[20:25]
		rd = int("".join(str(x) for x in rd), 2)

		func3 = inst_bin[17:20]

		rs1 = inst_bin[12:17]
		rs1 = int("".join(str(x) for x in rs1), 2)

		rs2 = inst_bin[7:12]
		rs2 = int("".join(str(x) for x in rs2), 2)

		func7 = inst_bin[0:7]

		# Armazenando os valores dos registradores de origem antes da instrução
		Val_rs1 = RG[rs1]
		Val_rs2 = RG[rs2]

		####################
		#
		#	Execution
		#
		####################

		# imm[31:12] rd 0110111 LUI
		# x[rd] = sext(immediate[31:12] << 12)
		if (opcode == [0,1,1,0,1,1,1]):

			imd_bin = inst_bin[0:20] + 12*[0]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<32)

			if (rd!=0):	RG[rd] = imd

			print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
				'lui     ', '{},{:d}'.format(RG_id[rd], imd))


		# imm[31:12] rd 0100111 AUIPC
		# x[rd] = pc + sext(immediate[31:12] << 12)
		elif (opcode == [0,0,1,0,1,1,1]):

			imd_bin = inst_bin[0:20] + 12*[0]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<32)

			if (rd!=0):	RG[rd] = PC + imd

			print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
				'auipc   ', '{},{:d}'.format(RG_id[rd], imd))


		#imm[20|10:1|11|19:12] rd 1101111 JAL
		elif (opcode == [1,1,0,1,1,1,1]):

			imd_bin = [inst_bin[0]] + inst_bin[12:20] + [inst_bin[11]] + inst_bin[1:11] + [0]

			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<21)

			if (rd!=0):	RG[rd] = PC + 4

			print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
				'jal     ', '{},{:d}'.format(RG_id[rd], imd))

			PC = PC + imd - 4


		#imm[11:0] rs1 000 rd 1100111 JALR
		elif (opcode == [1,1,0,0,1,1,1]):

			imd_bin = inst_bin[0:12]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<12)

			if (rd!=0):	RG[rd] = RG[rs1] + imd

			print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
				'jalr    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1],imd))

			PC = RG[rs1] + imd - 4


		#imm[12|10:5] rs2 rs1 XXX imm[4:1|11] 1100011 	
		elif (opcode == [1,1,0,0,0,1,1]):

			imd_bin = [inst_bin[0], inst_bin[24]] + inst_bin[1:7] + inst_bin[20:24] + [0]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<13)


			#imm[12|10:5] rs2 rs1 000 imm[4:1|11] 1100011 BEQ	
			if (func3 == [0,0,0]):

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'beq     ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))
				
				if (RG[rs1] == RG[rs2]): PC = PC + imd - 4


			#imm[12|10:5] rs2 rs1 001 imm[4:1|11] 1100011 BNE	
			elif (func3 == [0,0,1]):

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'bne     ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))

				if (RG[rs1] != RG[rs2]): PC = PC + imd - 4


			#imm[12|10:5] rs2 rs1 100 imm[4:1|11] 1100011 BLT	
			elif (func3 == [1,0,0]):

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'blt     ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))
				
				if (RG[rs1] < RG[rs2]):	PC = PC + imd - 4

				
			#imm[12|10:5] rs2 rs1 101 imm[4:1|11] 1100011 BGE	
			elif (func3 == [1,0,1]):

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'bge     ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))
				
				if (RG[rs1] >= RG[rs2]):	PC = PC + imd - 4

			
			#imm[12|10:5] rs2 rs1 110 imm[4:1|11] 1100011 BLTU	
			elif (func3 == [1,1,0]):
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'bltu    ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))

				aux_rs1 = RG[rs1]
				if (aux_rs1 < 0): 	aux_rs1 += (1<<32)

				aux_rs2 = RG[rs2]
				if (aux_rs2 < 0): 	aux_rs2 += (1<<32)

				if (aux_rs1 < aux_rs2):	PC = PC + imd - 4


			#imm[12|10:5] rs2 rs1 111 imm[4:1|11] 1100011 BGEU	
			elif (func3 == [1,1,1]):

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'bgeu    ', '{},{},{}'.format(RG_id[rs1], RG_id[rs2],imd))

				aux_rs1 = RG[rs1]
				if (aux_rs1 < 0): 	aux_rs1 += (1<<32)

				aux_rs2 = RG[rs2]
				if (aux_rs2 < 0): 	aux_rs2 += (1<<32)

				if (aux_rs1 >= aux_rs2):	PC = PC + imd - 4
					

		#imm[11:0] rs1 XXX rd 0000011 
		elif (opcode == [0,0,0,0,0,1,1]):

			imd_bin = inst_bin[0:12]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<12)

			if ((RG[rs1] + imd + 0) not in Mem): Mem[RG[rs1] + imd] =     8*[0]
			if ((RG[rs1] + imd + 1) not in Mem): Mem[RG[rs1] + imd + 1] = 8*[0]
			if ((RG[rs1] + imd + 2) not in Mem): Mem[RG[rs1] + imd + 2] = 8*[0]
			if ((RG[rs1] + imd + 3) not in Mem): Mem[RG[rs1] + imd + 3] = 8*[0]

			#imm[11:0] rs1 000 rd 0000011 LB
			if (func3 == [0,0,0]):
				if (rd!=0):	

					DATA = 24*[Mem[RG[rs1] + imd][0]] + Mem[RG[rs1] + imd]

					RG[rd] = int("".join(str(x) for x in DATA), 2)

					if (DATA[0] == 1): RG[rd] -= (1<<32)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'lb      ','{},{}({})'.format(RG_id[rd], imd, RG_id[rs1]))


			#imm[11:0] rs1 001 rd 0000011 LH
			elif (func3 == [0,0,1]):
				if (rd!=0):	

					DATA = 16*[Mem[RG[rs1] + imd][0]] + Mem[RG[rs1] + imd] + Mem[RG[rs1] + imd + 1]

					RG[rd] = int("".join(str(x) for x in DATA), 2)

					if (DATA[0] == 1): RG[rd] -= (1<<32)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'lh      ','{},{}({})'.format(RG_id[rd], imd, RG_id[rs1]))


			#imm[11:0] rs1 010 rd 0000011 LW
			elif (func3 == [0,1,0]):
				if (rd!=0):	

					DATA = Mem[RG[rs1] + imd] + Mem[RG[rs1] + imd + 1] + Mem[RG[rs1] + imd + 2] + Mem[RG[rs1] + imd + 3]

					RG[rd] = int("".join(str(x) for x in DATA), 2)

					if (DATA[0] == 1): RG[rd] -= (1<<32)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'lw      ','{},{}({})'.format(RG_id[rd], imd, RG_id[rs1]))


			#imm[11:0] rs1 100 rd 0000011 LBU
			elif (func3 == [1,0,0]):
				if (rd!=0):	

					DATA = 24*[0] + Mem[RG[rs1] + imd]

					RG[rd] = int("".join(str(x) for x in DATA), 2)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'lbu     ','{},{}({})'.format(RG_id[rd], imd, RG_id[rs1]))


			#imm[11:0] rs1 101 rd 0000011 LHU
			elif (func3 == [1,0,1]):
				if (rd!=0):	

					DATA = 16*[0] + Mem[RG[rs1] + imd] + Mem[RG[rs1] + imd + 1]

					RG[rd] = int("".join(str(x) for x in DATA), 2)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'lhu     ','{},{}({})'.format(RG_id[rd], imd, RG_id[rs1]))


		#imm[11:5] rs2 rs1 XXX imm[4:0] 0100011 
		elif (opcode == [0,1,0,0,0,1,1]):

			imd_bin = inst_bin[0:7] + inst_bin[20:25]
			imd = int("".join(str(x) for x in imd_bin), 2)
			if (inst_bin[0] == 1): imd -= (1<<12)

			#imm[11:5] rs2 rs1 000 imm[4:0] 0100011 SB
			if (func3 == [0,0,0]):

				if (RG[rs2] < 0):	DATA = bin((RG[rs2] + (1<<8)) % (2**8))
				else:				DATA = bin(RG[rs2] % (2**8))

				DATA = [int(d) for d in str(DATA)[2::]]		
				DATA = (8-len(DATA))*[0] + DATA 

				Mem[RG[rs1] + imd] = DATA[0:8]

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'sb      ', '{},{}({})'.format(RG_id[rs2], imd, RG_id[rs1]))


			#imm[11:5] rs2 rs1 001 imm[4:0] 0100011 SH
			elif (func3 == [0,0,1]):

				if (RG[rs2] < 0):	DATA = bin((RG[rs2] + (1<<16)) % (2**16))
				else:				DATA = bin(RG[rs2] % (2**16))

				DATA = [int(d) for d in str(DATA)[2::]]		
				DATA = (16-len(DATA))*[0] + DATA 	
				
				Mem[RG[rs1] + imd]     = DATA[0:8]
				Mem[RG[rs1] + imd + 1] = DATA[8:16]

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'sh      ', '{},{}({})'.format(RG_id[rs2], imd, RG_id[rs1]))


			#imm[11:5] rs2 rs1 010 imm[4:0] 0100011 SW
			elif (func3 == [0,1,0]):

				if (RG[rs2] < 0):	DATA = bin((RG[rs2] + (1<<32)) % (2**32))
				else:				DATA = bin(RG[rs2] % (2**32))

				DATA = [int(d) for d in str(DATA)[2::]]		
				DATA = (32-len(DATA))*[0] + DATA 		

				Mem[RG[rs1] + imd] 	   = DATA[0:8]
				Mem[RG[rs1] + imd + 1] = DATA[8:16]
				Mem[RG[rs1] + imd + 2] = DATA[16:24]
				Mem[RG[rs1] + imd + 3] = DATA[24:32]

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'sw      ', '{},{}({})'.format(RG_id[rs2], imd, RG_id[rs1]))


		#imm[11:0] rs1 XXX rd 0010011 
		elif (opcode == [0,0,1,0,0,1,1]):

			# ADDI SLTI SLTIU XORI OR ANDI
			imd_bin_e = 20*[inst_bin[0]] + inst_bin[0:12]
			imd_gates = int("".join(str(x) for x in imd_bin_e), 2)
			if (inst_bin[0] == 1): imd_gates -= (1<<32)

			# SRLI SLLI SRAI
			shamt = inst_bin[7:12]
			shamt = int("".join(str(x) for x in shamt), 2)


			#imm[11:0] rs1 000 rd 0010011 ADDI
			if (func3 == [0,0,0]):
				if (rd!=0):	RG[rd] = (RG[rs1] + imd_gates)%(1<<32)
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'addi    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))


			#imm[11:0] rs1 010 rd 0010011 SLTI
			elif (func3 == [0,1,0]):
				if (rd!=0):	
					if (RG[rs1] < imd_gates):	RG[rd] = 1;
					else:	 					RG[rd] = 0;

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'slti    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))


			#imm[11:0] rs1 011 rd 0010011 SLTIU
			elif (func3 == [0,1,1]):
				if (rd!=0):	
					if (inst_bin[0] == 1): imd_gates += (1<<32)

					aux_rs1 = RG[rs1]
					if (aux_rs1 < 0): 	aux_rs1 += (1<<32)

					if (aux_rs1 < imd_gates):	RG[rd] = 1;
					else:	 					RG[rd] = 0;
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'sltiu   ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))


			#imm[11:0] rs1 100 rd 0010011 XORI
			elif (func3 == [1,0,0]):
				if (rd!=0):	RG[rd] = RG[rs1] ^ imd_gates
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'xori    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))


			#imm[11:0] rs1 110 rd 0010011 ORI
			elif (func3 == [1,1,0]):
				if (rd!=0):	RG[rd] = RG[rs1] | imd_gates
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'ori     ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))


			#imm[11:0] rs1 111 rd 0010011 ANDI
			elif (func3 == [1,1,1]):
				if (rd!=0):	RG[rd] = RG[rs1] & imd_gates
					
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'andi    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], imd_gates))
	
			
			#0000000 shamt rs1 001 rd 0010011 SLLI
			elif (func3 == [0,0,1]):
				if (rd!=0):	

					# Converte para binário
					if (Val_rs1 < 0): 	aux = bin(Val_rs1+(1<<32))
					else :				aux = bin(Val_rs1)

					rs1_bin = [int(d) for d in str(aux)[2::]]		# Converte em um array
					rs1_bin = (32-len(rs1_bin))*[0] + rs1_bin 

					# Realiza o shift
					for x in range(shamt):
						for y in range(31):	
							rs1_bin[y] = rs1_bin[y+1]
						rs1_bin[31] = 0

					RG[rd] = int("".join(str(x) for x in rs1_bin), 2)		

				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'slli    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], shamt))


			#0X00000 shamt rs1 101 rd 0010011	
			elif (func3 == [1,0,1]):

				#0000000 shamt rs1 101 rd 0010011 SRLI
				if (func7 == [0,0,0,0,0,0,0]):
					if (rd!=0):	

						# Converte para binário
						if (Val_rs1 < 0): 	aux = bin(Val_rs1+(1<<32))
						else :				aux = bin(Val_rs1)

						rs1_bin = [int(d) for d in str(aux)[2::]]		# Converte em um array
						rs1_bin = (32-len(rs1_bin))*[0] + rs1_bin 

						# Realiza o shift
						for x in range(shamt):
							for y in range(31):	
								rs1_bin[31-y] = rs1_bin[30-y]
							rs1_bin[0] = 0

						RG[rd] = int("".join(str(x) for x in rs1_bin), 2)		
						
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'srli    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], shamt))


				#0100000 shamt rs1 101 rd 0010011 SRAI
				elif (func7 == [0,1,0,0,0,0,0]):
					if (rd!=0):	RG[rd] = RG[rs1] >> shamt

					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'srai    ', '{},{},{:d}'.format(RG_id[rd], RG_id[rs1], shamt))

	
		#0X0000X rs2 rs1 XXX rd 0110011		
		elif (opcode == [0,1,1,0,0,1,1]):		

			if (func7 == [0,0,0,0,0,0,0]):

				#0000000 rs2 rs1 000 rd 0110011 ADD
				if (func3 == [0,0,0]):
					if (rd!=0):	RG[rd] = (RG[rs1] + RG[rs2])%(1<<32)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'add     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 001 rd 0110011 SLL
				elif (func3 == [0,0,1]):
					if (rd!=0):	

						# Converte para binário
						if (Val_rs1 < 0): 	aux = bin(Val_rs1+(1<<32))
						else :				aux = bin(Val_rs1)

						rs1_bin = [int(d) for d in str(aux)[2::]]		# Converte em um array
						rs1_bin = (32-len(rs1_bin))*[0] + rs1_bin 

						# Realiza o shift
						for x in range(RG[rs2]):
							for y in range(31):	
								rs1_bin[y] = rs1_bin[y+1]
							rs1_bin[31] = 0

						RG[rd] = int("".join(str(x) for x in rs1_bin), 2)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'sll     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 010 rd 0110011 SLT
				elif (func3 == [0,1,0]):
					if (rd!=0):
						if (RG[rs1] < RG[rs2]):	RG[rd] = 1;
						else:	 				RG[rd] = 0;
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'slt     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))

		
				#0000000 rs2 rs1 101 rd 0110011 SRL
				elif (func3 == [1,0,1]):
					if (rd!=0):	

						# Converte para binário
						if (Val_rs1 < 0): 	aux = bin(Val_rs1+(1<<32))
						else :				aux = bin(Val_rs1)

						rs1_bin = [int(d) for d in str(aux)[2::]]		# Converte em um array
						rs1_bin = (32-len(rs1_bin))*[0] + rs1_bin 

						# Realiza o shift
						for x in range(RG[rs2]):
							for y in range(31):	
								rs1_bin[31-y] = rs1_bin[30-y]
							rs1_bin[0] = 0

						RG[rd] = int("".join(str(x) for x in rs1_bin), 2)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'srl     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 011 rd 0110011 SLTU
				elif (func3 == [0,1,1]):
					if (rd!=0):

						aux_rs1 = RG[rs1]
						if (aux_rs1 < 0): aux_rs1 += (1<<32)

						aux_rs2 = RG[rs2]
						if (aux_rs2 < 0): aux_rs2 += (1<<32)

						if (aux_rs1 < aux_rs2):	RG[rd] = 1;
						else:	 				RG[rd] = 0;
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'sltu    ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 100 rd 0110011 XOR
				elif (func3 == [1,0,0]):
					if (rd!=0):	RG[rd] = RG[rs1] ^ RG[rs2]
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'xor     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 110 rd 0110011 OR
				elif (func3 == [1,1,0]):
					if (rd!=0):	RG[rd] = RG[rs1] | RG[rs2]
				
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'or      ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000000 rs2 rs1 111 rd 0110011 AND
				elif (func3 == [1,1,1]):
					if (rd!=0):	RG[rd] = RG[rs1] & RG[rs2]
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'and     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))

			

			elif (func7 == [0,1,0,0,0,0,0]):

				#0100000 rs2 rs1 000 rd 0110011 SUB
				if (func3 == [0,0,0]):
					if (rd!=0):	RG[rd] = (RG[rs1] - RG[rs2])%(1<<32)

					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'sub     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0100000 rs2 rs1 101 rd 0110011 SRA
				elif (func3 == [1,0,1]):
					if (rd!=0):	RG[rd] = RG[rs1] >> RG[rs2]
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'sra     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


			elif (func7 == [0,0,0,0,0,0,1]):

				#0000001 rs2 rs1 000 rd 0110011 MUL
				if (func3 == [0,0,0]):
					if (rd!=0):	RG[rd] = (RG[rs1] * RG[rs2])%(1<<32)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'mul     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 001 rd 0110011 MULH
				elif (func3 == [0,0,1]):
					if (rd!=0):
						RG[rd] = (RG[rs1] * RG[rs2])
						RG[rd] = (RG[rd] >> 32)%(1<<32)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'mulh    ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 010 rd 0110011 MULHSU
				elif (func3 == [0,1,0]):
					if (rd!=0):

						aux_rs2 = RG[rs2]
						if (aux_rs2 < 0): aux_rs2 += (1<<32)

						RG[rd] = (RG[rs1] * aux_rs2)
						RG[rd] = (RG[rd] >> 32)%(1<<32)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'mulhsu  ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 011 rd 0110011 MULHU
				elif (func3 == [0,1,1]):
					if (rd!=0):

						aux_rs1 = RG[rs1]
						if (aux_rs1 < 0): aux_rs1 += (1<<32)

						aux_rs2 = RG[rs2]
						if (aux_rs2 < 0): aux_rs2 += (1<<32)

						RG[rd] = (aux_rs1 * aux_rs2)
						RG[rd] = (RG[rd] >> 32)%(1<<32)
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'mulhu   ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 100 rd 0110011 DIV
				elif (func3 == [1,0,0]):
					if (rd!=0):	

						RG[rd] = RG[rs1] // RG[rs2]

						if (RG[rd] < 0 and RG[rd] < Val_rs1 / Val_rs2): RG[rd] +=1

					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'div     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 101 rd 0110011 DIVU
				elif (func3 == [1,0,1]):
					if (rd!=0):	

						aux_rs1 = RG[rs1]
						if (aux_rs1 < 0): aux_rs1 += (1<<32)

						aux_rs2 = RG[rs2]
						if (aux_rs2 < 0): aux_rs2 += (1<<32)

						RG[rd] = (aux_rs1 // aux_rs2) 

						if (RG[rd] < 0 and RG[rd] < aux_rs1 / aux_rs2): RG[rd] +=1
					
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'divu    ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 110 rd 0110011 REM
				elif (func3 == [1,1,0]):
					if (rd!=0):	
						div_int = RG[rs1] // RG[rs2]

						if (div_int < 0 and div_int < Val_rs1 / Val_rs2): div_int +=1

						RG[rd] = RG[rs1] - (RG[rs2]*div_int)%(1<<32)

					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'rem     ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))


				#0000001 rs2 rs1 111 rd 0110011 REMU
				elif (func3 == [1,1,1]):
					if (rd!=0):	

						aux_rs1 = RG[rs1]
						if (aux_rs1 < 0): aux_rs1 += (1<<32)

						aux_rs2 = RG[rs2]
						if (aux_rs2 < 0): aux_rs2 += (1<<32)

						div_int = aux_rs1 // aux_rs2 

						if (div_int < 0 and div_int < aux_rs1 / aux_rs2): div_int +=1

						RG[rd] = aux_rs1 - (aux_rs2*div_int)%(1<<32)

					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'remu    ', '{},{},{}'.format(RG_id[rd], RG_id[rs1], RG_id[rs2]))



		#0000 XXXX XXXX 00000 000 00000 0001111 			
		elif (opcode == [0,0,0,1,1,1,1]):	

			#0000 pred succ 00000 000 00000 0001111 FENCE
			if (func3 == [0,0,0]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'fence   ', '()')


			#0000 0000 0000 00000 001 00000 0001111 FENCE.I
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'fence.i  ', '')

							

		#00000000000X 00000 XXX 00000 1110011 		
		elif (opcode == [1,1,1,0,0,1,1]):	

			if (func3 == [0,0,0]):

				#000000000000 00000 000 00000 1110011 ECALL
				if (rs2 == 0):
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'ecall   ', '')


				#000000000001 00000 000 00000 1110011 EBREAK
				elif (rs2 == 1):
					print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
						'ebreak  ', '')
					break

				
			#atomic csr rs1 001 rd 1110011 CSRRW		
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrw   ', '')


			#atomic csr rs1 010 rd 1110011 CSRRS
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrs   ', '')


			#atomic csr rs1 011 rd 1110011 CSRRC
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrc   ', '')


			#atomic csr zimm 101 rd 1110011 CSRRWI
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrwi  ', '')


			#atomic csr zimm 110 rd 1110011 CSRRSI
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrsi  ', '')


			#atomic csr zimm 111 rd 1110011 CSRRCI
			elif (func3 == [0,0,1]):
				print_log (w, PC, inst_hex, rd, RG[rd], rs1, Val_rs1, rs2, Val_rs2, \
					'csrrci  ', '')

#########################################################
#
#
#					MAIN
#
#
#########################################################
def main():

	# Identificando todos os códigos
	kernel = [] 
	dir_atual = os.listdir()
	for pastas in dir_atual:
		if (pastas == "assemble"):
			codigos = os.listdir(pastas)
			for x in codigos:
				kernel.append(x)

	kernel  = sorted(kernel)

	for codigos in kernel:
		t1 = time.time()
		riscv(codigos)
		print(codigos,time.time() - t1)

if __name__ == "__main__":
    main()