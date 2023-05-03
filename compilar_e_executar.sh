cd test/
make clean
make
cd ..
python3 Riscv_casio.py

rm -R assemble/

cd test/
rm -f *.riscv