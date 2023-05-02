# MO601-P1

Doutorando: Casio Pacheco Krebs

RA: 264953

O objetivo deste projeto é implementar um simulador de circuitos lógicos, que permita gerar o histórico dos valores dos sinais de entrada e de saída para cada porta lógica. Onde serão projetados dois fluxos de simulação, o primeiro considerando que o tempo de propagação da resposta a partir da variação de alguns dos sinais de entrada seja de 0 ciclos, e outro sendo de 1 ciclo de atraso.


# Clonar repositório

Para clonar o repositório, utilize o comando abaixo:

```
git clone https://github.com/CPKrebs/MO601-P1.git
```


# Preparação dos circuitos

Antes de realizar a construção da imagem Docker, é necessário realizar a cópia dos novos testes de simulação dentro da pasta "test".


# Configuração do Docker


Construa a imagem Docker a partir do Dockerfile. Este passo usa o comando ```docker build``` para construir a imagem:

```
docker build -t casio_p1 .
```


Modificar o nome do docker, com a flag ```--name```, a partir do comando ```run```: 

```
docker run -d --name casio_p1_exec casio_p1
```



# Coleta de resultados

Para realizar as copias dos dados de saida, é utilizado o comando ```docker cp```.

```
docker cp casio_p1_exec:/test/. test/.
```