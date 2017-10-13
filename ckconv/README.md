convergence test before running first principle calculations

workflow:

script for 收敛性测试; 包含ecut, kpoint(, 以及lat) 是用你要计算的结构测试，尽量用小的，固定截断能量值，对不同的k点计算，看能量值的收敛情况。再固定k点，选不同的截断能量值计算，再看能量值的熟练情况。这样是为了确定你所计算的体系用什么样的参数（k点和截断能量值）能使结果最可靠。

Finally use equation of state to find the most stable lattice constant
