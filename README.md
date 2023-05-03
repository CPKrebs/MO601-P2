# MO601-P2

Doutorando: Casio Pacheco Krebs

RA: 264953

O objetivo deste projeto é implementar um simulador de processador baseado no conjunto de instruções (ISA) RISC-V RV32IM, onde que RV32I significa a versão de 32 bits das instruções básicas, e M a extensão para as instruções de multiplicação e divisão. O objetivo do simulador é realizar o Debug dos kernels, permitindo visualizar as instruções simuladas, combinado com os valores dos registradores associados 

# Pré-Requisitos

É necessário ter configurado o compilador gcc-riscv64-linux-gnu. Caso seja necessário sua instalação, pode ser realizado com os comandos abaixo:

```
sudo apt-get update -y
sudo apt-get install -y gcc-riscv64-linux-gnu
```



# Clonar repositório

Para clonar o repositório, utilize o comando abaixo:

```
git clone https://github.com/CPKrebs/MO601-P2.git
```

# Preparação das aplicações de entradas

Antes de realizar a execução do simulador desenvolvido, é necessário realizar a cópia das novas aplicações de simulação (arquivos .c) dentro da pasta "test/".


Após a cópia das aplicações, é necessário realizar o comando ```make```, a partir do arquivo Makefile que se encontra de dentro da pasta "test/". 

```
make
```

Esse comando ira gerar uma pasta, denominada de "assemble/", na raiz do projeto, onde será povoada com os arquivos gerados pelo Objdump.


# Inicialização do simulador


Para realizar a ativação do simulador, deve ser utilizado o comando abaixo:

```
python3 Riscv_casio.py 
```

A saída será armazenada na pasta "test". Para cada aplicação simulada, será gerado um arquivo log com o nome correspondente da aplicação seguido pelo padão ".log".

# Execução automática

O fluxo de compilação, de simulação e de limpezas de arquivos temporários, podem ser realizadas de forma automática, para isso, as aplicações que serão simuladas devem estar na pasta "test/". O comando se encontra abaixo:

```
compilar_e_executar.sh
```
