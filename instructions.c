#include "syscall.h"

extern uint64_t vm_size;
extern REG pc;
extern REG flags;

// INSTRUCTIONS MODE 32 BITS

void add_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] + imm;
	return;
}

void add_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] + regs[Rm];
	return;
}

void sub_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] - imm;
	return;
}

void sub_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] - regs[Rm];
	return;
}

void xor_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] ^ imm;
	return;
}

void xor_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] ^ regs[Rm];
	return;
}

void and_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] & imm;
	return;
}

void and_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] & regs[Rm];
	return;
}

void or_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] | imm;
	return;
}

void or_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] | regs[Rm];
	return;
}

void shl_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] << imm;
	return;
}

void shl_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] << regs[Rm];
	return;
}

void shr_imm(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t imm){
	regs[Rd] = regs[Rn] >> imm;
	return;
}

void shr_reg(REG* regs, uint8_t Rd, uint8_t Rn, uint8_t Rm){
	regs[Rd] = regs[Rn] >> regs[Rm];
	return;
}

// INSTRUCTION MODE 64 BITS

void push_imm(REG* regs, uint8_t* vm_data, uint64_t imm){
	uint64_t sp = regs[SP];
	if(sp > (vm_size + STACK_SIZE)){ exit(0); };


	memcpy((void *)(vm_data + sp), &imm, 8);
	regs[SP] += 8;
	return;
}

void push_regs(REG* regs, uint8_t* vm_data, uint64_t imm, uint8_t nb_regs){
	uint8_t current_reg_nb;
	
	uint64_t sp ;

	if(nb_regs > 6){ exit(0); };

	while (nb_regs > 0){
		sp = regs[SP];

		if(sp > (vm_size + STACK_SIZE)){ exit(0); };
		current_reg_nb = imm & 0xff;
		if(current_reg_nb > 8){ exit(0); };
		
		imm >>= 8;

		memcpy((void *)(vm_data + sp), &regs[current_reg_nb], 8);
		regs[SP] += 8;
		nb_regs--;
		
	}
	return;
}

void pop(REG* regs, uint8_t* vm_data, uint64_t imm, uint8_t nb_regs){
	uint8_t current_reg_nb;
	uint64_t value;
	

	if(nb_regs > 6){ exit(0); };

	while (nb_regs > 0){
		if(regs[SP] >= (vm_size + STACK_SIZE));
	
		current_reg_nb = imm & 0xff;
		if(current_reg_nb > 8){ exit(0); };
		
		imm >>= 8;
		regs[SP] -= 8;
		memcpy(&value,(void *)vm_data + regs[SP], 8);
		regs[current_reg_nb] = value;
		nb_regs--;
		
	}
	return;
}



void ret(REG* regs, uint8_t* vm_data){
	
	opcode64 value;

	if(regs[SP] >= (vm_size + STACK_SIZE)){ exit(0); };
	
	regs[SP] -= 8;
	
	memcpy(&value, (void *)vm_data + regs[SP], 8);
	
	if (value & 1){
		value &= ~1;
		flags |= FLAG_THUMB;
	} else {
		flags &= ~FLAG_THUMB;
	}

	pc = value;
		
	return;
}


void jmp(uint64_t imm){

	if(imm > vm_size + STACK_SIZE){ exit(0); };
	if (imm & 1){
		imm &= ~1;
		flags |= FLAG_THUMB;
	} else {
		flags &= ~FLAG_THUMB;
	}

	pc = imm;
	return;
}

void ja(uint64_t imm){
	if(imm > vm_size + STACK_SIZE){ exit(0); };
	if (flags & FLAG_ABOVE){
		if (imm & 1){
			imm &= ~1;
			flags |= FLAG_THUMB;
		} else {
			flags &= ~FLAG_THUMB;
		}
		pc = imm;
	}
	return;
}

void jb(uint64_t imm){
	if(imm > vm_size - 8){ exit(0); };
	if (flags & FLAG_BELOW){
		if (imm & 1){
			imm &= ~1;
			flags |= FLAG_THUMB;
		} else {
			flags &= ~FLAG_THUMB;
		}
		pc = imm;
	}
	return;
}

