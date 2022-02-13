from pwn import *

payload = b""

current_payload = b""

with open("shellcode.s", "r") as f:
    data = f.readlines()

data = [line.strip().split(" ") for line in data]

full_payload = []


labels_later = []

count = 0

for line in data:
    instruction = line[0]
    assembly = 0x0
    if line == [""]:
        continue

    print(line)

    if instruction == "label":


        full_payload.append(current_payload)
        full_payload.append(line[1])
        count += 2
        current_payload = b""

        for previous_call in labels_later:
            if previous_call[0] == line[1]:
                offset_glob = previous_call[1][0]
                offset_in = previous_call[1][1]
                assembly = 0
                if previous_call[1][3] == "CALL":
                    assembly |= 0x000000000000CA00
                    assembly |= 0x000000000000000f
            
                elif previous_call[1][3] == "JMP":
                    assembly |= 0x000000000000BB00
                elif previous_call[1][3] == "JEQ":
                    assembly |= 0x000000000000BB00
                    assembly |= (0xf << 4)
                    assembly |= (0xf << 0)
                elif previous_call[1][3] == "JA":
                    assembly |= 0x000000000000BB00
                    assembly |= (0xf << 4)
                elif previous_call[1][3] == "JB":
                    assembly |= 0x000000000000BB00
                    assembly |= (0xf)
                elif previous_call[1][3] == "PUSH":
                    assembly |= 0x0000000000006500
                    assembly |= (0xf)


                l = 0
    
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                
                if previous_call[1][2] is True:
                    l += 1
                assembly |= (l << 16)

                new = full_payload[offset_glob][:offset_in] + p64(assembly) + full_payload[offset_glob][offset_in + 8:]
                full_payload[offset_glob] = new
                
        continue

    if instruction == "ADD":
        assembly |= 0x00AD0000
    

        if line[1].startswith("SP"):
            op1 = 8

        else:
            op1 = line[1].split(',')[0]
            try:
                _, op1 = op1.split('R')
            except ValueError:
                print("error op1 : " + ' '.join(line))
                exit(1)


        assembly |= (int(op1) << 0)

        if line[2].startswith("SP"):
            reg_nb = 8
        else:
            op2 = line[2]
            reg_nb = int(op2[1]) # A CHANGER!!
        
        assembly |= (reg_nb << 28)
        print(hex(assembly) + ' ' + hex(reg_nb))

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))

        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
        

        elif op3.startwith("SP"):
            op3 = 8
            assembly |= (int(op3) << 8)

        else:
            print("error op3 " + ' '.join(line))
            exit(1)

        print(hex(assembly))
        current_payload += p32(assembly)

    if instruction == "JMPt":
        assembly |= 0x00BB0000
        if line[1].startswith("R"):
            assembly |= (line[1][1]<< 0)
        elif line[1].startswith("PC"):
            assembly |= (9 << 0)
        else:
            print("error op : " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)


    if instruction == "SUB":
        assembly |= 0x005B0000
        

        if line[1].startswith("SP"):
            op1 = 8

        else:
            op1 = line[1].split(',')[0]
            try:
                _, op1 = op1.split('R')
            except ValueError:
                print("error op1 : " + ' '.join(line))
                exit(1)


        assembly |= int(op1) << 0

        op2 = line[2]
        if  op2.startswith('R'):
            reg_nb = int(op2[1])
        elif op2.startswith("SP"):
            reg_nb = 8

        else:
            print("pb op2 : " + " ".join(line))     
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))
                exit(1)


        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 

        elif op3.startwith("SP"):
            op3 = 8
            assembly |= (int(op3) << 8)

        else:
            print("error op3 " + ' '.join(line))
        
        current_payload += p32(assembly)

    if instruction == "SHL":
        assembly |= 0x00370000
        
        op1 = line[1].split(',')[0]
        try:
            _, op1 = op1.split('R')
        except ValueError:
            print("error op1 : " + ' '.join(line))


        assembly |= int(op1) << 0

        op2 = line[2]
        if not op2.startswith('R'):
            print("error op2 : " + ' '.join(line))
            exit(1)
        reg_nb = int(op2[1])
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))
                exit(1)


        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
                exit(1)

        else:
            print("error op3 " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)

    if instruction == "SHR":
        assembly |= 0x00D20000
        
        op1 = line[1].split(',')[0]
        try:
            _, op1 = op1.split('R')
        except ValueError:
            print("error op1 : " + ' '.join(line))
            exit(1)


        assembly |= (int(op1) << 0)

        op2 = line[2]
        if not op2.startswith('R'):
            print("error op2 : " + ' '.join(line))
            exit(1)
        reg_nb = int(op2[1])
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))
                exit(1)


        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
                exit(1)

        else:
            print("error op3 " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)



    if instruction == "XOR":
        assembly |= 0x00100000
        
        op1 = line[1].split(',')[0]
        try:
            _, op1 = op1.split('R')
        except ValueError:
            print("error op1 : " + ' '.join(line))
            exit(1)


        assembly |= int(op1) << 0

        op2 = line[2]
        if not op2.startswith('R'):
            print("error op2 : " + ' '.join(line))
            exit(1)
        reg_nb = int(op2[1])
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))
                exit(1)

        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
        

        else:
            print("error op3 " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)
    
    if instruction == "OR":
        assembly |= 0x000B0000
        
        op1 = line[1].split(',')[0]
        try:
            _, op1 = op1.split('R')
        except ValueError:
            print("error op1 : " + ' '.join(line))
            exit(1)


        assembly |= int(op1) << 0

        op2 = line[2]
        if not op2.startswith('R'):
            print("error op2 : " + ' '.join(line))
            exit(1)
        reg_nb = int(op2[1])
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))

        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
        

        else:
            print("error op3 " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)
    
    if instruction == "AND":
        assembly |= 0x004D0000
        
        op1 = line[1].split(',')[0]
        try:
            _, op1 = op1.split('R')
        except ValueError:
            print("error op1 : " + ' '.join(line))


        assembly |= int(op1) << 0

        op2 = line[2]
        if not op2.startswith('R'):
            print("error op2 : " + ' '.join(line))
            exit(1)
        reg_nb = int(op2[1])
        assembly |= (reg_nb << 28)

        op3 = line[3]
        if op3.startswith('#'):
            assembly |= 0x0f000000
            _, imm_value = op3.split('#')
            assembly |= (int(imm_value) << 8)

            if (int(imm_value) > 0xff):
                print("imm value too big : " + ' '.join(line))

        elif op3.startswith('R'):
            _, reg_nb = op3.split('R')
            assembly |= (int(reg_nb) << 8)

            if int(reg_nb) > 7:
                print("reg nb too big : " + ' '.join(line)) 
        

        else:
            print("error op3 " + ' '.join(line))
            exit(1)
        current_payload += p32(assembly)

    if instruction == "POP":
        assembly |= 0x0000000000005600
        nb_regs = len(line) - 1
        assembly |= (nb_regs << 4)
        for i in range(nb_regs):
            if line[1 + i].startswith("SP"):
                current_reg = 8
            else:
                current_reg = int(line[1 + i][1])

            assembly |= (current_reg << (8 * (i+2)))
        current_payload += p64(assembly)


    if instruction == "JMP":
        assembly |= 0x000000000000BB00
        if line[1].startswith("#"):
        #   assembly |= 0x000000000000000f
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "JMP")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)
        current_payload += p64(assembly)




    if instruction == "RET":
        assembly |= 0x0000000000008E00
        current_payload += p64(assembly)

    if instruction == "CALL":
        assembly |= 0x000000000000CA00
        if line[1].startswith("#"):
            assembly |= 0x000000000000000f
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "CALL")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)

        else:
            imm = int(line[1].split('R')[1])
            assembly |= (imm << 16)
            
        
        current_payload += p64(assembly)


    if instruction == "PUSH":
        assembly |= 0x0000000000006500

        if line[1].startswith("#"):
            assembly |= 0x000000000000000f
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "PUSH")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)



        else:
            nb_reg = len(line) - 1
            assembly |= (nb_reg << 4)
            for i in range(nb_reg):
            
                if line[1 + i].startswith("SP"):
                    current_reg = 8
                else:
                    current_reg = int(line[1 + i][1])
                assembly |= (current_reg << (8 *(i+2)))     


        current_payload += p64(assembly)

    if instruction == "JA":
        assembly |= 0x000000000000BB00
        assembly |= (0xf << 4)
        if line[1].startswith("#"):
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "JA")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)


        current_payload += p64(assembly)

    if instruction == "JB":
        assembly |= 0x000000000000BB00
        assembly |= (0xf)
        if line[1].startswith("#"):
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    print('thumb')
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "JB")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)


        current_payload += p64(assembly)

    if instruction == "JEQ":
        assembly |= 0x000000000000BB00
        assembly |= (0xf << 4)
        assembly |= (0xf << 0)
        if line[1].startswith("#"):
            data = line[1].split("#")[1]
            if (not data.isdigit()):
                #label
                l = 0
                save = data[0] == "*"
                if data[0] == "*":
                    l += 1
                    data = data[1:]
                imm = -1
                for i in range(len(full_payload)):
                    if type(full_payload[i]) == str:
                        if full_payload[i] == data:
                            imm = l
                            break
                    elif type(full_payload[i]) == bytes:
                        l += len(full_payload[i])
                if imm == -1:
                    labels_later.append((data, (count, len(current_payload), save, "JEQ")))
                    assembly = 0xFFFFFFFFFFFFFFFF
                else:
                    assembly |= (imm << 16)
            else:
                imm = int(data)
                assembly |= (imm << 16)

        current_payload += p64(assembly)
        
    if instruction == "SYSCALL":
        assembly |= 0x0000000000009000
        
        current_payload += p64(assembly)        

    if instruction == "MOV":
        assembly |= 0x0000000000001700

        if line[1].startswith("R"):
            op1 = int(line[1][1])
        elif line[1].startswith("SP"):
            op1 = 8
        if line[2].startswith("R"):
            op2 = int(line[2][1])
        elif line[2].startswith("SP"):
            op2 = 8

        assembly |= op1
        assembly |= (op2<<4)
        
        current_payload += p64(assembly)
        
    if instruction == "CMP":
        assembly |= 0x000000000000C300

        if line[2].startswith("#"):
            assembly |= 0xf

            nb_reg = int(line[1][1])
            assembly |= (nb_reg << 4)

            imm = int(line[2].split('#')[1])
            assembly |= (imm << 16)

        elif line[2].startswith("R"):
            nb_reg = int(line[1][1])
            assembly |= (nb_reg << 4)

            imm = int(line[2].split('R')[1])
            assembly |= (imm << 16)
        current_payload += p64(assembly)
    print(hex(assembly))




full_payload.append(current_payload)

if len(full_payload) == 1:
    payload = full_payload[0]
else:
    payload = b''.join([full_payload[i] for i in range(0, len(full_payload), 2)])



print(payload)


with open("vm_data.bin", "wb") as f:
    f.write(payload)
