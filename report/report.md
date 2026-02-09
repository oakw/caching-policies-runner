# Caching Policies Report

Last updated at: Mon Feb  9 09:11:38 PM EET 2026

| Policy | Model | Cache Size | Args | Hits | Misses | Accesses | Hit Object Size Sum | Hit Response Time Sum | User Time | Elapsed Time | Max RSS | Exit Code |
|--------|-------|------------|---------------------|------|--------|----------|---------------------|----------------------|-----------|--------------|---------|-----------|
| lfu | docker-registry-processed | 100000.0 | {} | 50552.0 | 49448.0 | 100000.0 | 364813262.0 | 41067.1 | 0.905 | 0.95 | 27858.0 | 0 |
| lfu | wiki-t-10 | 100000.0 | {} | 608.0 | 99392.0 | 100000.0 | 13842190.0 | 5.9 | 0.76 | 0.8500000000000001 | 38058.0 | 0 |
| lfu | docker-registry-processed | 1000000.0 | {} | 69918.0 | 30082.0 | 100000.0 | 2601795840.0 | 76493.6 | 1.51 | 1.55 | 27892.0 | 0 |
| lfu | wiki-t-10 | 1000000.0 | {} | 4134.0 | 95866.0 | 100000.0 | 137973586.0 | 21.8 | 1.22 | 1.3050000000000002 | 37736.0 | 0 |
| lfu | docker-registry-processed | 10000000.0 | {} | 78114.0 | 21886.0 | 100000.0 | 4481898184.0 | 93143.7 | 2.22 | 2.27 | 27836.0 | 0 |
| lfu | wiki-t-10 | 10000000.0 | {} | 8454.0 | 91546.0 | 100000.0 | 294063054.0 | 49.2 | 5.11 | 5.23 | 37680.0 | 0 |
| lfu | docker-registry-processed | 100000000.0 | {} | 80468.0 | 19532.0 | 100000.0 | 7691526288.0 | 100252.5 | 1.11 | 1.15 | 28052.0 | 0 |
| lfu | wiki-t-10 | 100000000.0 | {} | 16701.0 | 83299.0 | 100000.0 | 593475604.0 | 107.7 | 68.72 | 69.1 | 37972.0 | 0 |
| lfu-aging | docker-registry-processed | 100000.0 | {"tau": 1000.0} | 49383.0 | 50617.0 | 100000.0 | 366983738.0 | 37285.3 | 324.89 | 325.8 | 27080.0 | 0 |
| lfu-aging | wiki-t-10 | 100000.0 | {"tau": 1000.0} | 613.0 | 99387.0 | 100000.0 | 13876170.0 | 6.2 | 1.71 | 1.82 | 37920.0 | 0 |
| lfu-aging | docker-registry-processed | 1000000.0 | {"tau": 1000.0} | 67925.0 | 32075.0 | 100000.0 | 2661888623.0 | 71525.3 | 250.63 | 251.38 | 27316.0 | 0 |
| lfu-aging | wiki-t-10 | 1000000.0 | {"tau": 1000.0} | 4153.0 | 95847.0 | 100000.0 | 138060917.0 | 21.2 | 13.94 | 14.09 | 37688.0 | 0 |
| lfu-aging | docker-registry-processed | 10000000.0 | {"tau": 1000.0} | 77332.0 | 22668.0 | 100000.0 | 4472154342.0 | 91650.0 | 370.34 | 371.52 | 27048.0 | 0 |
| lfu-aging | wiki-t-10 | 10000000.0 | {"tau": 1000.0} | 8608.0 | 91392.0 | 100000.0 | 297025412.0 | 54.9 | 45.2 | 45.47 | 37276.0 | 0 |
| lfu-aging | docker-registry-processed | 100000000.0 | {"tau": 1000.0} | 80176.0 | 19824.0 | 100000.0 | 7745925387.0 | 99690.5 | 127.07 | 127.59 | 27776.0 | 0 |
| lfu-aging | wiki-t-10 | 100000000.0 | {"tau": 1000.0} | 17541.0 | 82459.0 | 100000.0 | 608639549.0 | 138.8 | 298.24 | 299.36 | 37656.0 | 0 |
| lfu-byte | docker-registry-processed | 100000.0 | {"size_utility": "freq_times_size"} | 36266.0 | 63734.0 | 100000.0 | 371368898.0 | 24682.6 | 0.94 | 0.97 | 28196.0 | 0 |
| lfu-byte | docker-registry-processed | 100000.0 | {"size_utility": "freq_over_size"} | 59078.0 | 40922.0 | 100000.0 | 314266171.0 | 58488.8 | 11.01 | 11.11 | 27704.0 | 0 |
| lfu-byte | wiki-t-10 | 100000.0 | {"size_utility": "freq_over_size"} | 667.0 | 99333.0 | 100000.0 | 13165822.0 | 8.0 | 0.82 | 0.92 | 37832.0 | 0 |
| lfu-byte | wiki-t-10 | 100000.0 | {"size_utility": "freq_times_size"} | 522.0 | 99478.0 | 100000.0 | 13143068.0 | 4.9 | 0.77 | 0.84 | 38392.0 | 0 |
| lfu-byte | docker-registry-processed | 1000000.0 | {"size_utility": "freq_over_size"} | 75662.0 | 24338.0 | 100000.0 | 2535823982.0 | 86754.2 | 33.15 | 33.36 | 27592.0 | 0 |
| lfu-byte | docker-registry-processed | 1000000.0 | {"size_utility": "freq_times_size"} | 53072.0 | 46928.0 | 100000.0 | 2663909613.0 | 51175.0 | 1.26 | 1.3 | 27792.0 | 0 |
| lfu-byte | wiki-t-10 | 1000000.0 | {"size_utility": "freq_over_size"} | 4761.0 | 95239.0 | 100000.0 | 125853352.0 | 30.2 | 2.36 | 2.46 | 38052.0 | 0 |
| lfu-byte | wiki-t-10 | 1000000.0 | {"size_utility": "freq_times_size"} | 2778.0 | 97222.0 | 100000.0 | 119184196.0 | 13.9 | 1.13 | 1.22 | 38100.0 | 0 |
| lfu-byte | docker-registry-processed | 10000000.0 | {"size_utility": "freq_times_size"} | 63651.0 | 36349.0 | 100000.0 | 4395518253.0 | 69996.8 | 1.32 | 1.37 | 28244.0 | 0 |
| lfu-byte | docker-registry-processed | 10000000.0 | {"size_utility": "freq_over_size"} | 81713.0 | 18287.0 | 100000.0 | 4481569882.0 | 99652.1 | 118.71 | 119.16 | 27516.0 | 0 |
| lfu-byte | wiki-t-10 | 10000000.0 | {"size_utility": "freq_times_size"} | 3823.0 | 96177.0 | 100000.0 | 184477362.0 | 22.8 | 2.04 | 2.13 | 38180.0 | 0 |
| lfu-byte | wiki-t-10 | 10000000.0 | {"size_utility": "freq_over_size"} | 9721.0 | 90279.0 | 100000.0 | 230965113.0 | 70.8 | 27.06 | 27.25 | 37296.0 | 0 |
| lfu-byte | docker-registry-processed | 100000000.0 | {"size_utility": "freq_times_size"} | 59433.0 | 40567.0 | 100000.0 | 7006375292.0 | 64941.0 | 0.65 | 0.68 | 28064.0 | 0 |
| lfu-byte | docker-registry-processed | 100000000.0 | {"size_utility": "freq_over_size"} | 85666.0 | 14334.0 | 100000.0 | 7354882647.0 | 107569.1 | 547.13 | 548.86 | 28052.0 | 0 |
| lfu-byte | wiki-t-10 | 100000000.0 | {"size_utility": "freq_times_size"} | 8621.0 | 91379.0 | 100000.0 | 449328060.0 | 67.7 | 28.84 | 29.07 | 37048.0 | 0 |
| lfu-byte | wiki-t-10 | 100000000.0 | {"size_utility": "freq_over_size"} | 17887.0 | 82113.0 | 100000.0 | 431079483.0 | 156.4 | 416.17 | 417.54 | 39152.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 100000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 50587.0 | 49413.0 | 100000.0 | 365103138.0 | 41087.3 | 2.935 | 2.98 | 28052.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 100000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 50621.0 | 49379.0 | 100000.0 | 365374157.0 | 41126.8 | 2.77 | 2.8 | 28352.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 100000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 609.0 | 99391.0 | 100000.0 | 13864969.0 | 5.9 | 3.0949999999999998 | 3.21 | 38256.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 100000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 608.0 | 99392.0 | 100000.0 | 13842190.0 | 5.9 | 3.29 | 3.39 | 37920.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 1000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 69909.0 | 30091.0 | 100000.0 | 2602144161.0 | 76474.2 | 3.375 | 3.415 | 28118.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 1000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 69907.0 | 30093.0 | 100000.0 | 2601270787.0 | 76470.3 | 3.17 | 3.2 | 28476.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 1000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 4130.0 | 95870.0 | 100000.0 | 137803005.0 | 21.8 | 3.58 | 3.6799999999999997 | 38178.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 1000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 4125.0 | 95875.0 | 100000.0 | 137492036.0 | 21.8 | 3.74 | 3.83 | 37852.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 10000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 78104.0 | 21896.0 | 100000.0 | 4481730002.0 | 93130.0 | 4.07 | 4.11 | 27884.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 10000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 78076.0 | 21924.0 | 100000.0 | 4480810751.0 | 93101.5 | 4.21 | 4.24 | 27892.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 10000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 8445.0 | 91555.0 | 100000.0 | 293634131.0 | 49.2 | 7.72 | 7.82 | 37724.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 10000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 8423.0 | 91577.0 | 100000.0 | 292626981.0 | 49.4 | 7.72 | 7.84 | 37880.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 100000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 80434.0 | 19566.0 | 100000.0 | 7691375980.0 | 100210.4 | 2.86 | 2.92 | 27980.0 | 0 |
| lfu-doorkeeper | docker-registry-processed | 100000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 80396.0 | 19604.0 | 100000.0 | 7690051052.0 | 100171.9 | 3.01 | 3.06 | 27908.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 100000000.0 | {"admission_threshold": 3, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 16625.0 | 83375.0 | 100000.0 | 590149221.0 | 107.9 | 68.78 | 69.06 | 37884.0 | 0 |
| lfu-doorkeeper | wiki-t-10 | 100000000.0 | {"admission_threshold": 2, "cms_delta": 1e-06, "cms_epsilon": 0.001} | 16659.0 | 83341.0 | 100000.0 | 591448568.0 | 107.3 | 77.38 | 77.74 | 37828.0 | 0 |
| lfu-latency-byte | docker-registry-processed | 10000000.0 | {"default_latency": 1.0, "latency_utility": "freq_times_latency_over_size"} | 81321.0 | 18679.0 | 100000.0 | 4458168866.0 | 99938.4 | 130.4 | 130.78 | 28280.0 | 0 |
| lfu-latency-byte | docker-registry-processed | 10000000.0 | {"default_latency": 1.0, "latency_utility": "freq_over_size_times_latency"} | 81520.0 | 18480.0 | 100000.0 | 4457069613.0 | 99014.0 | 161.35 | 161.85 | 28140.0 | 0 |
| lfu-latency-byte | wiki-t-10 | 10000000.0 | {"default_latency": 1.0, "latency_utility": "freq_over_size_times_latency"} | 9671.0 | 90329.0 | 100000.0 | 231753128.0 | 38.9 | 34.81 | 35.0 | 43076.0 | 0 |
| lfu-latency-byte | wiki-t-10 | 10000000.0 | {"default_latency": 1.0, "latency_utility": "freq_times_latency_over_size"} | 1131.0 | 98869.0 | 100000.0 | 24494272.0 | 81.2 | 48.29 | 48.53 | 43220.0 | 0 |
| lfu-sliding | docker-registry-processed | 100000.0 | {"window_size": 25} | 43726.0 | 56274.0 | 100000.0 | 348014771.0 | 31504.5 | 1.83 | 1.85 | 27936.0 | 0 |
| lfu-sliding | wiki-t-10 | 100000.0 | {"window_size": 25} | 684.0 | 99316.0 | 100000.0 | 15094102.0 | 8.6 | 0.93 | 1.02 | 38444.0 | 0 |
| lfu-sliding | docker-registry-processed | 1000000.0 | {"window_size": 25} | 60074.0 | 39926.0 | 100000.0 | 2505944574.0 | 59948.0 | 4.58 | 4.62 | 28252.0 | 0 |
| lfu-sliding | wiki-t-10 | 1000000.0 | {"window_size": 25} | 4384.0 | 95616.0 | 100000.0 | 140273321.0 | 27.1 | 2.25 | 2.33 | 38412.0 | 0 |
| lfu-sliding | docker-registry-processed | 10000000.0 | {"window_size": 25} | 69734.0 | 30266.0 | 100000.0 | 4148592018.0 | 78839.4 | 7.9 | 7.95 | 27340.0 | 0 |
| lfu-sliding | wiki-t-10 | 10000000.0 | {"window_size": 25} | 7876.0 | 92124.0 | 100000.0 | 250903026.0 | 56.1 | 11.76 | 11.92 | 37448.0 | 0 |
| lfu-sliding | docker-registry-processed | 100000000.0 | {"window_size": 30} | 68307.0 | 31693.0 | 100000.0 | 7192965180.0 | 78899.7 | 3.57 | 3.62 | 27924.0 | 0 |
| lfu-sliding | wiki-t-10 | 100000000.0 | {"window_size": 30} | 14348.0 | 85652.0 | 100000.0 | 458913342.0 | 177.0 | 130.95 | 131.49 | 37472.0 | 0 |
| lru | docker-registry-processed | 100000.0 | {} | 40669.0 | 59331.0 | 100000.0 | 311155733.0 | 29666.5 | 1.45 | 1.48 | 24172.0 | 0 |
| lru | wiki-t-10 | 100000.0 | {} | 259.0 | 99741.0 | 100000.0 | 5655363.0 | 7.5 | 0.84 | 0.92 | 31088.0 | 0 |
| lru | docker-registry-processed | 1000000.0 | {} | 57711.0 | 42289.0 | 100000.0 | 2401660929.0 | 57273.7 | 2.09 | 2.13 | 24004.0 | 0 |
| lru | wiki-t-10 | 1000000.0 | {} | 1452.0 | 98548.0 | 100000.0 | 38877500.0 | 36.6 | 1.39 | 1.48 | 30704.0 | 0 |
| lru | docker-registry-processed | 10000000.0 | {} | 67343.0 | 32657.0 | 100000.0 | 3997322457.0 | 75254.1 | 2.24 | 2.27 | 24144.0 | 0 |
| lru | wiki-t-10 | 10000000.0 | {} | 6992.0 | 93008.0 | 100000.0 | 201378743.0 | 125.1 | 6.53 | 6.63 | 30344.0 | 0 |
| lru | docker-registry-processed | 100000000.0 | {} | 66042.0 | 33958.0 | 100000.0 | 6789122982.0 | 75556.2 | 0.84 | 0.97 | 24540.0 | 0 |
| lru | wiki-t-10 | 100000000.0 | {} | 14687.0 | 85313.0 | 100000.0 | 463697807.0 | 183.2 | 74.34 | 74.66 | 30600.0 | 0 |
| tiny-lfu-byte | docker-registry-processed | 1000000.0 | {"tiny_window_size": 100000} | 78075.0 | 21925.0 | 100000.0 | 2462757528.0 | 90411.8 | 8.47 | 8.58 | 29932.0 | 0 |
| tiny-lfu-byte | wiki-t-10 | 1000000.0 | {"tiny_window_size": 100000} | 4529.0 | 95471.0 | 100000.0 | 121745566.0 | 16.8 | 2.63 | 2.73 | 47688.0 | 0 |
| tiny-lfu-byte | docker-registry-processed | 10000000.0 | {"tiny_window_size": 100000} | 85289.0 | 14711.0 | 100000.0 | 4100926720.0 | 104374.4 | 68.99 | 69.2 | 30384.0 | 0 |
| tiny-lfu-byte | wiki-t-10 | 10000000.0 | {"tiny_window_size": 100000} | 9291.0 | 90709.0 | 100000.0 | 222838460.0 | 57.4 | 25.69 | 25.88 | 47408.0 | 0 |
| two-segment | docker-registry-processed | 100000.0 | {"protected_fraction": 0.5} | 48373.0 | 51627.0 | 100000.0 | 297925238.0 | 38532.0 | 1.48 | 1.51 | 24136.0 | 0 |
| two-segment | wiki-t-10 | 100000.0 | {"protected_fraction": 0.5} | 226.0 | 99774.0 | 100000.0 | 4834653.0 | 4.9 | 0.79 | 0.88 | 30660.0 | 0 |
| two-segment | docker-registry-processed | 1000000.0 | {"protected_fraction": 0.5} | 62676.0 | 37324.0 | 100000.0 | 2499006252.0 | 63756.6 | 1.73 | 1.76 | 23848.0 | 0 |
| two-segment | wiki-t-10 | 1000000.0 | {"protected_fraction": 0.5} | 1520.0 | 98480.0 | 100000.0 | 37862292.0 | 29.3 | 1.32 | 1.41 | 30560.0 | 0 |
| two-segment | docker-registry-processed | 10000000.0 | {"protected_fraction": 0.5} | 70410.0 | 29590.0 | 100000.0 | 4113378786.0 | 80420.6 | 2.09 | 2.11 | 23784.0 | 0 |
| two-segment | docker-registry-processed | 10000000.0 | {"protected_fraction": 0.8} | 70410.0 | 29590.0 | 100000.0 | 4113693975.0 | 80422.5 | 2.08 | 2.12 | 24156.0 | 0 |
| two-segment | wiki-t-10 | 10000000.0 | {"protected_fraction": 0.5} | 7992.0 | 92008.0 | 100000.0 | 252213546.0 | 126.7 | 5.32 | 5.4 | 30668.0 | 0 |
| two-segment | wiki-t-10 | 10000000.0 | {"protected_fraction": 0.8} | 7274.0 | 92726.0 | 100000.0 | 236166065.0 | 114.0 | 4.71 | 4.8 | 30616.0 | 0 |
| two-segment | docker-registry-processed | 100000000.0 | {"protected_fraction": 0.5} | 73495.0 | 26505.0 | 100000.0 | 7325571608.0 | 86534.6 | 0.8 | 0.82 | 24328.0 | 0 |
| two-segment | docker-registry-processed | 100000000.0 | {"protected_fraction": 0.8} | 73500.0 | 26500.0 | 100000.0 | 7325620835.0 | 86533.7 | 0.8 | 0.83 | 24224.0 | 0 |
| two-segment | wiki-t-10 | 100000000.0 | {"protected_fraction": 0.5} | 16462.0 | 83538.0 | 100000.0 | 529077646.0 | 193.1 | 67.65 | 67.91 | 31316.0 | 0 |
| two-segment | wiki-t-10 | 100000000.0 | {"protected_fraction": 0.8} | 16462.0 | 83538.0 | 100000.0 | 529077646.0 | 193.1 | 66.54 | 66.83 | 31292.0 | 0 |

*Values marked with an asterisk (\*) indicate variance across 1 runs.*