void jeq(uint64_t imm){
	if(imm > vm_size - 8){ exit(0); };
	if (!(flags & FLAG_BELOW) && !(flags & FLAG_ABOVE)){
		if (imm & 1){
			imm &= ~1;
			flags |= FLAG_THUMB;
		} else {
			flags &= ~FLAG_THUMB;
		}
		pc = imm;
	}
	return;
}

void call_imm(REG* regs, uint8_t* vm_data, uint64_t imm){
	
	uint64_t sp = regs[SP];

	if(imm > vm_size){ exit(0); };
	
	if(sp > (vm_size + STACK_SIZE)){ exit(0); };
	
	memcpy((void *)(vm_data + sp), &pc, sizeof(pc));
	regs[SP] += 8;

	if (imm & 1){
		imm &= ~1;
		flags |= FLAG_THUMB;
	} else {
		flags &= ~FLAG_THUMB;
	}
	pc = imm;
	return;
}

void call_reg(REG* regs, uint8_t* vm_data, uint64_t imm){
	
	if(imm > 7){ exit(0); };
	
	uint64_t sp = regs[SP];

	if(sp >= (vm_size + STACK_SIZE)){ exit(0); };

	
	memcpy((void *)(vm_data + sp), &pc, sizeof(pc));
	regs[SP] += 8;
	
	if (regs[imm] & 1){
		flags |= FLAG_THUMB;
		pc = regs[imm] & ~1;
	} else {
		flags &= ~FLAG_THUMB;
		pc = regs[imm];
	}


	return;
}



void cmp_imm(REG* regs, uint8_t reg_nb, uint64_t imm){
	
	if(reg_nb > 8){ exit(0); };

	uint64_t op1 = regs[reg_nb];
	uint64_t op2 = imm;

	if (op1 == 0){
		flags |= FLAG_ZERO;
	} else {
		flags &= ~FLAG_ZERO;
	}

	if (op1 < op2){
		flags |= FLAG_BELOW;
		flags &= ~FLAG_ABOVE;
	} else if (op1 > op2){
		flags &= ~FLAG_BELOW;
		flags |= FLAG_ABOVE;
	} else {
		flags &= ~FLAG_ABOVE;
		flags &= ~FLAG_BELOW;
	}

	return;
}

void cmp_reg(REG* regs, uint8_t reg_nb, uint64_t imm){
	
	if(reg_nb > 8){ exit(0); };
	if(imm > 8){ exit(0); };

	uint64_t op1 = regs[reg_nb];
	uint64_t op2 = regs[imm];

	if (op1 == 0){
		flags |= FLAG_ZERO;
	} else {
		flags &= ~FLAG_ZERO;
	}

	if (op1 < op2){
		flags |= FLAG_BELOW;
		flags &= ~FLAG_ABOVE;
	} else if (op1 > op2){
		flags &= ~FLAG_BELOW;
		flags |= FLAG_ABOVE;
	} else {
		flags &= ~FLAG_ABOVE;
		flags &= ~FLAG_BELOW;
	}

	return;
}

void sys_call(REG* regs, uint8_t* vm_data){
	
	uint64_t syscall_nb = regs[R7];
	uint64_t arg1 = regs[R6];


	switch(syscall_nb){
		case SYS_PUTS:
			if(arg1 > vm_size + STACK_SIZE){ exit(0); };
			puts((char *)vm_data + arg1);
			break;
		case SYS_GETCHAR:
			regs[R7] = getchar();
			break;
        case SYS_SECRET_VAL:
            regs[R7] = 0x76769c90b4b3e9bc;
            break;
		case SYS_EXIT:
			exit(0);
		default:
			return;
	
	}

	return;
}

void mov(REG* regs, uint8_t op1, uint8_t op2){

	if(op1 > 8){ exit(0); };
	if(op2 > 8){ exit(0); };

	regs[op1] = regs[op2];
	return;
}


