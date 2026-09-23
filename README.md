# etolegko

```
pip install requests
python speedtest.py <...>
```
```
python speedtest.py https://speedtest.selectel.ru/100MB
INFO: [ 1/10] GET https://speedtest.selectel.ru/100MB (прогрев, не учитывается)
INFO:         100.00 MiB за 7.949 с (105.52 Mbps)
INFO: [ 2/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.692 с (311.65 Mbps)
INFO: [ 3/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.660 с (315.40 Mbps)
INFO: [ 4/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.699 с (310.85 Mbps)
INFO: [ 5/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.701 с (310.56 Mbps)
INFO: [ 6/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.654 с (316.08 Mbps)
INFO: [ 7/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 3.752 с (223.58 Mbps)
INFO: [ 8/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.946 с (284.73 Mbps)
INFO: [ 9/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.486 с (337.37 Mbps)
INFO: [10/10] GET https://speedtest.selectel.ru/100MB
INFO:         100.00 MiB за 2.688 с (312.10 Mbps)
INFO: 
INFO: ====================================================================
INFO: URL:              https://speedtest.selectel.ru/100MB
INFO: Среднее время:    2.809 с
INFO: Средняя скорость: 298.67 Mbps
INFO: ====================================================================
```

```
python speedtest.py https://google.com
INFO: [ 1/10] GET https://google.com (прогрев, не учитывается)
INFO:         215.42 KiB за 5.690 с (0.31 Mbps)
ERROR: Ресурс слишком мал (215.42 KiB). Для осмысленного замера нужен ресурс от 10.00 MiB и выше.
```
